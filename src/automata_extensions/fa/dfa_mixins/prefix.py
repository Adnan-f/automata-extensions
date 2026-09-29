"""PrefixMixin : clôture par préfixe (items 27-28)."""

from __future__ import annotations

from typing import TypeVar

DFAType = TypeVar("DFAType")


class PrefixMixin:
    """Test de clôture par préfixe et extraction du plus grand sous-langage préfixe-clos."""

    def is_prefix_closed(self) -> bool:
        """
        Teste si le langage est clos par préfixe.

        Un langage est préfixe-clos ssi tous ses états utiles sont finaux :
        s'il existait un état utile non final, un mot y menant serait un
        préfixe d'un mot accepté sans être lui-même accepté.

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| + |E|)
        """
        useful = self.useful_states()
        return useful.issubset(self._final_states_set())

    def prefix_closed_sublanguage(self: DFAType) -> DFAType:
        """
        Plus grand sous-langage préfixe-clos inclus dans L(self).

        Obtenu en rendant finaux tous les états utiles, puis en élaguant.

        Returns
        -------
        DFA
            Nouvel automate dont le langage est préfixe-clos.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        useful = self.useful_states()
        params = dict(self.input_parameters)
        if "final_states" in params:
            params["final_states"] = frozenset(useful)
        else:
            raise TypeError("prefix_closed_sublanguage: nécessite des final_states (pas GNFA).")
        result = self.__class__(**params)
        return result.trim()
