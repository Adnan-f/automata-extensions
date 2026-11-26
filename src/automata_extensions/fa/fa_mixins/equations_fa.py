"""EquationsMixin : système d'équations de langages associé à un automate (item 58)."""

from __future__ import annotations

from ...equations import EquationSystem


class EquationsMixin:
    """Lien entre automates et équations rationnelles."""

    def to_equations(self) -> EquationSystem:
        """
        Système d'équations de langages de l'automate (une inconnue ``X_q`` par état,
        ``X_q = Σ a·X_q' | ε``). ``.solve()`` le résout par le lemme d'Arden.

        Returns
        -------
        EquationSystem

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return EquationSystem.from_automaton(self)
