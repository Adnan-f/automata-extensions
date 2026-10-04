"""DeterminizationMixin : construction des sous-ensembles (item 35)."""

from __future__ import annotations

from typing import TypeVar

NFAType = TypeVar("NFAType")
DFAType = TypeVar("DFAType")


class DeterminizationMixin:
    """Détermine un NFA (avec ou sans epsilon-transitions) par construction des sous-ensembles."""

    def determinize(self) -> "DFAType":
        """
        Construction des sous-ensembles : DFA équivalent au NFA.

        Chaque état du DFA résultat est un ``frozenset`` d'états du NFA
        (sa fermeture epsilon). Seuls les sous-ensembles accessibles depuis
        l'état initial sont construits.

        Returns
        -------
        DFA
            Nouveau DFA équivalent, de type ``ExtendedDFA``.

        Complexity
        ----------
        O(2^|Q| * |Sigma|) dans le pire cas.

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        has_epsilon = any("" in row for row in self.transitions.values())
        # La fermeture epsilon de l'état initial doit être calculée AVANT
        # d'éliminer les epsilon-transitions (sinon elle est triviale).
        start = frozenset(self.epsilon_closure(self.initial_state)) \
            if has_epsilon else frozenset({self.initial_state})
        source = self.remove_epsilon_transitions() if has_epsilon else self
        finals = source._final_states_set()

        transitions: dict = {}
        states = {start}
        queue = [start]
        head = 0
        while head < len(queue):
            current = queue[head]
            head += 1
            row = {}
            for symbol in source.input_symbols:
                target = set()
                for q in current:
                    target |= set(source.transitions.get(q, {}).get(symbol, ()))
                target = frozenset(target)
                row[symbol] = target
                # ``target`` peut être l'ensemble vide (état puits implicite,
                # cas d'un NFA partiel) : il doit aussi devenir un état du DFA.
                if target not in states:
                    states.add(target)
                    queue.append(target)
            transitions[current] = row

        final_states = {s for s in states if s & finals}

        from ..dfa import ExtendedDFA  # import tardif (dépendance circulaire sinon)

        return ExtendedDFA(
            states=frozenset(states),
            input_symbols=frozenset(source.input_symbols),
            transitions=transitions,
            initial_state=start,
            final_states=frozenset(final_states),
            allow_partial=True,
        )

    def to_dfa(self) -> "DFAType":
        """
        Alias de ``determinize``.

        Returns
        -------
        DFA

        Complexity
        ----------
        O(2^|Q| * |Sigma|)
        """
        return self.determinize()
