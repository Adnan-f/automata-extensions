"""EliminationMixin : suppression des epsilon-transitions (item 37)."""

from __future__ import annotations

from typing import TypeVar

NFAType = TypeVar("NFAType")


class EliminationMixin:
    """
    NFA équivalent sans epsilon-transitions.

    automata-lib fournit ``NFA.eliminate_lambda``, mais cette méthode échoue
    sur les classes étendues (problème de ``__slots__``/reconstruction) ;
    cette implémentation est donc totalement indépendante.
    """

    def remove_epsilon_transitions(self: NFAType) -> NFAType:
        """
        Propage les transitions au travers des fermetures epsilon.

        Pour chaque état p et symbole a (non vide), la nouvelle relation de
        transition est : delta'(p, a) = fermeture_eps(union des delta(q, a)
        pour q dans fermeture_eps(p)). Un état devient final si sa fermeture
        epsilon contient un état final d'origine.

        Returns
        -------
        NFA
            Nouveau NFA équivalent, sans transitions epsilon.

        Complexity
        ----------
        O(|Q|^2 * |Sigma|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        symbols = self.input_symbols
        new_transitions: dict = {}
        new_finals = set()
        finals = self._final_states_set()

        for state in self.states:
            closure = self.epsilon_closure(state)
            if closure & finals:
                new_finals.add(state)
            row = {}
            for symbol in symbols:
                targets = set()
                for q in closure:
                    targets |= set(self.transitions.get(q, {}).get(symbol, ()))
                if targets:
                    row[symbol] = frozenset(self.epsilon_closure_of_set(targets))
            new_transitions[state] = row

        return self.__class__(
            states=frozenset(self.states),
            input_symbols=frozenset(symbols),
            transitions=new_transitions,
            initial_state=self.initial_state,
            final_states=frozenset(new_finals),
        )
