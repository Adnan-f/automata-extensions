"""IsomorphismMixin : test d'isomorphisme entre deux DFA (item 26)."""

from __future__ import annotations


class IsomorphismMixin:
    """
    Isomorphisme d'automates : existence d'une bijection entre états qui
    préserve exactement la structure (plus fort que l'équivalence de langage).
    """

    def is_isomorphic_to(self, other) -> bool:
        """
        Teste l'existence d'un isomorphisme d'automates entre ``self`` et ``other``.

        Recherche par backtracking sur les couples d'états accessibles en
        parallèle depuis les deux états initiaux (BFS synchronisé) : à
        chaque étape le mapping est déterminé de façon unique par la
        structure, donc pas de véritable recherche combinatoire tant que
        les deux automates sont déterministes et complets sur les mêmes
        symboles.

        Parameters
        ----------
        other : DFA

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| * |Sigma|)
        """
        a = self.complete()
        b = other.complete()
        if len(a.states) != len(b.states):
            return False
        if a.input_symbols != b.input_symbols:
            return False

        mapping = {a.initial_state: b.initial_state}
        reverse = {b.initial_state: a.initial_state}
        queue = [(a.initial_state, b.initial_state)]
        head = 0
        while head < len(queue):
            sa, sb = queue[head]
            head += 1
            if (sa in a.final_states) != (sb in b.final_states):
                return False
            for symbol in a.input_symbols:
                ta = a.transitions[sa][symbol]
                tb = b.transitions[sb][symbol]
                if ta in mapping:
                    if mapping[ta] != tb:
                        return False
                elif tb in reverse:
                    return False
                else:
                    mapping[ta] = tb
                    reverse[tb] = ta
                    queue.append((ta, tb))
        return len(mapping) == len(a.states)
