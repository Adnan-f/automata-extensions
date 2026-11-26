"""Analyse syntaxique d'expressions régulières (syntaxe d'automata-lib, sous-ensemble).

Grammaire ::

    union   := concat ('|' concat)*
    concat  := postfix*
    postfix := atom ('*' | '+' | '?')*
    atom    := '(' union ')' | '\\' caractère | caractère

``()`` et la chaîne vide dénotent ε. ``r+`` est développé en ``r r*`` et
``r?`` en ``ε | r``. Les opérateurs avancés d'automata-lib (``&``, ``.``,
``^``, ``{n,m}``...) ne sont pas supportés.
"""

from __future__ import annotations

from .ast import EPSILON, Concat, Regex, Star, Symbol, Union, concat, optional, plus

_POSTFIX = "*+?"
_STOP = "|)"


class RegexSyntaxError(ValueError):
    """Expression régulière mal formée."""


def parse(text: str) -> Regex:
    """
    Construit l'AST *brut* (non normalisé) d'une expression régulière.

    Appeler ``.simplify()`` sur le résultat pour obtenir la forme normale.

    Parameters
    ----------
    text : str
        Expression en syntaxe automata-lib (``|``, ``*``, ``+``, ``?``, ``()``).

    Returns
    -------
    Regex

    Raises
    ------
    RegexSyntaxError
        Parenthèses déséquilibrées, alternative vide, opérateur isolé...

    Complexity
    ----------
    O(n) pour n = len(text).
    """
    parser = _Parser(text)
    result = parser.parse_union()
    if parser.pos != len(text):
        raise RegexSyntaxError(f"')' inattendu en position {parser.pos}")
    return result


class _Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def peek(self):
        return self.text[self.pos] if self.pos < len(self.text) else None

    def parse_union(self) -> Regex:
        alternatives = [self.parse_concat()]
        while self.peek() == "|":
            self.pos += 1
            alternatives.append(self.parse_concat())
        if len(alternatives) == 1:
            return alternatives[0] if alternatives[0] is not None else EPSILON
        if any(a is None for a in alternatives):
            raise RegexSyntaxError("alternative vide autour de '|'")
        return Union(tuple(alternatives))

    def parse_concat(self):
        items = []
        while self.peek() is not None and self.peek() not in _STOP:
            items.append(self.parse_postfix())
        if not items:
            return None
        return items[0] if len(items) == 1 else Concat(tuple(items))

    def parse_postfix(self) -> Regex:
        node = self.parse_atom()
        while self.peek() is not None and self.peek() in _POSTFIX:
            op = self.text[self.pos]
            self.pos += 1
            if op == "*":
                node = Star(node)
            elif op == "+":
                node = Concat((node, Star(node)))
            else:
                node = Union((EPSILON, node))
        return node

    def parse_atom(self) -> Regex:
        ch = self.peek()
        if ch == "(":
            self.pos += 1
            inner = self.parse_union()
            if self.peek() != ")":
                raise RegexSyntaxError("parenthèse fermante manquante")
            self.pos += 1
            return inner
        if ch == "\\":
            self.pos += 1
            if self.peek() is None:
                raise RegexSyntaxError("échappement en fin d'expression")
            ch = self.text[self.pos]
            self.pos += 1
            return Symbol(ch)
        if ch in _POSTFIX:
            raise RegexSyntaxError(f"opérateur '{ch}' sans opérande (position {self.pos})")
        self.pos += 1
        return Symbol(ch)
