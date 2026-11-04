"""VisualisationMixin : export DOT, TikZ, LaTeX et rendu Graphviz (items 40, 41).

Le texte DOT, le TikZ et le LaTeX sont produits en Python pur (aucun binaire
requis) ; seuls ``svg()``, ``png()``, ``pdf()`` et ``save()`` font appel au
programme ``dot`` de Graphviz, via le paquet Python ``graphviz``.

Hiérarchie : ``dot()`` est la source de vérité ; ``graph()``, ``svg()``,
``png()``, ``pdf()`` s'appuient dessus.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Dict, List, Tuple

_DOT_ID = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*|-?(\.[0-9]+|[0-9]+(\.[0-9]*)?))$")
_NATURAL = re.compile(r"(\d+)")

# Géométrie de placement, en « unités de ligne » : une ligne = 1, une colonne = _COL_STRETCH.
_COL_STRETCH = 140.0 / 120.0
_CLEARANCE = 0.42          # distance minimale (en unités) entre une arête et un autre état


def _curve_clearance(p0, p2, h, others) -> float:
    """
    Distance minimale entre la courbe de ``p0`` à ``p2`` (quadratique, flèche ``h``
    à gauche du sens de marche ; ``h = 0`` : segment droit) et les points ``others``.
    """
    (x0, y0), (x2, y2) = p0, p2
    dx, dy = x2 - x0, y2 - y0
    length = math.hypot(dx, dy) or 1.0
    px, py = dy / length, -dx / length
    cx, cy = (x0 + x2) / 2 + px * 2 * h, (y0 + y2) / 2 + py * 2 * h
    best = math.inf
    for i in range(2, 19):
        t = i / 20
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x2
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y2
        for ox, oy in others:
            best = min(best, math.hypot(x - ox, y - oy))
    return best


def _natural_key(text: str):
    """Tri « naturel » : ``q2 < q10``."""
    return [int(part) if part.isdigit() else part for part in _NATURAL.split(text)]


def state_label(state) -> str:
    """
    Texte lisible d'un état : ``frozenset({'0','1'})`` s'écrit ``{0,1}``,
    ``('a','b')`` s'écrit ``(a,b)``, le reste via ``str``.
    """
    if isinstance(state, (set, frozenset)):
        return "{" + ",".join(sorted((state_label(s) for s in state), key=_natural_key)) + "}"
    if isinstance(state, tuple):
        return "(" + ",".join(state_label(s) for s in state) + ")"
    return str(state)


def dot_quote(text: str) -> str:
    """Identifiant DOT : tel quel s'il est « simple », sinon entre guillemets échappés."""
    if _DOT_ID.match(text):
        return text
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def tex_escape(text: str) -> str:
    """Échappe les caractères spéciaux LaTeX ; ``ε`` devient ``\\varepsilon``."""
    if text == "ε":
        return r"$\varepsilon$"
    table = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
             "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
             "^": r"\textasciicircum{}"}
    return "".join(table.get(ch, ch) for ch in text).replace("ε", r"$\varepsilon$")


