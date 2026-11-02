"""Monoïde de transitions / monoïde syntaxique d'un DFA (item 62).

Un mot ``w`` agit sur les états d'un DFA complet par la transformation
``q -> delta*(q, w)``. L'ensemble de ces transformations, muni de la
composition, est le *monoïde de transitions* ; pour le DFA minimal, c'est le
*monoïde syntaxique* du langage.

Convention : ``multiply(f, g)`` est « f puis g » (le mot ``uv`` agit comme
``multiply(element(u), element(v))``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, List, Mapping, Sequence, Tuple

Element = Tuple[int, ...]


@dataclass(frozen=True, eq=False)
class TransitionMonoid:
    """
    Monoïde fini de transformations d'un ensemble ordonné d'états.

    Attributes
    ----------
    states : tuple
        États du DFA, dans l'ordre qui indexe les transformations.
    alphabet : tuple of str
        Symboles, triés.
    elements : dict
        Transformation -> plus court mot (ordre longueur puis lexicographique)
        qui l'induit. L'identité correspond au mot vide.
    """

    states: Tuple
    alphabet: Tuple[str, ...]
    elements: Mapping[Element, str]
    _generators: Mapping[str, Element]

    # ---- construction ---------------------------------------------------
    @classmethod
    def from_dfa_table(cls, states: Sequence, alphabet: Sequence[str],
                       delta: Mapping) -> "TransitionMonoid":
        """
        Construit le monoïde par parcours en largeur depuis l'identité.

        Parameters
        ----------
        states : sequence
            États (DFA *complet*), dans un ordre fixé.
        alphabet : sequence of str
            Symboles.
        delta : mapping
            ``delta[state][symbol] -> state``.

        Complexity
        ----------
        O(|M| * |Sigma| * |Q|) où |M| est la taille du monoïde (qui peut
        atteindre |Q|^|Q| dans le pire cas).
        """
        states = tuple(states)
        alphabet = tuple(sorted(alphabet))
        index = {s: i for i, s in enumerate(states)}
        generators = {
            a: tuple(index[delta[s][a]] for s in states) for a in alphabet
        }
        identity = tuple(range(len(states)))
        elements: Dict[Element, str] = {identity: ""}
        queue = [identity]
        head = 0
        while head < len(queue):
            current = queue[head]
            head += 1
            for a in alphabet:
                nxt = tuple(generators[a][i] for i in current)   # current puis a
                if nxt not in elements:
                    elements[nxt] = elements[current] + a
                    queue.append(nxt)
        return cls(states, alphabet, elements, generators)

    # ---- structure ------------------------------------------------------
    @property
    def identity(self) -> Element:
        """Transformation identité (mot vide)."""
        return tuple(range(len(self.states)))

    def __len__(self) -> int:
        return len(self.elements)

    def __contains__(self, element) -> bool:
        return element in self.elements

    def __iter__(self) -> Iterator[Element]:
        """Éléments par plus court mot croissant (longueur, puis lexicographique)."""
        return iter(sorted(self.elements, key=lambda e: (len(self.elements[e]), self.elements[e])))

    def shortest_word(self, element: Element) -> str:
        """Plus court mot induisant ``element``."""
        return self.elements[element]

    def element_of(self, word: str) -> Element:
        """Transformation induite par ``word``."""
        current = self.identity
        for a in word:
            if a not in self._generators:
                raise ValueError(f"symbole hors alphabet : {a!r}")
            current = tuple(self._generators[a][i] for i in current)
        return current

    @staticmethod
    def multiply(f: Element, g: Element) -> Element:
        """Composition « f puis g »."""
        return tuple(g[i] for i in f)

    # ---- propriétés algébriques ----------------------------------------
    def is_commutative(self) -> bool:
        """
        Vrai si ``fg = gf`` pour tous éléments. Il suffit de le vérifier sur
        les générateurs (les lettres).

        Complexity
        ----------
        O(|Sigma|^2 * |Q|)
        """
        gens = list(self._generators.values())
        return all(self.multiply(f, g) == self.multiply(g, f) for f in gens for g in gens)

    def idempotents(self) -> List[Element]:
        """Éléments ``e`` tels que ``e e = e``, par plus court mot croissant."""
        return [e for e in self if self.multiply(e, e) == e]

    def is_group(self) -> bool:
        """Vrai si tous les éléments sont des permutations (le monoïde est un groupe)."""
        n = len(self.states)
        return all(len(set(e)) == n for e in self.elements)

    def is_aperiodic(self) -> bool:
        """
        Vrai si pour tout ``x`` il existe ``m`` avec ``x^m = x^(m+1)``
        (aucun sous-groupe non trivial).

        Par le théorème de Schützenberger, le langage est *sans étoile*
        (star-free) si et seulement si son monoïde syntaxique est apériodique.

        Complexity
        ----------
        O(|M| * |M| * |Q|) dans le pire cas.
        """
        for x in self.elements:
            seen: Dict[Element, int] = {}
            current, step = x, 1
            while current not in seen:
                seen[current] = step
                current = self.multiply(current, x)
                step += 1
            if step - seen[current] != 1:        # période > 1
                return False
        return True

    def __repr__(self) -> str:
        return f"TransitionMonoid({len(self)} éléments, {len(self.states)} états)"
