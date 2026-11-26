"""ExecutionMixin (NFA) : trace d'exécution par ensembles d'états actifs (item 16)."""

from __future__ import annotations

from typing import FrozenSet, List, Tuple


class NFAExecutionMixin:
    """Trace pas à pas de la lecture d'un mot par un NFA."""

    def _trace_start(self) -> FrozenSet:
        return frozenset(self.epsilon_closure(self.initial_state))

    @staticmethod
    def _format_config(states) -> str:
        return "{" + ", ".join(sorted(map(str, states))) + "}"

    def execution_trace(self, word: str) -> List[Tuple[FrozenSet, str, FrozenSet]]:
        """
        Trace de la lecture de ``word`` : ensembles d'états actifs.

        Returns
        -------
        list of (ensemble avant, symbole, ensemble après)
            Les ensembles sont ε-fermés ; le premier est la fermeture de
            l'état initial. La liste s'arrête dès que l'ensemble devient vide
            (cet ensemble vide est le dernier élément enregistré).

        Complexity
        ----------
        O(|mot| * |Q| * |E|)
        """
        current = self._trace_start()
        trace = []
        for symbol in word:
            reached = set()
            for state in current:
                reached |= set(self.transitions.get(state, {}).get(symbol, ()))
            after = frozenset(self.epsilon_closure_of_set(reached))
            trace.append((current, symbol, after))
            current = after
            if not current:
                break
        return trace
