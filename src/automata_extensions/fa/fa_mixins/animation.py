"""AnimationMixin : animation HTML autonome de la lecture d'un mot.

La page produite est un unique fichier HTML sans dépendance externe : le
diagramme est un SVG généré en Python (placement en colonnes, voir
``VisualisationMixin._viz_layout``) et un court JavaScript colore les états
actifs et les transitions empruntées à chaque pas (boutons, lecture
automatique, flèches du clavier).
"""

from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_X, _Y = 140.0, 120.0           # écart entre colonnes / lignes (px)
_LEFT, _TOP = 100.0, 90.0       # marges (la gauche laisse place à la flèche initiale)
_R = 24.0                       # rayon d'un état

_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>%%TITLE%%</title>
<style>
  :root { --bg:#ffffff; --fg:#1f2430; --muted:#6b7280; --edge:#8a93a6; --accent:#2563eb;
          --accent-bg:#dbeafe; --ok:#15803d; --ko:#b91c1c; --panel:#f3f4f6; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#14171f; --fg:#e5e7eb; --muted:#9ca3af; --edge:#6b7280; --accent:#60a5fa;
            --accent-bg:#1e3a5f; --ok:#4ade80; --ko:#f87171; --panel:#1f2430; } }
  body { margin:0; padding:1.2rem; background:var(--bg); color:var(--fg);
         font-family:system-ui,-apple-system,Segoe UI,sans-serif; }
  h1 { font-size:1.05rem; margin:0 0 .8rem; }
  #diagram { width:100%; max-width:%%MAXW%%px; height:auto; background:var(--panel);
             border-radius:10px; }
  .state circle { fill:var(--bg); stroke:var(--fg); stroke-width:2; }
  .state .inner { fill:none; }
  .state text, .edge text { fill:var(--fg); text-anchor:middle; dominant-baseline:central;
                            font-size:14px; }
  .edge text { font-size:13px; }
  .edge path, .start-arrow { fill:none; stroke:var(--edge); stroke-width:1.6; }
  .state.active circle { fill:var(--accent-bg); stroke:var(--accent); stroke-width:3.5; }
  .state.active text { font-weight:700; }
  .state.blocked circle { stroke:var(--ko); }
  .edge.used path { stroke:var(--accent); stroke-width:3.2; }
  .edge.used text { fill:var(--accent); font-weight:700; }
  #arrow-head { fill:var(--edge); } #arrow-used-head { fill:var(--accent); }
  #word { font-family:ui-monospace,Menlo,Consolas,monospace; font-size:1.5rem;
          margin:.9rem 0 .3rem; letter-spacing:.12em; }
  #word span { padding:0 .08em; border-bottom:3px solid transparent; }
  #word .done { color:var(--muted); }
  #word .current { border-bottom-color:var(--accent); color:var(--accent); font-weight:700; }
  #note { min-height:1.4em; margin:.2rem 0 .6rem; }
  #verdict { font-weight:700; }
  #verdict.ok { color:var(--ok); } #verdict.ko { color:var(--ko); }
  button { font:inherit; padding:.35rem .8rem; margin-right:.3rem; border-radius:6px;
           border:1px solid var(--edge); background:var(--panel); color:var(--fg); cursor:pointer; }
  button:disabled { opacity:.4; cursor:default; }
  #counter { color:var(--muted); margin-left:.6rem; }
</style>
</head>
<body>
<h1>%%TITLE%%</h1>
%%SVG%%
<div id="word" aria-label="mot lu"></div>
<div id="note"></div>
<div>
  <button id="reset" title="Début (Origine)">⏮</button>
  <button id="prev" title="Pas précédent (←)">◀</button>
  <button id="next" title="Pas suivant (→)">▶</button>
  <button id="play" title="Lecture automatique (espace)">⏵ Lecture</button>
  <span id="counter"></span> <span id="verdict"></span>
