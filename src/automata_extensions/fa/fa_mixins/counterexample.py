"""CounterexampleMixin : plus court mot accepté, mot contre-exemple (§2.5 du cahier des charges).

Quand deux automates ne sont pas équivalents, ``distinguishing_word`` produit
un *témoin* : un mot que l'un accepte et pas l'autre. C'est la meilleure
explication d'un « non » : elle se vérifie à la main en quelques secondes.
"""

from __future__ import annotations

from collections import deque
from typing import Optional


def _coerce(fa):
    """Accepte aussi les DFA/NFA « purs » d'automata-lib en les convertissant."""
    from automata.fa.dfa import DFA
    from automata.fa.nfa import NFA

    from ..dfa import ExtendedDFA
    from ..nfa import ExtendedNFA

    if hasattr(fa, "_nondeterministic"):
        return fa
    if isinstance(fa, DFA):
        return ExtendedDFA(**fa.input_parameters)
    if isinstance(fa, NFA):
        return ExtendedNFA(**fa.input_parameters)
    raise TypeError(f"automate non supporté : {type(fa).__name__}")


def _as_dfa(fa):
    fa = _coerce(fa)
    from automata.fa.gnfa import GNFA

    if isinstance(fa, GNFA):
        raise TypeError("opération non définie pour un GNFA")
    return fa.determinize() if fa._nondeterministic else fa


def _extend_alphabet(dfa, alphabet):
    """DFA complet équivalent sur un alphabet plus grand (symboles ajoutés -> puits)."""
    if frozenset(alphabet) == frozenset(dfa.input_symbols):
        return dfa.complete()
    params = dict(dfa.input_parameters)
    params["input_symbols"] = frozenset(alphabet)
    params["allow_partial"] = True
    return dfa.__class__(**params).complete()


class CounterexampleMixin:
    """Plus court mot accepté et mot distinguant deux automates."""

    def shortest_word(self) -> Optional[str]:
        """
        Plus court mot accepté (le plus petit dans l'ordre longueur puis
        lexicographique), ou ``None`` si le langage est vide.

        Parcours en largeur de l'automate (déterminisé si besoin), symboles
        visités dans l'ordre : le premier chemin trouvé vers chaque état est
        le plus court et le plus petit lexicographiquement.

        Returns
        -------
        str or None

        Complexity
        ----------
        O(|Q| * |Sigma|) pour un DFA ; O(2^|Q|) dans le pire cas pour un NFA.
        """
        dfa = _as_dfa(self)
        finals = dfa.final_states
        parent = {dfa.initial_state: None}
        queue = deque([dfa.initial_state])
        while queue:
            state = queue.popleft()
            if state in finals:
                word = []
                while parent[state] is not None:
                    state, symbol = parent[state]
                    word.append(symbol)
                return "".join(reversed(word))
            row = dfa.transitions.get(state, {})
            for symbol in sorted(row):
                target = row[symbol]
                if target not in parent:
                    parent[target] = (state, symbol)
                    queue.append(target)
        return None

    def distinguishing_word(self, other) -> Optional[str]:
        """
        Plus court mot sur lequel ``self`` et ``other`` diffèrent (un seul des deux
        l'accepte), ou ``None`` si les deux automates sont équivalents.

        À longueur égale, le plus petit dans l'ordre lexicographique. Les
        alphabets peuvent différer : un symbole inconnu d'un automate le fait
        simplement rejeter. ``other`` peut être un DFA/NFA d'automata-lib
        « pur » ou un NFA (les deux sont déterminisés).

        Parameters
        ----------
        other : FA

        Returns
        -------
        str or None
            ``""`` (le mot vide) est un témoin valable.

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|) pour deux DFA.

        References
        ----------
        Hopcroft & Karp (1971) ; Hopcroft, Motwani, Ullman.
        """
        a, b = _as_dfa(self), _as_dfa(other)
        alphabet = frozenset(a.input_symbols) | frozenset(b.input_symbols)
        a, b = _extend_alphabet(a, alphabet), _extend_alphabet(b, alphabet)
        difference = a.product(
            b, is_final=lambda s1, s2: (s1 in a.final_states) != (s2 in b.final_states))
        return difference.shortest_word()
