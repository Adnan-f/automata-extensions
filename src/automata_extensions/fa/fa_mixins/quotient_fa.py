"""QuotientMixin : quotients d'un langage par un MOT (items 47, 48).

Nommés ``*_word`` pour ne pas entrer en collision avec ``NFA.left_quotient`` /
``right_quotient`` d'automata-lib, qui prennent un *automate* en argument.
"""

from __future__ import annotations


class QuotientMixin:
    """Quotients gauche (``w^-1 L``) et droit (``L w^-1``) par un mot."""

    def _check_quotient_supported(self) -> None:
        from automata.fa.gnfa import GNFA

        if isinstance(self, GNFA):
            raise TypeError("les quotients ne sont pas définis pour un GNFA")

    def _delta_star(self, states, word: str) -> set:
        """États atteints depuis ``states`` en lisant ``word`` (ε-fermeture pour un NFA)."""
        current = set(states)
        if self._nondeterministic:
            current = set(self.epsilon_closure_of_set(current))
        for symbol in word:
            reached = set()
            for state in current:
                target = self.transitions.get(state, {}).get(symbol)
                if target is None:
                    continue
                reached |= set(target) if self._nondeterministic else {target}
            current = set(self.epsilon_closure_of_set(reached)) if self._nondeterministic else reached
            if not current:
                break
        return current

    def left_quotient_word(self, word: str):
        """
        Quotient à gauche par un mot : ``{u : word·u ∈ L}``.

        DFA : le nouvel état initial est l'état atteint après lecture de
        ``word``. NFA : un nouvel état initial est relié par ε-transitions à
        tous les états atteints. Seuls les états accessibles sont conservés.
        Si ``word`` bloque l'automate, le résultat reconnaît le langage vide.

        Returns
        -------
        FA
            Nouvel automate de même classe que ``self``.

        Complexity
        ----------
        O(|mot| * |Q| + |Q| + |E|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        self._check_quotient_supported()
        reached = self._delta_star({self.initial_state}, word)
        params = dict(self.input_parameters)

        if not self._nondeterministic:
            if not reached:
                params.update(states=frozenset({self.initial_state}),
                              transitions={self.initial_state: {}},
                              final_states=frozenset(), allow_partial=True)
                return self.__class__(**params)
            params["initial_state"] = next(iter(reached))
        else:
            taken = set(self.states)
            start = "__lq_start__"
            while start in taken:
                start += "_"
            transitions = {s: dict(row) for s, row in self.transitions.items()}
            transitions[start] = {"": frozenset(reached)} if reached else {}
            params.update(states=frozenset(taken | {start}), transitions=transitions,
                          initial_state=start)

        built = self.__class__(**params)
        return built.induced_subautomaton(built.accessible_states())

    def right_quotient_word(self, word: str):
        """
        Quotient à droite par un mot : ``{u : u·word ∈ L}``.

        Les nouveaux états finaux sont ceux depuis lesquels la lecture de
        ``word`` atteint un état final d'origine.

        Returns
        -------
        FA
            Nouvel automate de même classe que ``self`` (mêmes états et
            transitions, états finaux modifiés).

        Complexity
        ----------
        O(|Q| * |mot| * |Q|)
        """
        self._check_quotient_supported()
        finals = self._final_states_set()
        new_finals = frozenset(
            q for q in self.states if self._delta_star({q}, word) & finals
        )
        params = dict(self.input_parameters)
        params["final_states"] = new_finals
        return self.__class__(**params)