class VisualisationMixin:
    """Représentations graphiques d'un automate (DOT, TikZ, LaTeX, SVG, PNG, PDF)."""

    # ---- données communes ------------------------------------------------
    def _viz_is_gnfa(self) -> bool:
        from automata.fa.gnfa import GNFA

        return isinstance(self, GNFA)

    def _viz_label(self, state) -> str:
        """Texte d'un état ; les états spéciaux d'un GNFA (0 et 1) s'appellent start/end."""
        if self._viz_is_gnfa():
            if state == self.initial_state and not isinstance(state, str):
                return "start"
            if state == self.final_state and not isinstance(state, str):
                return "end"
        return state_label(state)

    def _viz_states(self) -> List:
        """États dans un ordre déterministe (tri naturel sur le texte affiché)."""
        return sorted(self.states, key=lambda s: _natural_key(self._viz_label(s)))

    def _viz_finals(self) -> set:
        return self._final_states_set()

    def _viz_edges(self) -> List[Tuple[object, object, str]]:
        """
        Arêtes ``(source, cible, étiquette)`` ; les symboles menant d'un même état
        à un même état sont regroupés (``a,b``) ; ε s'écrit ``ε``.
        """
        merged: Dict[Tuple, List[str]] = {}
        if self._viz_is_gnfa():
            for src, row in self.transitions.items():
                for dst, regex in row.items():
                    if regex is not None:
                        merged.setdefault((src, dst), []).append("ε" if regex == "" else regex)
        else:
            for src, row in self.transitions.items():
                for symbol, target in row.items():
                    targets = target if self._nondeterministic else {target}
                    for dst in targets:
                        merged.setdefault((src, dst), []).append("ε" if symbol == "" else symbol)
        index = {s: i for i, s in enumerate(self._viz_states())}
        edges = [(src, dst, ",".join(sorted(set(labels), key=_natural_key)))
                 for (src, dst), labels in merged.items()]
        return sorted(edges, key=lambda e: (index[e[0]], index[e[1]]))

    def _viz_layout(self) -> Dict:
        """
        Placement en colonnes : colonne = distance (BFS) depuis l'état initial,
        ligne = rang de découverte dans la colonne ; les états inaccessibles
        sont rangés dans les colonnes suivantes.

        Returns
        -------
        dict
            état -> (colonne, ligne), entiers à partir de 0.
        """
        index = {s: i for i, s in enumerate(self._viz_states())}
        adjacency: Dict = {s: [] for s in self.states}
        for src, dst, _ in self._viz_edges():
            adjacency[src].append(dst)
        depth = {self.initial_state: 0}
        order = [self.initial_state]
        head = 0
        while head < len(order):
            cur = order[head]
            head += 1
            for nxt in sorted(adjacency[cur], key=lambda s: index[s]):
                if nxt not in depth:
                    depth[nxt] = depth[cur] + 1
                    order.append(nxt)
        last = max(depth.values())
        for state in self._viz_states():
            if state not in depth:
                last += 1
                depth[state] = last
                order.append(state)
        rows: Dict[int, int] = {}
        layout = {}
        for state in order:
            col = depth[state]
            layout[state] = (col, rows.get(col, 0))
            rows[col] = rows.get(col, 0) + 1
        return layout

    def _viz_bends(self, layout: Dict, edges: List) -> Dict[Tuple, float]:
        """
        Courbure de chaque arête (hors boucles), choisie pour éviter les autres états.

        Pour chaque arête on essaie des courbures croissantes (droite d'abord, sauf
        pour un aller-retour, qui se courbe toujours) et on garde la première dont la
        courbe reste à distance ``_CLEARANCE`` de tous les autres états ; à défaut,
        la plus dégagée.

        Returns
        -------
        dict
            ``(source, cible) -> h`` : flèche de la courbe en unités de ligne,
            positive à gauche du sens de marche, ``0.0`` pour un segment droit.
        """
        pairs = {(s, d) for s, d, _ in edges}
        pos = {s: (c * _COL_STRETCH, r) for s, (c, r) in layout.items()}
        bends: Dict[Tuple, float] = {}
        for src, dst, _ in edges:
            if src == dst:
                continue
            others = [p for s, p in pos.items() if s not in (src, dst)]
            if (dst, src) in pairs:
                candidates = [0.18, 0.4, 0.7, 1.0]
            else:
                candidates = [0.0, 0.35, -0.35, 0.7, -0.7, 1.0, -1.0]
            chosen, chosen_clearance = candidates[0], -1.0
            for h in candidates:
                clearance = _curve_clearance(pos[src], pos[dst], h, others) if others else math.inf
                if clearance >= _CLEARANCE:
                    chosen = h
                    break
                if clearance > chosen_clearance:
                    chosen, chosen_clearance = h, clearance
            bends[(src, dst)] = chosen
        return bends

    # ---- DOT ---------------------------------------------------------------
    def _dot_ids(self) -> Dict:
        return {s: f"s{i}" for i, s in enumerate(self._viz_states())}

    def dot(self) -> str:
        """
        Source DOT (Graphviz) de l'automate, en texte pur.

        États nommés ``s0, s1, ...`` (tri naturel), étiquetés par leur nom ;
        états finaux en ``doublecircle`` ; une flèche invisible-ancrée
        ``__start__`` désigne l'état initial.

        Returns
        -------
        str

        Complexity
        ----------
        O(|Q| log |Q| + |E|)
        """
        ids = self._dot_ids()
        finals = self._viz_finals()
        lines = ["digraph {", "\trankdir=LR",
                 "\t__start__ [shape=point style=invis]",
                 f"\t__start__ -> {ids[self.initial_state]}"]
        for state in self._viz_states():
            shape = "doublecircle" if state in finals else "circle"
            lines.append(f"\t{ids[state]} [label={dot_quote(self._viz_label(state))} shape={shape}]")
        for src, dst, label in self._viz_edges():
            lines.append(f"\t{ids[src]} -> {ids[dst]} [label={dot_quote(label)}]")
        lines.append("}")
        return "\n".join(lines)

    # ---- TikZ / LaTeX ------------------------------------------------------
    def tikz(self, x_step: float = 3.0, y_step: float = 2.2) -> str:
        """
        Code TikZ (bibliothèque ``automata``) de l'automate.

        Placement en colonnes par distance depuis l'état initial (voir
        ``_viz_layout``). Les arêtes sont courbées si nécessaire pour ne pas
        traverser un autre état (voir ``_viz_bends``).

        Parameters
        ----------
        x_step, y_step : float
            Écarts (en cm) entre colonnes et entre lignes.

        Returns
        -------
        str
            Un environnement ``tikzpicture`` (prérequis :
            ``\\usetikzlibrary{automata}``).

        Complexity
        ----------
        O(|Q| log |Q| + |E|)
        """
        ids = self._dot_ids()
        finals = self._viz_finals()
        layout = self._viz_layout()
        edges = self._viz_edges()
        bends = self._viz_bends(layout, edges)
        lines = [r"\begin{tikzpicture}[->,>=stealth,shorten >=1pt,auto,semithick]"]
        for state in self._viz_states():
            col, row = layout[state]
            options = ["state"]
            if state == self.initial_state:
                options += ["initial", "initial text="]
            if state in finals:
                options.append("accepting")
            lines.append(
                f"  \\node[{','.join(options)}] ({ids[state]}) "
                f"at ({col * x_step:g},{-row * y_step:g}) {{{tex_escape(self._viz_label(state))}}};")
        for src, dst, label in edges:
            h = bends.get((src, dst), 0.0)
            if src == dst:
                style = "loop above"
            elif h:
                (xa, ya), (xb, yb) = layout[src], layout[dst]
                chord = math.hypot((xb - xa) * x_step, (yb - ya) * y_step) or 1.0
                angle = max(5, min(80, round(math.degrees(math.atan(4 * abs(h) * y_step / chord)))))
                style = f"bend {'left' if h > 0 else 'right'}={angle}"
            else:
                style = None
            option = f"[{style}] " if style else ""
            lines.append(f"  \\path ({ids[src]}) edge {option}node {{{tex_escape(label)}}} ({ids[dst]});")
        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    def latex(self) -> str:
        """
        Document LaTeX autonome (classe ``standalone``) contenant le TikZ de l'automate.

        Complexity
        ----------
        O(|Q| log |Q| + |E|)
        """
        return "\n".join([
            r"\documentclass[tikz,border=5pt]{standalone}",
            r"\usetikzlibrary{automata}",
            r"\begin{document}",
            self.tikz(),
            r"\end{document}",
            "",
        ])

    # ---- Graphviz ----------------------------------------------------------
    def graph(self):
        """
        Objet ``graphviz.Digraph`` de l'automate (s'affiche tel quel dans Jupyter).

        Raises
        ------
        ImportError
            Si le paquet Python ``graphviz`` n'est pas installé.
        """
        import graphviz

        digraph = graphviz.Digraph()
        digraph.body = [line + "\n" for line in self.dot().splitlines()[1:-1]]
        return digraph

    def _pipe(self, fmt: str):
        import graphviz

        try:
            return self.graph().pipe(format=fmt)
        except graphviz.ExecutableNotFound as error:
            raise RuntimeError(
                "Le programme « dot » de Graphviz est introuvable. Installez-le "
                "(Arch Linux : sudo pacman -S graphviz) puis relancez.") from error

    def svg(self) -> str:
        """Rendu SVG (texte). Nécessite le binaire ``dot``."""
        return self._pipe("svg").decode("utf-8")

    def png(self) -> bytes:
        """Rendu PNG (octets). Nécessite le binaire ``dot``."""
        return self._pipe("png")

    def pdf(self) -> bytes:
        """Rendu PDF (octets). Nécessite le binaire ``dot``."""
        return self._pipe("pdf")

    def save(self, filename) -> Path:
        """
        Écrit l'automate dans un fichier ; le format est déduit de l'extension :
        ``.dot``, ``.tex`` (document LaTeX), ``.svg``, ``.png`` ou ``.pdf``.

        Returns
        -------
        pathlib.Path

        Raises
        ------
        ValueError
            Extension non reconnue.
        """
        path = Path(filename)
        suffix = path.suffix.lower()
        if suffix == ".dot":
            path.write_text(self.dot() + "\n", encoding="utf-8")
        elif suffix == ".tex":
            path.write_text(self.latex(), encoding="utf-8")
        elif suffix == ".svg":
            path.write_text(self.svg(), encoding="utf-8")
        elif suffix == ".png":
            path.write_bytes(self.png())
        elif suffix == ".pdf":
            path.write_bytes(self.pdf())
        else:
            raise ValueError(f"extension non reconnue : {suffix!r} (dot, tex, svg, png, pdf)")
        return path

    def _repr_svg_(self):
        """Affichage automatique dans Jupyter ; silencieux si Graphviz est absent."""
        try:
            return self.svg()
        except Exception:
            return None
