"""Lemme d'Arden et systèmes d'équations de langages (items 57, 58).

Un système (linéaire à droite) associe à chaque variable ``X_i`` une équation ::

    X_i = A_i1 X_1 | A_i2 X_2 | ... | B_i

où les coefficients ``A_ij`` et les constantes ``B_i`` sont des expressions
régulières. Pour un automate, ``X_q`` désigne le langage des mots menant de ``q``
à un état final : ``X_q = Σ a·X_q' (pour chaque transition) | ε (si q est final)``.

Le lemme d'Arden résout une équation à une inconnue : ``X = A X | B`` a pour plus
petite solution ``X = A* B`` (et c'est l'unique solution si ``A`` ne contient pas ε).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Hashable, Mapping, Optional, Sequence, Tuple

from .regex.ast import EMPTY, EPSILON, Regex, concat, star, union
from .utils.ordering import sort_states, state_label

_CONST = object()


def arden(a: Regex, b: Regex) -> Regex:
    """
    Plus petite solution de ``X = A X | B`` : ``A* B`` (lemme d'Arden).

    Parameters
    ----------
    a, b : Regex
        Coefficient et terme constant (expressions de ``automata_extensions.regex``).

    Returns
    -------
    Regex
        ``A* B`` normalisée. Si ``A`` est ``∅``, la solution est simplement ``B``.

    Complexity
    ----------
    O(taille de a + taille de b)
    """
    return concat(star(a), b)


@dataclass(frozen=True, eq=False)
class EquationSystem:
    """
    Système d'équations ``X_i = ⋃_j A_ij X_j ∪ B_i`` sur des expressions régulières.

    Attributes
    ----------
    variables : tuple
        Les inconnues (n'importe quels objets hachables, ex. des états d'automate).
    coefficients : dict
        ``(i, j) -> A_ij`` ; une paire absente vaut ``∅``.
    constants : dict
        ``i -> B_i`` ; une variable absente a la constante ``∅``.
    """

    variables: Tuple[Hashable, ...]
    coefficients: Mapping[Tuple[Hashable, Hashable], Regex]
    constants: Mapping[Hashable, Regex]

    @classmethod
    def from_automaton(cls, fa) -> "EquationSystem":
        """
        Système associé à un DFA/NFA : une inconnue par état, ``X_q = Σ a·X_q' | ε``
        (ε en terme constant si ``q`` est final ; ε-transition : coefficient ``ε``).

        Complexity
        ----------
        O(|Q| + |E|)
        """
        from automata.fa.gnfa import GNFA
        from .regex.ast import Symbol

        if isinstance(fa, GNFA):
            raise TypeError("pas de système d'équations associé à un GNFA")
        coefficients: Dict = {}
        for p, row in fa.transitions.items():
            for symbol, target in row.items():
                label = EPSILON if symbol == "" else Symbol(symbol)
                for q in (target if fa._nondeterministic else {target}):
                    coefficients[(p, q)] = union(coefficients.get((p, q), EMPTY), label)
        constants = {f: EPSILON for f in fa._final_states_set()}
        return cls(tuple(sort_states(fa.states)), coefficients, constants)

    def __str__(self) -> str:
        """Une équation par ligne, ex. ``X0 = bX0 | aX1 | ε``."""
        lines = []
        for i in self.variables:
            terms = []
            for j in self.variables:
                coefficient = self.coefficients.get((i, j))
                if coefficient is None or coefficient == EMPTY:
                    continue
                text = "" if coefficient == EPSILON else str(coefficient)
                if "|" in text:
                    text = f"({text})"
                terms.append(f"{text}X{state_label(j)}")
            constant = self.constants.get(i, EMPTY)
            if constant != EMPTY:
                terms.append("ε" if constant == EPSILON else str(constant))
            lines.append(f"X{state_label(i)} = {' | '.join(terms) if terms else '∅'}")
        return "\n".join(lines)

    def solve(self, order: Optional[Sequence[Hashable]] = None) -> Dict[Hashable, Regex]:
        """
        Résout le système : une expression régulière pour *chaque* inconnue.

        Méthode : on élimine les inconnues une à une dans l'ordre ``order`` (Arden
        pour retirer l'auto-référence, puis substitution dans les autres équations),
        puis on remonte (substitution arrière) pour exprimer chaque inconnue sans
        variable. Le résultat est la plus petite solution ; l'ordre d'élimination
        change l'écriture, jamais le langage.

        Parameters
        ----------
        order : sequence, optional
            Permutation de ``variables`` (par défaut, leur ordre).

        Returns
        -------
        dict
            ``variable -> Regex``.

        Raises
        ------
        ValueError
            Si ``order`` n'est pas une permutation des variables.

        Complexity
        ----------
        O(n^3) opérations sur des expressions (la taille des expressions peut
        croître exponentiellement dans le pire cas).

        References
        ----------
        Lemme d'Arden ; Hopcroft, Motwani, Ullman.
        """
        order = list(self.variables if order is None else order)
        if set(order) != set(self.variables) or len(order) != len(self.variables):
            raise ValueError("order doit être une permutation des variables")

        equations: Dict = {i: {} for i in self.variables}
        for (i, j), coefficient in self.coefficients.items():
            equations[i][j] = coefficient
        for i, constant in self.constants.items():
            equations[i][_CONST] = constant

        expressions: Dict = {}                 # variable éliminée -> équation (sur variables restantes)
        for k in order:
            equation = equations.pop(k)
            star_self = star(equation.pop(k, EMPTY))
            resolved = {j: concat(star_self, c) for j, c in equation.items()}
            expressions[k] = resolved
            for other in equations.values():
                c_to_k = other.pop(k, None)
                if c_to_k is None:
                    continue
                for j, c in resolved.items():
                    other[j] = union(other.get(j, EMPTY), concat(c_to_k, c))

        solution: Dict = {}
        for k in reversed(order):              # substitution arrière
            total = EMPTY
            for j, c in expressions[k].items():
                total = union(total, c if j is _CONST else concat(c, solution[j]))
            solution[k] = total
        return solution
