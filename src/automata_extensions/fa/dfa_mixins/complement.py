"""ComplementMixin : complémentaire d'un DFA et test du langage universel."""

from __future__ import annotations

from typing import TypeVar

DFAType = TypeVar("DFAType")


class ComplementMixin:
    """Complémentaire d'un DFA (item 22) et décision du langage universel (38)."""

    def complement(self: DFAType, minify: bool = False, retain_names: bool = False) -> DFAType:
        """
        Complémentaire du langage reconnu.

        Complète d'abord le DFA si besoin, puis échange les états finaux et
        non finaux. Contrairement à ``DFA.complement`` d'automata-lib, la
        minimisation n'est pas faite par défaut.

        Parameters
        ----------
        minify : bool
            Si ``True``, minimise le résultat (``minimize``).
        retain_names : bool
            Avec ``minify=True``, nomme chaque classe fusionnée par un de ses états
            d'origine plutôt que par le ``frozenset`` de la classe.

        Returns
        -------
        DFA
            Nouveau DFA reconnaissant le complémentaire du langage.

        Complexity
        ----------
        O(|Q| * |Sigma|) ; O(|Q|^2 * |Sigma|) avec ``minify=True``.

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        complete_self = self.complete()
        params = dict(complete_self.input_parameters)
        params["final_states"] = frozenset(
            set(complete_self.states) - set(complete_self.final_states)
        )
        result = self.__class__(**params)
        if minify:
            return result.minimize(keep_original_names=retain_names)
        return result

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