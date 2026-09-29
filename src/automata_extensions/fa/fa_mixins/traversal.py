"""TraversalMixin : parcours BFS/DFS du graphe de transition."""

from __future__ import annotations

from typing import List, Optional


class TraversalMixin:
    """Parcours en largeur (BFS) et en profondeur (DFS) d'un automate."""

    def bfs(self, start=None) -> List:
        """
        Parcours en largeur depuis ``start`` (état initial par défaut).

        Parameters
        ----------
        start : optionnel
            État de départ. Si omis, ``self.initial_state``.

        Returns
        -------
        list
            États dans l'ordre de découverte BFS.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest, Stein — Introduction to Algorithms.
        """
        start = self.initial_state if start is None else start
        visited = {start}
        order = [start]
        queue = [start]
        head = 0
        while head < len(queue):
            current = queue[head]
            head += 1
            for succ in sorted(self.successors_graph(current), key=str):
                if succ not in visited:
                    visited.add(succ)
                    order.append(succ)
                    queue.append(succ)
        return order

    def dfs(self, start=None, *, recursive: bool = False) -> List:
        """
        Parcours en profondeur depuis ``start`` (état initial par défaut).

        Parameters
        ----------
        start : optionnel
            État de départ. Si omis, ``self.initial_state``.
        recursive : bool
            Si ``True``, utilise une implémentation récursive plutôt qu'une
            pile explicite. Les deux versions existent pour l'aspect
            pédagogique (cf. cahier des charges, item 1).

        Returns
        -------
        list
            États dans l'ordre de découverte DFS.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest, Stein — Introduction to Algorithms.
        """
        start = self.initial_state if start is None else start
        if recursive:
            visited: set = set()
            order: List = []

            def visit(state) -> None:
                visited.add(state)
                order.append(state)
                for succ in sorted(self.successors_graph(state), key=str):
                    if succ not in visited:
                        visit(succ)

            visit(start)
            return order

        visited = {start}
        order = [start]
        stack = [iter(sorted(self.successors_graph(start), key=str))]
        path = [start]
        while stack:
            try:
                succ = next(stack[-1])
            except StopIteration:
                stack.pop()
                path.pop()
                continue
            if succ not in visited:
                visited.add(succ)
                order.append(succ)
                path.append(succ)
                stack.append(iter(sorted(self.successors_graph(succ), key=str)))
        return order

    def reachable_states(self, start=None) -> set:
        """
        États atteignables depuis ``start`` (état initial par défaut).

        Généralise ``accessible_states`` (qui part toujours de l'état initial)
        à un état de départ quelconque.

        Parameters
        ----------
        start : optionnel
            État de départ.

        Returns
        -------
        set
            États atteignables.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return set(self.bfs(start))