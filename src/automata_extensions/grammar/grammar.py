"""Grammaires (régulières), dérivations et arbres de dérivation.

Une grammaire est un quadruplet immuable (N, T, P, S). Les symboles sont des
chaînes ; les non-terminaux et les terminaux forment deux ensembles disjoints
(la distinction ne repose donc pas sur la casse, ce qui permet d'utiliser
comme non-terminaux les noms d'états d'un automate : ``"0"``, ``"1"``...).

Seules les grammaires *régulières* (linéaires à droite ou à gauche) sont
convertibles en automate et dérivables (``derive``) ; une grammaire
quelconque peut être construite et affichée.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Optional, Tuple

_EPSILON_WORDS = ("", "ε", "ϵ", "λ", "()")


class NotDerivableError(ValueError):
    """Le mot n'est pas engendré par la grammaire."""


@dataclass(frozen=True)
class Production:
    """Règle ``lhs -> rhs`` ; ``rhs == ()`` est la règle ε."""

    lhs: str
    rhs: Tuple[str, ...] = ()

    def __str__(self) -> str:
        return f"{self.lhs} -> {''.join(self.rhs) or 'ε'}"


@dataclass(frozen=True)
class Grammar:
    """
    Grammaire (N, T, P, S) immuable.

    Raises
    ------
    ValueError
        Si N et T ne sont pas disjoints, si l'axiome n'est pas dans N, ou si
        une règle utilise un symbole inconnu ou un membre gauche hors de N.
    """

    nonterminals: FrozenSet[str]
    terminals: FrozenSet[str]
    productions: FrozenSet[Production]
    start: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "nonterminals", frozenset(self.nonterminals))
        object.__setattr__(self, "terminals", frozenset(self.terminals))
        object.__setattr__(self, "productions", frozenset(self.productions))
        if self.nonterminals & self.terminals:
            raise ValueError(
                f"symboles à la fois terminaux et non-terminaux : "
                f"{sorted(self.nonterminals & self.terminals)}")
        if self.start not in self.nonterminals:
            raise ValueError(f"axiome {self.start!r} absent des non-terminaux")
        known = self.nonterminals | self.terminals
        for p in self.productions:
            if p.lhs not in self.nonterminals:
                raise ValueError(f"membre gauche inconnu dans « {p} »")
            for s in p.rhs:
                if s not in known:
                    raise ValueError(f"symbole inconnu {s!r} dans « {p} »")

    # ---- construction ---------------------------------------------------
    @classmethod
    def from_string(cls, text: str, start: Optional[str] = None) -> "Grammar":
        """
        Lit une grammaire au format classique, une ligne par non-terminal ::

            S -> aS | b
            # commentaire
            A -> ε

        Convention : une lettre majuscule est un non-terminal, tout autre
        caractère (hors espace) est un terminal. ``ε``, ``λ``, ``()`` ou une
        alternative vide dénotent le mot vide. L'axiome est le premier
        membre gauche, sauf si ``start`` est donné.

        Complexity
        ----------
        O(taille du texte)
        """
        productions = set()
        lhs_order: List[str] = []
        used_symbols = set()
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            sep = "->" if "->" in line else "→" if "→" in line else None
            if sep is None:
                raise ValueError(f"règle sans flèche : {line!r}")
            lhs, rhs_text = (part.strip() for part in line.split(sep, 1))
            if len(lhs) != 1 or not lhs.isupper():
                raise ValueError(f"membre gauche invalide (une majuscule attendue) : {lhs!r}")
            if lhs not in lhs_order:
                lhs_order.append(lhs)
            for alt in rhs_text.split("|"):
                alt = alt.strip()
                if alt in _EPSILON_WORDS:
                    rhs: Tuple[str, ...] = ()
                else:
                    rhs = tuple(ch for ch in alt if not ch.isspace())
                    if any(ch in "εϵλ" for ch in rhs):
                        raise ValueError(f"ε mêlé à d'autres symboles : {alt!r}")
                used_symbols.update(rhs)
                productions.add(Production(lhs, rhs))
        if not lhs_order:
            raise ValueError("grammaire vide")
        nonterminals = set(lhs_order) | {s for s in used_symbols if s.isupper()}
        terminals = {s for s in used_symbols if not s.isupper()}
        return cls(nonterminals, terminals, productions, start or lhs_order[0])

    # ---- affichage ------------------------------------------------------
    def rules_for(self, nonterminal: str) -> List[Production]:
        """Règles de ``nonterminal``, triées (la règle ε en dernier)."""
        rules = [p for p in self.productions if p.lhs == nonterminal]
        return sorted(rules, key=lambda p: (p.rhs == (), p.rhs))

    def __str__(self) -> str:
        order = [self.start] + sorted(self.nonterminals - {self.start}, key=str)
        lines = []
        for nt in order:
            rules = self.rules_for(nt)
            if rules:
                lines.append(f"{nt} -> " + " | ".join(''.join(p.rhs) or 'ε' for p in rules))
        return "\n".join(lines)

    # ---- classification -------------------------------------------------
    def _linear(self, right: bool) -> bool:
        for p in self.productions:
            rhs = p.rhs if right else p.rhs[::-1]
            body = rhs[:-1] if rhs and rhs[-1] in self.nonterminals else rhs
            if any(s not in self.terminals for s in body):
                return False
        return True

    def is_right_linear(self) -> bool:
        """Toute règle est ``A -> w B`` ou ``A -> w`` (w terminal, B non-terminal)."""
        return self._linear(True)

    def is_left_linear(self) -> bool:
        """Toute règle est ``A -> B w`` ou ``A -> w``."""
        return self._linear(False)

    def is_regular(self) -> bool:
        """Linéaire à droite *ou* à gauche (pas un mélange des deux)."""
        return self.is_right_linear() or self.is_left_linear()

    # ---- transformations ------------------------------------------------
    def reverse(self) -> "Grammar":
        """
        Grammaire du langage miroir : chaque membre droit est renversé.
        Transforme une grammaire linéaire à droite en linéaire à gauche et
        réciproquement.
        """
        return Grammar(
            self.nonterminals, self.terminals,
            {Production(p.lhs, p.rhs[::-1]) for p in self.productions}, self.start)

    def to_nfa(self, nfa_cls=None):
        """
        NFA (avec ε-transitions) reconnaissant le langage de la grammaire.

        Chaque non-terminal devient un état. Une règle ``A -> a1..ak B``
        devient un chemin de k transitions de A vers B (états intermédiaires
        créés si k > 1), ``A -> a1..ak`` un chemin vers un unique état final.
        Une grammaire linéaire à gauche est traitée par renversement.

        Returns
        -------
        NFA
            ``ExtendedNFA`` par défaut.

        Raises
        ------
        ValueError
            Si la grammaire n'est pas régulière.

        Complexity
        ----------
        O(|P| * longueur maximale d'un membre droit)
        """
        if nfa_cls is None:
            from ..fa.nfa import ExtendedNFA as nfa_cls
        if self.is_right_linear():
            return self._right_linear_to_nfa(nfa_cls)
        if self.is_left_linear():
            return self.reverse()._right_linear_to_nfa(nfa_cls).reverse()
        raise ValueError("la grammaire n'est pas régulière (ni linéaire à droite ni à gauche)")

    def _right_linear_to_nfa(self, nfa_cls):
        taken = set(self.nonterminals)

        def fresh(base: str) -> str:
            name = base
            while name in taken:
                name += "_"
            taken.add(name)
            return name

        final = fresh("__final__")
        rows: Dict[str, Dict[str, set]] = {s: {} for s in self.nonterminals | {final}}

        def add(src: str, symbol: str, dst: str) -> None:
            rows[src].setdefault(symbol, set()).add(dst)

        for index, p in enumerate(sorted(self.productions, key=lambda p: (p.lhs, p.rhs))):
            if p.rhs and p.rhs[-1] in self.nonterminals:
                body, target = p.rhs[:-1], p.rhs[-1]
            else:
                body, target = p.rhs, final
            if not body:
                add(p.lhs, "", target)
                continue
            current = p.lhs
            for j, symbol in enumerate(body):
                nxt = target if j == len(body) - 1 else fresh(f"{p.lhs}_{index}_{j}")
                rows.setdefault(nxt, {})
                add(current, symbol, nxt)
                current = nxt

        return nfa_cls(
            states=frozenset(rows),
            input_symbols=self.terminals,
            transitions={s: {a: frozenset(t) for a, t in row.items()} for s, row in rows.items()},
            initial_state=self.start,
            final_states=frozenset({final}),
        )

    # ---- dérivation -----------------------------------------------------
    def generates(self, word: str) -> bool:
        """Teste si ``word`` appartient au langage (grammaires régulières seulement)."""
        try:
            self.derive(word)
            return True
        except NotDerivableError:
            return False

    def derive(self, word: str) -> "DerivationStep":
        """
        Une dérivation la plus courte de ``word``, sous forme d'une chaîne de formes
        sentencielles (renvoie la dernière étape ; ``.sequence()`` les affiche toutes).

        Parcours en largeur sur les couples (non-terminal, position dans le mot).
        Grammaires régulières uniquement.

        Raises
        ------
        NotDerivableError
            Si le mot n'est pas engendré.
        ValueError
            Si la grammaire n'est pas régulière.

        Complexity
        ----------
        O(|P| * |mot|^2) dans le pire cas.
        """
        if self.is_right_linear():
            rules = self._derive_right_linear(word)
        elif self.is_left_linear():
            reversed_rules = self.reverse()._derive_right_linear(word[::-1])
            rules = [Production(p.lhs, p.rhs[::-1]) for p in reversed_rules]
        else:
            raise ValueError("dérivation supportée uniquement pour les grammaires régulières")
        return self._chain(rules)

    def _derive_right_linear(self, word: str) -> List[Production]:
        by_lhs: Dict[str, List[Production]] = {}
        for p in sorted(self.productions, key=lambda p: (p.lhs, p.rhs)):
            by_lhs.setdefault(p.lhs, []).append(p)

        origin = (self.start, 0)
        parent: Dict[tuple, Optional[tuple]] = {origin: None}
        queue = deque([origin])
        while queue:
            node = queue.popleft()
            nonterminal, i = node
            for p in by_lhs.get(nonterminal, ()):
                if p.rhs and p.rhs[-1] in self.nonterminals:
                    body, target = "".join(p.rhs[:-1]), p.rhs[-1]
                else:
                    body, target = "".join(p.rhs), None
                if not word.startswith(body, i):
                    continue
                j = i + len(body)
                if target is None:
                    if j == len(word):
                        path = [p]
                        while parent[node] is not None:
                            node, used = parent[node]
                            path.append(used)
                        return path[::-1]
                else:
                    nxt = (target, j)
                    if nxt not in parent:
                        parent[nxt] = (node, p)
                        queue.append(nxt)
        raise NotDerivableError(f"mot non engendré : {word!r}")

    def _chain(self, rules: Iterable[Production]) -> "DerivationStep":
        step = DerivationStep(self, (self.start,), None, None)
        for p in rules:
            form = step.form
            index = next(i for i, s in enumerate(form) if s in self.nonterminals)
            if form[index] != p.lhs:
                raise ValueError("règle incompatible avec la forme sentencielle")
            step = DerivationStep(self, form[:index] + p.rhs + form[index + 1:], p, step)
        return step


