"""ThompsonMixin : construction de Thompson regex -> NFA (item 51)."""

from __future__ import annotations

from typing import Dict, Iterable, Optional, Set, Tuple, Union as TypingUnion

from ...regex.ast import (Concat, Empty, Epsilon, Regex, Star, Symbol, Union)
from ...regex.parser import parse


class ThompsonMixin:
    """
    ``from_regex`` par la construction de Thompson, rendue explicite pour
    pouvoir l'illustrer pas à pas (chaque opérateur ajoute des états et des
    ε-transitions, jamais plus de 2 transitions sortantes par état).

    Surcharge ``NFA.from_regex`` d'automata-lib (qui construit l'automate
    autrement) ; ne supporte que ``| * + ? ()`` et l'échappement ``\\``.
    """

    @classmethod
    def from_regex(
        cls,
        regex: TypingUnion[str, Regex],
        *,
        input_symbols: Optional[Iterable[str]] = None,
    ):
        """
        NFA de Thompson reconnaissant le langage de ``regex``.

        Parameters
        ----------
        regex : str or Regex
            Expression (texte ou AST).
        input_symbols : iterable of str, optional
            Alphabet ; par défaut, les symboles présents dans ``regex``.

        Returns
        -------
        NFA
            Automate à ε-transitions ; états nommés ``q0, q1, ...``.
            Il a exactement un état final et 2n états au plus (n = taille
            de l'expression).

        Complexity
        ----------
        O(n) états et transitions.

        References
        ----------
        Thompson (1968) ; Hopcroft, Motwani, Ullman.
        """
        tree = parse(regex) if isinstance(regex, str) else regex
        alphabet = frozenset(input_symbols) if input_symbols is not None else tree.symbols()
        missing = tree.symbols() - alphabet
        if missing:
            raise ValueError(f"symboles hors alphabet : {sorted(missing)}")

        counter = [0]
        transitions: Dict[str, Dict[str, Set[str]]] = {}

        def fresh() -> str:
            name = f"q{counter[0]}"
            counter[0] += 1
            transitions[name] = {}
            return name

        def add(src: str, symbol: str, dst: str) -> None:
            transitions[src].setdefault(symbol, set()).add(dst)

        def build(node: Regex) -> Tuple[str, str]:
            if isinstance(node, Symbol):
                s, e = fresh(), fresh()
                add(s, node.char, e)
                return s, e
            if isinstance(node, Epsilon):
                s, e = fresh(), fresh()
                add(s, "", e)
                return s, e
            if isinstance(node, Empty):
                return fresh(), fresh()
            if isinstance(node, Union):
                s = fresh()
                parts = [build(item) for item in node.items]
                e = fresh()
                for ps, pe in parts:
                    add(s, "", ps)
                    add(pe, "", e)
                return s, e
            if isinstance(node, Concat):
                parts = [build(item) for item in node.items]
                for (_, e1), (s2, _) in zip(parts, parts[1:]):
                    add(e1, "", s2)
                return parts[0][0], parts[-1][1]
            if isinstance(node, Star):
                s = fresh()
                ps, pe = build(node.inner)
                e = fresh()
                add(s, "", ps)
                add(s, "", e)
                add(pe, "", ps)
                add(pe, "", e)
                return s, e
            raise TypeError(node)

        start, end = build(tree)
        return cls(
            states=frozenset(transitions),
            input_symbols=alphabet,
            transitions={
                s: {a: frozenset(t) for a, t in row.items()} for s, row in transitions.items()
            },
            initial_state=start,
            final_states=frozenset({end}),
        )
