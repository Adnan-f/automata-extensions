"""SyntacticMonoidMixin : monoïde syntaxique et de transitions (item 62)."""

from __future__ import annotations

from ...algebra.monoid import TransitionMonoid


class SyntacticMonoidMixin:
    """Monoïde syntaxique du langage et test « sans étoile » (Schützenberger)."""

    def transition_monoid(self) -> TransitionMonoid:
        """
        Monoïde de transitions de ce DFA (complété, états accessibles seulement).

        Complexity
        ----------
        O(|M| * |Sigma| * |Q|), |M| = taille du monoïde.
        """
        c = self.complete()
        c = c.induced_subautomaton(c.accessible_states())
        states = sorted(c.states, key=str)
        return TransitionMonoid.from_dfa_table(states, c.input_symbols, c.transitions)

    def syntactic_monoid(self) -> TransitionMonoid:
        """
        Monoïde syntaxique du langage = monoïde de transitions du DFA minimal.

        Ses éléments sont les classes de mots indiscernables *en contexte*
        (``u ~ v`` ssi ``xuy ∈ L ⇔ xvy ∈ L`` pour tous ``x, y``).

        Returns
        -------
        TransitionMonoid
            ``len(...)`` donne le nombre de classes ; les états du monoïde
            sont les classes de Myhill-Nerode.

        Complexity
        ----------
        O(|Q|^2 * |Sigma| + |M| * |Sigma| * |Q|)

        References
        ----------
        Pin, « Mathematical Foundations of Automata Theory ».
        """
        c = self.complete()
        c = c.induced_subautomaton(c.accessible_states())
        classes = c.equivalence_classes()
        class_of = {s: cls for cls in classes for s in cls}
        states = sorted(classes, key=lambda cls: sorted(map(str, cls)))
        delta = {
            cls: {a: class_of[c.transitions[next(iter(cls))][a]] for a in c.input_symbols}
            for cls in classes
        }
        return TransitionMonoid.from_dfa_table(states, c.input_symbols, delta)

    def is_star_free(self) -> bool:
        """
        Teste si le langage est *sans étoile* (exprimable avec union,
        concaténation et complément, sans étoile de Kleene).

        Théorème de Schützenberger : équivalent à l'apériodicité du monoïde
        syntaxique.

        Complexity
        ----------
        Celle de ``syntactic_monoid`` + ``is_aperiodic``.
        """
        return self.syntactic_monoid().is_aperiodic()
