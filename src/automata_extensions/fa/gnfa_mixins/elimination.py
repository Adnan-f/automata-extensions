"""GNFAEliminationMixin : élimination d'états d'un GNFA (item 39)."""

from __future__ import annotations

from typing import Optional, Sequence

from ...regex.ast import EMPTY, EPSILON, Regex, concat, star, union
from ...regex.parser import parse


def _to_ast(label: Optional[str]) -> Regex:
    """``None`` (pas de transition) -> ∅ ; texte -> AST normalisé."""
    return EMPTY if label is None else parse(label).simplify()


def _to_label(node: Regex) -> Optional[str]:
    """Inverse de ``_to_ast`` : ∅ -> ``None``, ε -> ``""``."""
    if node == EMPTY:
        return None
    if node == EPSILON:
        return ""
    return str(node)


class GNFAEliminationMixin:
    """Méthode d'élimination d'états (« state elimination ») sur un GNFA."""

    def eliminate_state(self, state):
        """
        GNFA équivalent sans l'état ``state`` (un pas de la méthode d'élimination).

        Pour tous les états ``p`` (≠ final) et ``r`` (≠ initial) restants, la nouvelle
        étiquette est ``T(p, r) | T(p, q) T(q, q)* T(q, r)`` où ``q`` est l'état supprimé.

        Parameters
        ----------
        state
            État à supprimer ; ni l'état initial ni l'état final.

        Returns
        -------
        GNFA
            Nouvel automate (même classe), ``self`` n'est pas modifié.

        Raises
        ------
        ValueError
            Si ``state`` n'est pas un état, ou est l'état initial ou final.

        Complexity
        ----------
        O(|Q|^2) opérations sur des expressions régulières.

        References
        ----------
        Sipser, « Introduction to the Theory of Computation » (conversion GNFA -> regex).
        """
        if state not in self.states:
            raise ValueError(f"état inconnu : {state!r}")
        if state in (self.initial_state, self.final_state):
            raise ValueError("on ne peut éliminer ni l'état initial ni l'état final")
        kept = [s for s in self.states if s != state]
        loop = star(_to_ast(self.transitions[state].get(state)))
        transitions = {}
        for p in kept:
            if p == self.final_state:
                continue
            into_state = _to_ast(self.transitions[p].get(state))
            row = {}
            for r in kept:
                if r == self.initial_state:
                    continue
                direct = _to_ast(self.transitions[p].get(r))
                through = concat(into_state, loop, _to_ast(self.transitions[state].get(r)))
                row[r] = _to_label(union(direct, through))
            transitions[p] = row
        return self.__class__(
            states=frozenset(kept), input_symbols=frozenset(self.input_symbols),
            transitions=transitions, initial_state=self.initial_state,
            final_state=self.final_state)

    def eliminate_states(self, order: Optional[Sequence] = None):
        """
        Élimine tous les états intermédiaires ; il reste le GNFA à deux états dont la
        transition ``initial -> final`` est l'expression régulière du langage.

        Parameters
        ----------
        order : sequence, optional
            Ordre d'élimination (par défaut : ordre déterministe des états). Il change
            l'écriture de l'expression, jamais le langage.

        Returns
        -------
        GNFA
            Utiliser ``g.transitions[g.initial_state][g.final_state]`` pour lire l'expression
            (``None`` si le langage est vide).

        Raises
        ------
        ValueError
            Si ``order`` n'est pas une permutation des états intermédiaires.

        Complexity
        ----------
        O(|Q|^3) opérations sur des expressions (tailles potentiellement exponentielles).
        """
        from ...utils.ordering import sort_states

        middle = [s for s in self.states if s not in (self.initial_state, self.final_state)]
        sequence = sort_states(middle) if order is None else list(order)
        if len(sequence) != len(middle) or set(sequence) != set(middle):
            raise ValueError("order doit être une permutation des états intermédiaires")
        current = self
        for state in sequence:
            current = current.eliminate_state(state)
        return current