</div>
<script id="automaton-data" type="application/json">%%DATA%%</script>
<script>
(function () {
  var D = JSON.parse(document.getElementById("automaton-data").textContent);
  var i = 0, timer = null;
  function $(id) { return document.getElementById(id); }
  function render() {
    var s = D.steps[i], last = i === D.steps.length - 1;
    Array.prototype.forEach.call(document.querySelectorAll(".state"), function (el) {
      el.classList.remove("active", "blocked"); });
    Array.prototype.forEach.call(document.querySelectorAll(".edge"), function (el) {
      el.classList.remove("used");
      el.querySelector("path").setAttribute("marker-end", "url(#arrow)"); });
    s.active.forEach(function (id) {
      $("n_" + id).classList.add(s.blocked ? "blocked" : "active");
      if (s.blocked) { $("n_" + id).classList.add("active"); } });
    s.edges.forEach(function (key) {
      var e = $("e_" + key);
      if (e) { e.classList.add("used");
               e.querySelector("path").setAttribute("marker-end", "url(#arrow-used)"); } });
    var word = $("word"); word.textContent = "";
    if (D.word.length === 0) { word.textContent = "ε"; }
    for (var k = 0; k < D.word.length; k++) {
      var span = document.createElement("span");
      span.textContent = D.word.charAt(k);
      if (k < s.consumed) { span.className = "done"; }
      else if (k === s.consumed && !last) { span.className = "current"; }
      word.appendChild(span);
    }
    $("note").textContent = s.note;
    $("counter").textContent = (i + 1) + " / " + D.steps.length;
    $("prev").disabled = $("reset").disabled = (i === 0);
    $("next").disabled = last;
    var v = $("verdict");
    if (last) { v.textContent = D.accepted ? "✔ mot accepté" : "✘ mot rejeté";
                v.className = D.accepted ? "ok" : "ko"; }
    else { v.textContent = ""; v.className = ""; }
    if (last) { stop(); }
  }
  function go(n) { i = Math.max(0, Math.min(D.steps.length - 1, n)); render(); }
  function stop() { if (timer) { clearInterval(timer); timer = null; }
                    $("play").textContent = "⏵ Lecture"; }
  function play() {
    if (timer) { stop(); return; }
    if (i === D.steps.length - 1) { i = 0; render(); }
    $("play").textContent = "⏸ Pause";
    timer = setInterval(function () { go(i + 1); }, 900);
  }
  $("reset").addEventListener("click", function () { stop(); go(0); });
  $("prev").addEventListener("click", function () { stop(); go(i - 1); });
  $("next").addEventListener("click", function () { stop(); go(i + 1); });
  $("play").addEventListener("click", play);
  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") { stop(); go(i + 1); }
    else if (e.key === "ArrowLeft") { stop(); go(i - 1); }
    else if (e.key === " ") { e.preventDefault(); play(); } });
  render();
})();
</script>
</body>
</html>
"""


def _unit(dx: float, dy: float) -> Tuple[float, float]:
    length = math.hypot(dx, dy) or 1.0
    return dx / length, dy / length


class AnimationMixin:
    """Animation HTML interactive de la lecture d'un mot (DFA et NFA)."""

    # ---- géométrie SVG ---------------------------------------------------
    @staticmethod
    def _svg_edge_geometry(p1, p2, h: float) -> Tuple[str, Tuple[float, float], List[Tuple[float, float]]]:
        """Trajet (attribut ``d``), position de l'étiquette et points d'encombrement d'une arête."""
        (x1, y1), (x2, y2) = p1, p2
        if p1 == p2:                                       # boucle au-dessus de l'état
            a1, a2 = math.radians(-125), math.radians(-55)
            sx, sy = x1 + _R * math.cos(a1), y1 + _R * math.sin(a1)
            ex, ey = x1 + _R * math.cos(a2), y1 + _R * math.sin(a2)
            d = (f"M {sx:.1f} {sy:.1f} C {x1 - 40:.1f} {y1 - _R - 56:.1f} "
                 f"{x1 + 40:.1f} {y1 - _R - 56:.1f} {ex:.1f} {ey:.1f}")
            label = (x1, y1 - _R - 48)
            extent = [label, (x1 - 40, y1 - _R - 42), (x1 + 40, y1 - _R - 42)]
            return d, label, extent
        ux, uy = _unit(x2 - x1, y2 - y1)
        px, py = uy, -ux                                    # perpendiculaire (à gauche du sens de marche)
        if not h:
            sx, sy = x1 + ux * _R, y1 + uy * _R
            ex, ey = x2 - ux * _R, y2 - uy * _R
            d = f"M {sx:.1f} {sy:.1f} L {ex:.1f} {ey:.1f}"
            label = ((sx + ex) / 2 + px * 13, (sy + ey) / 2 + py * 13)
            return d, label, [(sx, sy), (ex, ey), label]
        bend = 2 * h * _Y                                  # h est en unités de ligne
        cx, cy = (x1 + x2) / 2 + px * bend, (y1 + y2) / 2 + py * bend
        sux, suy = _unit(cx - x1, cy - y1)
        eux, euy = _unit(cx - x2, cy - y2)
        sx, sy = x1 + sux * _R, y1 + suy * _R
        ex, ey = x2 + eux * _R, y2 + euy * _R
        # Quadratique écrite en cubique équivalente : certains moteurs de rendu
        # n'affichent pas les marqueurs (pointes de flèche) sur les segments « Q ».
        c1x, c1y = sx + 2 / 3 * (cx - sx), sy + 2 / 3 * (cy - sy)
        c2x, c2y = ex + 2 / 3 * (cx - ex), ey + 2 / 3 * (cy - ey)
        d = (f"M {sx:.1f} {sy:.1f} C {c1x:.1f} {c1y:.1f} {c2x:.1f} {c2y:.1f} "
             f"{ex:.1f} {ey:.1f}")
        mx, my = 0.25 * sx + 0.5 * cx + 0.25 * ex, 0.25 * sy + 0.5 * cy + 0.25 * ey
        side = 11 if h > 0 else -11
        label = (mx + px * side, my + py * side)
        extent = [label]
        for i in range(11):
            t = i / 10
            extent.append(((1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t * t * ex,
                           (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t * t * ey))
        return d, label, extent

    def _svg_diagram(self) -> Tuple[str, float]:
        """SVG du diagramme (états ``n_<id>``, arêtes ``e_<id>_<id>``) et sa largeur."""
        ids = self._dot_ids()
        layout = self._viz_layout()
        edges = self._viz_edges()
        bends = self._viz_bends(layout, edges)
        finals = self._viz_finals()
        pos: Dict = {s: (_LEFT + c * _X, _TOP + r * _Y) for s, (c, r) in layout.items()}
        x0, y0 = pos[self.initial_state]
        extent = [(x - _R - 8, y - _R - 8) for x, y in pos.values()]
        extent += [(x + _R + 8, y + _R + 8) for x, y in pos.values()]
        extent.append((x0 - _R - 54, y0))
        drawn = []
        for src, dst, label in edges:
            d, (lx, ly), pts = self._svg_edge_geometry(pos[src], pos[dst], bends.get((src, dst), 0.0))
            drawn.append((src, dst, label, d, lx, ly))
            extent += [(px_ - 12, py_ - 12) for px_, py_ in pts] + [(px_ + 12, py_ + 12) for px_, py_ in pts]
        pad = 12
        min_x = min(x for x, _ in extent) - pad
        min_y = min(y for _, y in extent) - pad
        width = max(x for x, _ in extent) + pad - min_x
        height = max(y for _, y in extent) + pad - min_y
        parts: List[str] = [
            f'<svg id="diagram" viewBox="{min_x:.0f} {min_y:.0f} {width:.0f} {height:.0f}" '
            f'xmlns="http://www.w3.org/2000/svg" role="img">',
            '<defs>'
            '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" '
            'markerWidth="11" markerHeight="11" orient="auto-start-reverse">'
            '<path id="arrow-head" d="M0,0 L10,5 L0,10 z"/></marker>'
            '<marker id="arrow-used" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" '
            'markerWidth="11" markerHeight="11" orient="auto-start-reverse">'
            '<path id="arrow-used-head" d="M0,0 L10,5 L0,10 z"/></marker>'
            '</defs>']
        parts.append(f'<line class="start-arrow" x1="{x0 - _R - 46:.1f}" y1="{y0:.1f}" '
                     f'x2="{x0 - _R:.1f}" y2="{y0:.1f}" marker-end="url(#arrow)"/>')
        for src, dst, label, d, lx, ly in drawn:
            parts.append(
                f'<g class="edge" id="e_{ids[src]}_{ids[dst]}"><path d="{d}" marker-end="url(#arrow)"/>'
                f'<text x="{lx:.1f}" y="{ly:.1f}">{html.escape(label)}</text></g>')
        for state in self._viz_states():
            x, y = pos[state]
            text = self._viz_label(state)
            size = 14 if len(text) <= 4 else 11
            inner = (f'<circle class="inner" cx="{x:.1f}" cy="{y:.1f}" r="{_R - 5:.0f}"/>'
                     if state in finals else "")
            parts.append(
                f'<g class="state" id="n_{ids[state]}"><circle cx="{x:.1f}" cy="{y:.1f}" r="{_R:.0f}"/>'
                f'{inner}<text x="{x:.1f}" y="{y:.1f}" style="font-size:{size}px">'
                f'{html.escape(text)}</text></g>')
        parts.append("</svg>")
        return "\n".join(parts), width

    # ---- pas d'animation -------------------------------------------------
    def _animation_steps(self, word: str) -> List[Dict]:
        ids = self._dot_ids()
        as_set = (lambda c: set(c)) if self._nondeterministic else (lambda c: {c})
        fmt = lambda c: self._format_config(c)
        trace = self.execution_trace(word)
        start = self._trace_start()
        title = "États initiaux (après ε-fermeture)" if self._nondeterministic else "État initial"
        steps: List[Dict] = [{
            "active": sorted(ids[s] for s in as_set(start)), "edges": [], "consumed": 0,
            "blocked": False, "note": f"{title} : {fmt(start)}"}]
        for index, (before, symbol, after) in enumerate(trace):
            used = []
            for p in as_set(before):
                targets = self.transitions.get(p, {}).get(symbol)
                if targets is None:
                    continue
                for q in (targets if self._nondeterministic else {targets}):
                    if q in as_set(after):
                        used.append(f"{ids[p]}_{ids[q]}")
            steps.append({
                "active": sorted(ids[s] for s in as_set(after)), "edges": sorted(set(used)),
                "consumed": index + 1, "blocked": False,
                "note": f"Lecture de « {symbol} » : {fmt(before)} → {fmt(after)}"})
        if len(trace) < len(word):
            blocked_on = word[len(trace)]
            last = steps[-1]
            reason = ("plus aucun état actif" if self._nondeterministic
                      else f"aucune transition pour « {blocked_on} »")
            steps.append({"active": last["active"], "edges": [], "consumed": len(trace),
                          "blocked": not self._nondeterministic,
                          "note": f"Blocage : {reason}."})
        return steps

    def animate(self, word: str, path=None) -> str:
        """
        Page HTML autonome animant la lecture de ``word``.

        La page montre le diagramme, le mot (lettres lues grisées, lettre
        courante soulignée) et des commandes : début, pas précédent/suivant,
        lecture automatique ; les flèches ← → et la barre d'espace fonctionnent
        aussi. Pour un NFA, tous les états actifs (après ε-fermeture) sont
        colorés à chaque pas.

        Parameters
        ----------
        word : str
            Mot à lire.
        path : str or Path, optional
            Si fourni, la page est aussi écrite dans ce fichier.

        Returns
        -------
        str
            Document HTML complet (aucune dépendance externe).

        Raises
        ------
        TypeError
            Pour un GNFA (pas de simulation pas à pas).

        Complexity
        ----------
        O(|mot| * |Q| * |E| + |Q| + |E|)
        """
        if not hasattr(self, "execution_trace"):
            raise TypeError("animate n'est pas défini pour ce type d'automate (GNFA)")
        svg, width = self._svg_diagram()
        steps = self._animation_steps(word)
        accepted = self.accepts_input(word)
        shown = word if word else "ε"
        title = f"Lecture du mot « {shown} »"
        data = json.dumps({"word": word, "steps": steps, "accepted": accepted},
                          ensure_ascii=False)
        data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        page = (_TEMPLATE.replace("%%TITLE%%", html.escape(title))
                .replace("%%MAXW%%", f"{max(width, 520):.0f}")
                .replace("%%SVG%%", svg).replace("%%DATA%%", data))
        if path is not None:
            Path(path).write_text(page, encoding="utf-8")
        return page
