"""CycleMixin : détection de cycles, vacuité et finitude du langage."""

from __future__ import annotations


class CycleMixin:
    """Détection de cycle (global ou depuis un état) et décision vide/fini."""

    def has_cycle_from(self, state) -> bool:
        """
        Teste l'existence d'un cycle dans le sous-graphe accessible depuis ``state``.

        DFS avec distinction des couleurs blanc/gris/noir : un cycle existe
        ssi on rencontre une arête de retour (vers un état gris, càd en cours
        de visite dans la pile d'appel courante).

        Parameters
        ----------
        state
            État de départ.

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest, Stein — Introduction to Algorithms.
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {s: WHITE for s in self.states}
        stack = [(state, iter(sorted(self.successors_graph(state), key=str)))]
        color[state] = GRAY
        while stack:
            current, it = stack[-1]
            advanced = False
            for succ in it:
                if color.get(succ, WHITE) == GRAY:
                    return True
                if color.get(succ, WHITE) == WHITE:
                    color[succ] = GRAY
                    stack.append((succ, iter(sorted(self.successors_graph(succ), key=str))))
                    advanced = True
                    break
            if not advanced:
                color[current] = BLACK
                stack.pop()
        return False

    def has_cycle(self) -> bool:
        """
        Teste l'existence d'un cycle accessible depuis l'état initial.

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return self.has_cycle_from(self.initial_state)

    def is_empty(self) -> bool:
        """
        Teste si le langage reconnu est vide.

        Un langage est vide ssi aucun état accessible n'est accepteur
        (approche indépendante de ``DFA.isempty`` d'automata-lib : ici on
        raisonne uniquement sur le graphe).

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return not (self.accessible_states() & self._final_states_set())

    def is_finite(self) -> bool:
        """
        Teste si le langage reconnu est fini.

        Le langage est infini ssi il existe un cycle passant par un état à
        la fois accessible et coaccessible (un tel cycle peut être « pompé »
        indéfiniment tout en restant sur un chemin acceptant).

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| + |E|)
        """
        if self.is_empty():
            return True
        useful = self.useful_states()
        if not useful:
            return True
        sub = self.induced_subautomaton(useful)
        return not sub.has_cycle()