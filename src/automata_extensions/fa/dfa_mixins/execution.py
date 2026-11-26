"""ExecutionMixin (DFA) : trace d'exécution d'un mot (item 16)."""

from __future__ import annotations

from typing import List, Tuple


class ExecutionMixin:
    """Trace pas à pas de la lecture d'un mot par un DFA."""

    def _trace_start(self):
        return self.initial_state

    @staticmethod
    def _format_config(state) -> str:
        return str(state)

    def execution_trace(self, word: str) -> List[Tuple]:
        """
        Trace complète de la lecture de ``word``.

        Returns
        -------
        list of (état, symbole, état)
            Une transition par symbole lu. La liste s'arrête avant le premier
            symbole sans transition (DFA partiel ou symbole hors alphabet) :
            elle est alors plus courte que le mot.

        Complexity
        ----------
        O(|mot|)
        """
        trace = []
        state = self.initial_state
        for symbol in word:
            row = self.transitions.get(state, {})
            if symbol not in row:
                break
            target = row[symbol]
            trace.append((state, symbol, target))
            state = target
        return trace
