"""ReverseMixin : automate du langage miroir (item 36)."""

from __future__ import annotations


class ReverseMixin:
    """
    Renversement d'un automate : inversion des transitions, échange des
    états initiaux/finaux.

    Le résultat est toujours un ``ExtendedNFA`` : renverser un DFA peut
    introduire du non-déterminisme.
    """

    def reverse(self):
        """
        Automate (NFA) du langage miroir de L(self).

        Returns
        -------
        NFA
            Nouvel ``ExtendedNFA``. S'il n'y a qu'un seul état final, il
            devient directement le nouvel état initial. S'il y en a
            plusieurs, un nouvel état initial est ajouté, relié par
            epsilon-transition à chacun d'eux.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        from ..nfa import ExtendedNFA

        finals = self._final_states_set()
        existing = set(self.states)

        new_transitions: dict = {state: {} for state in existing}
        for source, row in self.transitions.items():
            for symbol, target in row.items():
                targets = target if self._nondeterministic else {target}
                for t in targets:
                    bucket = new_transitions.setdefault(t, {})
                    bucket[symbol] = frozenset(bucket.get(symbol, set()) | {source})

        if len(finals) == 1:
            # Un seul état final : on peut directement en faire le nouvel état
            # initial, sans epsilon-préambule. Évite de créer, après
            # déterminisation, deux sous-ensembles distincts mais sémantiquement
            # équivalents (ce qui casserait la garantie de minimalité de
            # BrzozowskiMixin.brzozowski_minimize).
            new_states = existing
            new_initial = next(iter(finals))
        else:
            # Plusieurs états finaux : un NFA (contrairement à un DFA) ne peut
            # avoir qu'un seul état initial déclaré, donc on fusionne les
            # anciens finaux via un nouvel état relié par epsilon-transitions.
            new_start = "__reverse_start__"
            while new_start in existing:
                new_start += "_"
            new_transitions[new_start] = {"": frozenset(finals)}
            new_states = existing | {new_start}
            new_initial = new_start

        return ExtendedNFA(
            states=frozenset(new_states),
            input_symbols=frozenset(self.input_symbols),
            transitions=new_transitions,
            initial_state=new_initial,
            final_states=frozenset({self.initial_state}),
        )
