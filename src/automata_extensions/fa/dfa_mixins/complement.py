"""ComplementMixin : complémentaire d'un DFA et test du langage universel."""

from __future__ import annotations

from typing import TypeVar

DFAType = TypeVar("DFAType")


class ComplementMixin:
    """Complémentaire d'un DFA (item 22) et décision du langage universel (38)."""

    def complement(self: DFAType) -> DFAType:
        """
        Complémentaire du langage reconnu.

        Complète d'abord le DFA si besoin, puis échange les états finaux et
        non finaux.

        Returns
        -------
        DFA
            Nouveau DFA reconnaissant le complémentaire du langage.

        Complexity
        ----------
        O(|Q| * |Sigma|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        complete_self = self.complete()
        params = dict(complete_self.input_parameters)
        params["final_states"] = frozenset(
            set(complete_self.states) - set(complete_self.final_states)
        )
        return self.__class__(**params)

    def is_universal(self) -> bool:
        """
        Teste si l'automate reconnaît Sigma* tout entier.

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| * |Sigma|)
        """
        return self.complement().is_empty()
