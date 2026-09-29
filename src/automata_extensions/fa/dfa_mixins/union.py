"""UnionMixin : union de deux DFA par produit synchronisé (item 42)."""

from __future__ import annotations

from typing import TypeVar

DFAType = TypeVar("DFAType")


class UnionMixin:
    """Union de deux DFA sur le même alphabet, par produit synchronisé."""

    def union(self: DFAType, other: DFAType) -> DFAType:
        """
        Union des langages : L(self) ∪ L(other).

        Parameters
        ----------
        other : DFA

        Returns
        -------
        DFA

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        return self.product(
            other,
            is_final=lambda s1, s2: s1 in self.final_states or s2 in other.final_states,
        )
