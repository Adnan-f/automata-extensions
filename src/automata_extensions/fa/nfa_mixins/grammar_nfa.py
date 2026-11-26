"""GrammarNFAMixin : grammaire régulière -> NFA."""

from __future__ import annotations

from typing import Optional

from ...grammar.grammar import Grammar


class GrammarNFAMixin:
    """Constructeurs ``from_grammar`` et ``from_grammar_string``."""

    @classmethod
    def from_grammar(cls, grammar: Grammar):
        """
        NFA reconnaissant le langage d'une grammaire régulière (à droite ou à gauche).

        Raises
        ------
        ValueError
            Si la grammaire n'est pas régulière.

        Complexity
        ----------
        O(|P| * longueur maximale d'un membre droit)
        """
        return grammar.to_nfa(cls)

    @classmethod
    def from_grammar_string(cls, text: str, start: Optional[str] = None):
        """
        NFA d'une grammaire écrite en texte, ex. ``"S -> aS | b"``
        (voir ``Grammar.from_string`` pour le format).

        Complexity
        ----------
        O(taille du texte)
        """
        return cls.from_grammar(Grammar.from_string(text, start))