@dataclass(frozen=True)
class DerivationStep:
    """
    Une étape d'une dérivation : forme sentencielle atteinte, règle appliquée
    pour y arriver (``None`` pour l'axiome) et étape précédente.
    """

    grammar: Grammar = field(compare=False, repr=False)
    form: Tuple[str, ...]
    rule: Optional[Production]
    previous: Optional["DerivationStep"] = field(compare=False, repr=False)

    def steps(self) -> List["DerivationStep"]:
        """Toutes les étapes, de l'axiome jusqu'à celle-ci."""
        chain, current = [], self
        while current is not None:
            chain.append(current)
            current = current.previous
        return chain[::-1]

    def rules(self) -> List[Production]:
        """Règles appliquées, dans l'ordre."""
        return [s.rule for s in self.steps() if s.rule is not None]

    def is_complete(self) -> bool:
        """Vrai si la forme ne contient plus de non-terminal."""
        return all(s in self.grammar.terminals for s in self.form)

    def word(self) -> str:
        """Mot dérivé (la forme doit être terminale)."""
        if not self.is_complete():
            raise ValueError(f"forme non terminale : {''.join(self.form)}")
        return "".join(self.form)

    def sequence(self, sep: str = " => ") -> str:
        """Suite des formes sentencielles, ex. ``S => aS => aaS => aab``."""
        return sep.join("".join(s.form) or "ε" for s in self.steps())

    def parse_tree(self) -> "ParseTree":
        """Arbre de dérivation correspondant (dérivation la plus à gauche)."""
        root = _Node(self.grammar.start)
        open_nodes = [root]
        for step in self.steps()[1:]:
            index = next(i for i, n in enumerate(open_nodes)
                         if n.symbol in self.grammar.nonterminals)
            node = open_nodes[index]
            children = [_Node(s) for s in step.rule.rhs] or [_Node("ε")]
            node.children = children
            open_nodes[index:index + 1] = [c for c in children if c.symbol != "ε"]
        return root.freeze()

    def __repr__(self) -> str:
        return f"DerivationStep({self.sequence()!r})"


