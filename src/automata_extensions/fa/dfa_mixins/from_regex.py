"""FromRegexMixin : regex -> DFA direct, par dérivées de Brzozowski (item 49)."""

from __future__ import annotations

from typing import Iterable, Optional, Union as TypingUnion

from ...regex.ast import Regex
from ...regex.parser import parse


class FromRegexMixin:
    """Construction directe d'un DFA complet à partir d'une expression régulière."""

    @classmethod
    def from_regex(
        cls,
        regex: TypingUnion[str, Regex],
        *,
        input_symbols: Optional[Iterable[str]] = None,
    ):
        """
        DFA reconnaissant le langage de ``regex``, sans passer par un NFA.

        Parameters
        ----------
        regex : str or Regex
            Expression (texte ou AST).
        input_symbols : iterable of str, optional
            Alphabet ; par défaut, les symboles présents dans ``regex``.

        Returns
        -------
        DFA
            Automate des dérivées (complet ; l'état puits est ``∅``).

        Complexity
        ----------
        O(n * |Sigma|) dérivées, n = nombre de dérivées distinctes.

        References
        ----------
        Brzozowski (1964).
        """
        tree = parse(regex) if isinstance(regex, str) else regex
        built = tree.to_dfa(input_symbols)
        if cls.__name__ == type(built).__name__:
            return built
        return cls(**built.input_parameters)
