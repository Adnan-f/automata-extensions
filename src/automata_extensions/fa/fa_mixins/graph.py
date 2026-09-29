"""GraphMixin : voisinage direct dans le graphe de transition (indépendant du symbole)."""

from __future__ import annotations

from typing import AbstractSet


class GraphMixin:
    """
    Vue « graphe » d'un automate : successeurs et prédécesseurs directs d'un état.

    Nommées ``*_graph`` (et non ``predecessors``/``successors``) pour ne pas
    entrer en collision avec ``DFA.predecessors``/``successors`` d'automata-lib,
    qui portent sur des *mots*, pas des états.
    """

    def successors_graph(self, state) -> AbstractSet:
        """
        États atteignables en une transition depuis ``state``, tout symbole confondu.

        Parameters
        ----------
        state
            État de départ.

        Returns
        -------
        set
            Ensemble des états cibles directs.

        Complexity
        ----------
        O(|Sigma|) pour un DFA, O(somme des tailles des ensembles cibles) pour un NFA.

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        result = set()
        row = self.transitions.get(state, {})
        for target in row.values():
            if self._nondeterministic:
                result.update(target)
            else:
                result.add(target)
        return result


    def predecessors_graph(self, state) -> AbstractSet:
        """
        États ayant une transition directe vers ``state``, tout symbole confondu.

        Parameters
        ----------
        state
            État d'arrivée.

        Returns
        -------
        set
            Ensemble des états sources directs.

        Complexity
        ----------
        O(|Q| * |Sigma|) : on parcourt toutes les transitions de l'automate.

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        result = set()
        for source, row in self.transitions.items():
            for target in row.values():
                targets = target if self._nondeterministic else {target}
                if state in targets:
                    result.add(source)
        return result