class _Node:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.children: List["_Node"] = []

    def freeze(self) -> "ParseTree":
        return ParseTree(self.symbol, tuple(c.freeze() for c in self.children))


@dataclass(frozen=True)
class ParseTree:
    """Arbre de dérivation : un symbole et ses fils (``ε`` pour une règle vide)."""

    symbol: str
    children: Tuple["ParseTree", ...] = ()

    def leaves(self) -> List[str]:
        """Feuilles de gauche à droite (symboles, ε compris)."""
        if not self.children:
            return [self.symbol]
        return [leaf for c in self.children for leaf in c.leaves()]

    def word(self) -> str:
        """Mot lu sur les feuilles (ε ignoré)."""
        return "".join(leaf for leaf in self.leaves() if leaf != "ε")

    def depth(self) -> int:
        """Hauteur de l'arbre (une feuille seule : 0)."""
        return 0 if not self.children else 1 + max(c.depth() for c in self.children)

    def to_dot(self) -> str:
        """Description Graphviz de l'arbre."""
        lines = ["digraph {", "\tnode [shape=plaintext]", "\tedge [arrowhead=none]"]
        counter = [0]

        def visit(node: "ParseTree") -> int:
            ident = counter[0]
            counter[0] += 1
            label = node.symbol.replace('"', '\\"')
            shape = "circle" if node.children else "plaintext"
            lines.append(f'\tn{ident} [label="{label}" shape={shape}]')
            for child in node.children:
                lines.append(f"\tn{ident} -> n{visit(child)}")
            return ident

        visit(self)
        lines.append("}")
        return "\n".join(lines)

    def __str__(self) -> str:
        out: List[str] = []

        def visit(node: "ParseTree", depth: int) -> None:
            out.append("  " * depth + node.symbol)
            for child in node.children:
                visit(child, depth + 1)

        visit(self, 0)
        return "\n".join(out)
