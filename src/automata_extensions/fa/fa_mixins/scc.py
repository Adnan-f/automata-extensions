"""SCCMixin : composantes fortement connexes, algorithme de Tarjan (item 10)."""

from __future__ import annotations

from typing import Dict, FrozenSet, List

from ...utils.ordering import sort_states


class SCCMixin:
    """Composantes fortement connexes du graphe de transition."""

    def _scc_adjacency(self) -> Dict:
        """Successeurs directs de chaque état, triés (gère aussi les GNFA)."""
        from automata.fa.gnfa import GNFA

        adjacency = {}
        for state in self.states:
            if isinstance(self, GNFA):
                targets = {t for t, regex in self.transitions.get(state, {}).items()
                           if regex is not None}
            else:
                targets = set(self.successors_graph(state))
            adjacency[state] = sort_states(targets)
        return adjacency

    def strongly_connected_components(self) -> List[FrozenSet]:
        """
        Composantes fortement connexes de *tout* le graphe de transition (états
        inaccessibles compris), par l'algorithme de Tarjan (version itérative, donc
        sans limite de récursion).

        Deux états sont dans la même composante si chacun est atteignable depuis
        l'autre. Les composantes sont renvoyées dans l'ordre d'émission de Tarjan,
        qui est un **ordre topologique inverse** : si une transition va d'une
        composante A vers une composante B, alors B apparaît avant A.

        Returns
        -------
        list of frozenset
            Partition de l'ensemble des états.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Tarjan, « Depth-first search and linear graph algorithms » (1972).
        """
        adjacency = self._scc_adjacency()
        index: Dict = {}
        low: Dict = {}
        on_stack = set()
        stack: List = []
        components: List[FrozenSet] = []
        counter = 0

        for root in sort_states(self.states):
            if root in index:
                continue
            index[root] = low[root] = counter
            counter += 1
            stack.append(root)
            on_stack.add(root)
            work = [(root, iter(adjacency[root]))]
            while work:
                vertex, successors = work[-1]
                descended = False
                for nxt in successors:
                    if nxt not in index:
                        index[nxt] = low[nxt] = counter
                        counter += 1
                        stack.append(nxt)
                        on_stack.add(nxt)
                        work.append((nxt, iter(adjacency[nxt])))
                        descended = True
                        break
                    if nxt in on_stack:
                        low[vertex] = min(low[vertex], index[nxt])
                if descended:
                    continue
                work.pop()
                if work:
                    parent = work[-1][0]
                    low[parent] = min(low[parent], low[vertex])
                if low[vertex] == index[vertex]:
                    component = set()
                    while True:
                        member = stack.pop()
                        on_stack.discard(member)
                        component.add(member)
                        if member == vertex:
                            break
                    components.append(frozenset(component))
        return components

    def is_strongly_connected(self) -> bool:
        """
        Vrai si tous les états sont mutuellement atteignables (une seule composante).

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return len(self.strongly_connected_components()) == 1
