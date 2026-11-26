"""InclusionMixin : inclusion et équivalence de langages (items 24-25)."""

from __future__ import annotations


class InclusionMixin:
    """Inclusion (L1 ⊆ L2) et équivalence (L1 = L2) via vacuité de la différence."""

    def is_included_in(self, other) -> bool:
        """
        Teste si L(self) ⊆ L(other).

        Implémenté en testant la vacuité de ``self.difference(other)``
        (item 24 du cahier des charges).

        Parameters
        ----------
        other : DFA

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|)
        """
        return self.difference(other).is_empty()

    def is_equivalent(self, other) -> bool:
        """
        Teste l'égalité de langages L(self) = L(other) par double inclusion.

        Parameters
        ----------
        other : DFA

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        return self.is_included_in(other) and other.is_included_in(self)
