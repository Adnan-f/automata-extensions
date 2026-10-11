"""RegexOptimumMixin : conversion automate -> regex courte (essai de plusieurs ordres).

L'élimination d'états (ou la résolution d'Arden) donne des expressions de
tailles très différentes selon l'ordre d'élimination. On explore ici les
ordres (tous si l'automate est petit, sinon un échantillon reproductible) et
on garde la plus courte, après normalisation de l'AST. Aucune garantie de
minimalité globale.
"""

from __future__ import annotations

from itertools import permutations
from random import Random
from typing import Dict, Iterator, List, Optional, Tuple

from ...regex.ast import EMPTY, EPSILON, Regex, Symbol, concat, star, union

_CONST = object()


def _best(candidates: Iterator[Regex]) -> Optional[str]:
    best: Optional[str] = None
    for r in candidates:
        text = str(r)
        if best is None or (len(text), text) < (len(best), best):
            best = text
    return best


def _orders(states: List, max_exhaustive: int, samples: int, seed: int) -> Iterator[Tuple]:
    states = sorted(states, key=str)
    if len(states) <= max_exhaustive:
        yield from permutations(states)
        return
    yield tuple(states)
    yield tuple(reversed(states))
    rng = Random(seed)
    for _ in range(samples):
        shuffled = list(states)
        rng.shuffle(shuffled)
        yield tuple(shuffled)


class RegexOptimumMixin:
    """Variantes « courtes » de ``to_regex`` et ``to_regex_arden`` (AST normalisé)."""

    def _useful_edges(self) -> Tuple[Dict[tuple, Regex], set]:
        useful = self.useful_states()
        edges: Dict[tuple, Regex] = {}
        for p in useful:
            for symbol, target in self.transitions.get(p, {}).items():
                targets = target if self._nondeterministic else {target}
                label = EPSILON if symbol == "" else Symbol(symbol)
                for q in targets:
                    if q in useful:
                        edges[(p, q)] = union(edges.get((p, q), EMPTY), label)
        return edges, useful

    @staticmethod
    def _eliminate(edges, order, initial, finals) -> Regex:
        S, A = object(), object()
        edges = dict(edges)
        edges[(S, initial)] = EPSILON
        for f in finals:
            edges[(f, A)] = union(edges.get((f, A), EMPTY), EPSILON)
        for q in order:
            loop = star(edges.pop((q, q), EMPTY))
            ins = [(p, r) for (p, x), r in edges.items() if x == q]
            outs = [(x, r) for (p, x), r in edges.items() if p == q]
            for p, _ in ins:
                del edges[(p, q)]
            for x, _ in outs:
                del edges[(q, x)]
            for p, rin in ins:
                for x, rout in outs:
                    edges[(p, x)] = union(edges.get((p, x), EMPTY), concat(rin, loop, rout))
        return edges.get((S, A), EMPTY)

    @staticmethod
    def _solve_arden(edges, order, initial, finals, useful) -> Regex:
        equations: Dict = {q: {} for q in useful}
        for (p, q), r in edges.items():
            equations[p][q] = r
        for f in finals:
            equations[f][_CONST] = EPSILON
        for q in order:
            eq_q = equations.pop(q)
            star_self = star(eq_q.pop(q, EMPTY))
            resolved = {t: concat(star_self, c) for t, c in eq_q.items()}
            for eq_p in equations.values():
                c_to_q = eq_p.pop(q, None)
                if c_to_q is None:
                    continue
                for t, c in resolved.items():
                    eq_p[t] = union(eq_p.get(t, EMPTY), concat(c_to_q, c))
        final_eq = equations[initial]
        star_self = star(final_eq.pop(initial, EMPTY))
        return concat(star_self, final_eq.get(_CONST, EMPTY))

    def to_regex_optimum(
        self, max_exhaustive: int = 6, samples: int = 200, seed: int = 0
    ) -> Optional[str]:
        """
        Expression régulière courte, par élimination d'états avec essai de plusieurs ordres.

        Parameters
        ----------
        max_exhaustive : int
            Jusqu'à ce nombre d'états utiles, tous les ordres sont essayés.
        samples : int
            Au-delà, nombre d'ordres aléatoires essayés (graine ``seed``).

        Returns
        -------
        str or None
            La plus courte expression trouvée ; ``None`` si le langage est vide.

        Complexity
        ----------
        O(k * |Q|^3) pour k ordres essayés (k = |Q|! si |Q| <= max_exhaustive).
        """
        edges, useful = self._useful_edges()
        if self.initial_state not in useful:
            return None
        finals = self._final_states_set() & useful
        return _best(
            self._eliminate(edges, order, self.initial_state, finals)
            for order in _orders(list(useful), max_exhaustive, samples, seed)
        )

    def to_regex_arden_optimum(
        self, max_exhaustive: int = 6, samples: int = 200, seed: int = 0
    ) -> Optional[str]:
        """
        Comme ``to_regex_optimum``, mais par résolution d'Arden (ordre d'élimination variable).

        Returns
        -------
        str or None
            La plus courte expression trouvée ; ``None`` si le langage est vide.

        Complexity
        ----------
        O(k * |Q|^3)
        """
        edges, useful = self._useful_edges()
        if self.initial_state not in useful:
            return None
        finals = self._final_states_set() & useful
        others = [q for q in useful if q != self.initial_state]
        return _best(
            self._solve_arden(edges, order, self.initial_state, finals, useful)
            for order in _orders(others, max_exhaustive, samples, seed)
        )
