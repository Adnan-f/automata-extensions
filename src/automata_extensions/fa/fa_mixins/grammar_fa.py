"""GrammarMixin : automate -> grammaire régulière, dérivation d'un mot (item 55)."""

from __future__ import annotations

from typing import Dict

from ...grammar.grammar import DerivationStep, Grammar, Production


class GrammarMixin:
    """Association états/non-terminaux et transitions/règles."""

    def _grammar_names(self) -> Dict:
        """Nom de non-terminal unique pour chaque état (disjoint de l'alphabet)."""
        taken = set(self.input_symbols)
        names = {}
        for state in sorted(self.states, key=str):
            name = str(state)
            while name in taken:
                name += "'"
            taken.add(name)
            names[state] = name
        return names

    def to_grammar(self) -> Grammar:
        """
        Grammaire régulière linéaire à droite équivalente.

        Chaque état q devient un non-terminal ; une transition ``p --a--> q``
        devient la règle ``p -> a q`` (une ε-transition ``p -> q``) ; un état
        final f donne la règle ``f -> ε``. L'axiome est l'état initial.

        Returns
        -------
        Grammar

        Raises
        ------
        TypeError
            Pour un GNFA (transitions étiquetées par des regex).

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        from automata.fa.gnfa import GNFA

        # NB : GNFA expose aussi une propriété ``final_states`` en 9.2.0, donc
        # tester hasattr(self, "final_states") ne suffit pas à l'exclure.
        if isinstance(self, GNFA):
            raise TypeError("to_grammar n'est pas défini pour un GNFA")
        names = self._grammar_names()
        productions = set()
        for p, row in self.transitions.items():
            for symbol, target in row.items():
                targets = target if self._nondeterministic else {target}
                for q in targets:
                    rhs = (names[q],) if symbol == "" else (symbol, names[q])
                    productions.add(Production(names[p], rhs))
        for f in self.final_states:
            productions.add(Production(names[f], ()))
        return Grammar(frozenset(names.values()), frozenset(self.input_symbols),
                       productions, names[self.initial_state])

    def to_left_grammar(self) -> Grammar:
        """
        Grammaire régulière linéaire à gauche équivalente.

        Obtenue en renversant la grammaire à droite de l'automate miroir.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        return self.reverse().to_grammar().reverse()

    def derivation_tree(self, word: str) -> DerivationStep:
        """
        Dérivation de ``word`` dans la grammaire de l'automate (dernière étape).

        ``.sequence()`` donne par exemple ``0 => a1 => aa2 => aaa0 => aaa`` ;
        ``.word()`` redonne le mot ; ``.parse_tree()`` l'arbre associé.

        Raises
        ------
        NotDerivableError
            Si le mot n'est pas accepté par l'automate.

        Complexity
        ----------
        O(|E| * |mot|^2)
        """
        return self.to_grammar().derive(word)
