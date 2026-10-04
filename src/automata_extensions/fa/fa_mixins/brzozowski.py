"""BrzozowskiMixin : minimisation de Brzozowski (item 50)."""

from __future__ import annotations

from typing import TypeVar

DFAType = TypeVar("DFAType")


class BrzozowskiMixin:
    """Minimisation par double renversement-déterminisation (algorithme de Brzozowski)."""

    def brzozowski_minimize(self: DFAType) -> DFAType:
        """
        DFA minimal équivalent, par l'algorithme de Brzozowski.

        Principe : reverse + determinize élimine les états inaccessibles
        *et* coaccessibles de l'automate renversé (donc les classes
        d'équivalence du résultat correspondent aux classes de l'original) ;
        répéter l'opération une seconde fois donne un DFA minimal.

        Returns
        -------
        DFA
            Nouveau DFA minimal.

        Complexity
        ----------
        O(2^|Q|) dans le pire cas (la déterminisation peut exploser), mais
        se comporte bien en pratique.

        References
        ----------
        Brzozowski (1962) ; Hopcroft, Motwani, Ullman.
        """
        step1 = self.reverse().determinize()
        step2 = step1.reverse().determinize()
        return step2
