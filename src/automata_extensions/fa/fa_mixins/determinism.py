"""DeterminismMixin : test de déterminisme (item 33)."""

from __future__ import annotations


class DeterminismMixin:
    """Un automate est déterministe s'il n'a ni ε-transition ni choix multiple."""

    def is_deterministic(self) -> bool:
        """
        Teste si la fonction de transition est déterministe.

        Vrai si, pour chaque état et chaque symbole, il y a au plus une
        transition, et aucune ε-transition. Un DFA (même partiel) l'est
        toujours ; un NFA l'est s'il n'a ni ε-transition ni ensemble cible de
        plus d'un état ; un GNFA ne l'est jamais (transitions étiquetées par
        des expressions régulières).

        Returns
        -------
        bool

        Complexity
        ----------
        O(|E|)
        """
        from automata.fa.gnfa import GNFA

        if isinstance(self, GNFA):
            return False
        if not self._nondeterministic:
            return True
        for row in self.transitions.values():
            if "" in row and row[""]:
                return False
            if any(len(targets) > 1 for targets in row.values()):
                return False
        return True
