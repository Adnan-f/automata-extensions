"""AccessibilityMixin : états accessibles / coaccessibles / utiles, trim, sous-automate."""

from __future__ import annotations

from typing import AbstractSet, TypeVar

FAType = TypeVar("FAType")


class AccessibilityMixin:
    """Accessibilité, coaccessibilité, élagage (trim) et sous-automates induits."""

    def accessible_states(self) -> set:
        """
        États atteignables depuis l'état initial.

        Returns
        -------
        set
            Ensemble des états accessibles.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani, Ullman — Introduction to Automata Theory,
        Languages, and Computation.
        """
        return self.reachable_states(self.initial_state)

    def is_accessible(self, state) -> bool:
        """
        Teste si ``state`` est accessible depuis l'état initial.

        Parameters
        ----------
        state
            État à tester.

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return state in self.accessible_states()

    def _final_states_set(self) -> AbstractSet:
        """Uniformise ``final_states`` (DFA/NFA) et ``final_state`` (GNFA)."""
        if hasattr(self, "final_states"):
            return set(self.final_states)
        return {self.final_state}

    def _reversed_transitions(self) -> dict:
        """Table de transitions inversée : état -> ensemble des prédécesseurs directs."""
        reversed_map: dict = {state: set() for state in self.states}
        for source, row in self.transitions.items():
            for target in row.values():
                targets = target if isinstance(target, (set, frozenset)) else {target}
                for t in targets:
                    reversed_map.setdefault(t, set()).add(source)
        return reversed_map

    def coaccessible_states(self) -> set:
        """
        États depuis lesquels un état final est atteignable.

        Calculé par un BFS sur l'automate renversé, depuis les états
        accepteurs (item 5 du cahier des charges).

        Returns
        -------
        set
            Ensemble des états coaccessibles.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        reversed_map = self._reversed_transitions()
        finals = self._final_states_set()
        visited = set(finals)
        queue = list(finals)
        head = 0
        while head < len(queue):
            current = queue[head]
            head += 1
            for pred in reversed_map.get(current, ()):
                if pred not in visited:
                    visited.add(pred)
                    queue.append(pred)
        return visited

    def is_coaccessible(self, state) -> bool:
        """
        Teste si un état final est atteignable depuis ``state``.

        Parameters
        ----------
        state
            État à tester.

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return state in self.coaccessible_states()

    def useful_states(self) -> set:
        """
        États à la fois accessibles et coaccessibles.

        Returns
        -------
        set
            Intersection des états accessibles et coaccessibles.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return self.accessible_states() & self.coaccessible_states()

    def is_trim(self) -> bool:
        """
        Teste si tous les états de l'automate sont utiles.

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return self.useful_states() == set(self.states)

    def induced_subautomaton(self: FAType, subset: AbstractSet) -> FAType:
        """
        Sous-automate induit par un sous-ensemble d'états.

        Les transitions dont la source ou la (les) cible(s) sortent de
        ``subset`` sont retirées. ``subset`` doit contenir l'état initial.

        Parameters
        ----------
        subset : AbstractSet
            États à conserver.

        Returns
        -------
        FA
            Nouvel automate (même classe que ``self``), non modifié en place.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        subset = set(subset)
        if self.initial_state not in subset:
            raise ValueError(
                "induced_subautomaton: l'état initial doit appartenir au sous-ensemble."
            )
        new_transitions: dict = {}
        for source, row in self.transitions.items():
            if source not in subset:
                continue
            new_row = {}
            for symbol, target in row.items():
                if isinstance(target, (set, frozenset)):
                    kept = frozenset(t for t in target if t in subset)
                    if kept:
                        new_row[symbol] = kept
                elif target in subset:
                    new_row[symbol] = target
            new_transitions[source] = new_row

        params = dict(self.input_parameters)
        params["states"] = frozenset(subset)
        params["transitions"] = new_transitions
        if "allow_partial" in params:
            params["allow_partial"] = True
        if "final_states" in params:
            params["final_states"] = frozenset(subset & self._final_states_set())
        else:
            if self.final_state not in subset:
                raise ValueError(
                    "induced_subautomaton: l'état final du GNFA doit rester dans le sous-ensemble."
                )
        return self.__class__(**params)

    def trim(self: FAType) -> FAType:
        """
        Automate élagué : restriction aux états utiles.

        Returns
        -------
        FA
            Nouvel automate ne contenant que des états utiles.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return self.induced_subautomaton(self.useful_states())