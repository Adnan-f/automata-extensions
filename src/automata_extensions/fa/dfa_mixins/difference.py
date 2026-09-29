"""DifferenceMixin : différence de deux DFA (item 44)."""

from __future__ import annotations

from typing import TypeVar

DFAType = TypeVar("DFAType")


class DifferenceMixin:
    """Différence de langages : L(self) \\ L(other) = L(self) ∩ complement(L(other))."""

    def difference(self: DFAType, other: DFAType) -> DFAType:
        """
        Différence des langages : mots de ``self`` absents de ``other``.

        Parameters
        ----------
        other : DFA

        Returns
        -------
        DFA

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|)
        """
        return self.product(
            other,
            is_final=lambda s1, s2: s1 in self.final_states and s2 not in other.final_states,
        )
