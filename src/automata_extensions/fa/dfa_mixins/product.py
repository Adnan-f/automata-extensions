"""ProductMixin : produit synchronisé de deux DFA (item 23)."""

from __future__ import annotations

from typing import Callable, TypeVar

DFAType = TypeVar("DFAType")


class ProductMixin:
    """
    Produit synchronisé de deux DFA.

    Construction paresseuse : seuls les couples d'états accessibles depuis
    ``(self.initial_state, other.initial_state)`` sont créés (item 23 :
    « construction paresseuse des couples d'états accessibles »).
    """

    def product(
        self: DFAType,
        other: DFAType,
        is_final: Callable[[object, object], bool],
    ) -> DFAType:
        """
        Produit synchronisé général de deux DFA sur le même alphabet.

        ``is_final(s1, s2)`` décide si le couple d'états ``(s1, s2)`` est
        final dans le résultat : union, intersection et différence ne sont
        que des choix différents de cette fonction.

        Parameters
        ----------
        other : DFA
            Second automate. Doit partager l'alphabet de ``self``.
        is_final : callable
            Fonction ``(état de self, état de other) -> bool``.

        Returns
        -------
        DFA
            Nouveau DFA, construit uniquement sur les couples accessibles.

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        if self.input_symbols != other.input_symbols:
            raise ValueError("product: les deux automates doivent partager le même alphabet.")

        a = self.complete()
        b = other.complete()

        start = (a.initial_state, b.initial_state)
        transitions: dict = {}
        states = {start}
        queue = [start]
        head = 0
        while head < len(queue):
            s1, s2 = queue[head]
            head += 1
            row = {}
            for symbol in a.input_symbols:
                t1 = a.transitions[s1][symbol]
                t2 = b.transitions[s2][symbol]
                target = (t1, t2)
                row[symbol] = target
                if target not in states:
                    states.add(target)
                    queue.append(target)
            transitions[(s1, s2)] = row

        final_states = {pair for pair in states if is_final(pair[0], pair[1])}

        return self.__class__(
            states=frozenset(states),
            input_symbols=frozenset(a.input_symbols),
            transitions=transitions,
            initial_state=start,
            final_states=frozenset(final_states),
        )

    def intersection(self: DFAType, other: DFAType) -> DFAType:
        """
        Intersection des langages : L(self) ∩ L(other).

        Returns
        -------
        DFA

        Complexity
        ----------
        O(|Q1| * |Q2| * |Sigma|)
        """
        return self.product(other, is_final=lambda s1, s2: s1 in self.final_states
                             and s2 in other.final_states)
