"""CompletenessMixin : test et ajout de la complétude d'un DFA."""

from __future__ import annotations

from typing import TypeVar

DFAType = TypeVar("DFAType")

_DEFAULT_TRAP = "__trap__"


class CompletenessMixin:
    """
    Complétude d'un DFA : chaque état doit avoir une transition sortante
    par symbole de l'alphabet (item 20-21 du cahier des charges).
    """

    def is_complete(self) -> bool:
        """
        Teste si la fonction de transition est totale.

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| * |Sigma|)
        """
        for state in self.states:
            row = self.transitions.get(state, {})
            for symbol in self.input_symbols:
                if symbol not in row:
                    return False
        return True

    def complete(self: DFAType, trap_name=_DEFAULT_TRAP) -> DFAType:
        """
        Complète le DFA : ajoute un état puits si nécessaire.

        L'état puits reçoit toutes les transitions manquantes et boucle sur
        lui-même pour chaque symbole. Ne modifie jamais ``self``.

        Parameters
        ----------
        trap_name
            Nom du nouvel état puits, s'il faut en créer un. Un suffixe est
            ajouté si ce nom est déjà pris.

        Returns
        -------
        DFA
            Nouveau DFA complet.

        Complexity
        ----------
        O(|Q| * |Sigma|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        if self.is_complete():
            params = dict(self.input_parameters)
            if "allow_partial" in params:
                params["allow_partial"] = False
            return self.__class__(**params)

        trap = trap_name
        existing = set(self.states)
        suffix = 0
        while trap in existing:
            suffix += 1
            trap = f"{trap_name}_{suffix}"

        new_states = existing | {trap}
        new_transitions = {
            state: dict(row) for state, row in self.transitions.items()
        }
        for state in new_states:
            row = new_transitions.setdefault(state, {})
            for symbol in self.input_symbols:
                if symbol not in row:
                    row[symbol] = trap

        params = dict(self.input_parameters)
        params["states"] = frozenset(new_states)
        params["transitions"] = new_transitions
        if "allow_partial" in params:
            params["allow_partial"] = False
        return self.__class__(**params)
