"""EpsilonMixin : fermeture epsilon d'un état ou d'un ensemble d'états."""

from __future__ import annotations

from typing import AbstractSet, Iterable


class EpsilonMixin:
    """Fermeture epsilon (item 34 du cahier des charges)."""

    def epsilon_closure(self, state) -> AbstractSet:
        """
        Fermeture epsilon d'un seul état.

        Parameters
        ----------
        state
            État de départ.

        Returns
        -------
        set
            États atteignables en ne suivant que des epsilon-transitions
            (y compris ``state`` lui-même).

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        return self.epsilon_closure_of_set({state})

    def epsilon_closure_of_set(self, states: Iterable) -> AbstractSet:
        """
        Fermeture epsilon d'un ensemble d'états.

        Parameters
        ----------
        states : Iterable
            États de départ.

        Returns
        -------
        set
            États atteignables en ne suivant que des epsilon-transitions,
            à partir de n'importe quel état de ``states``.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        closure = set(states)
        stack = list(closure)
        while stack:
            current = stack.pop()
            row = self.transitions.get(current, {})
            for target in row.get("", ()):
                if target not in closure:
                    closure.add(target)
                    stack.append(target)
        return closure
