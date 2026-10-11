"""AST d'expressions régulières : normalisation, dérivées de Brzozowski, positions.

Les nœuds sont immuables et hachables. Les *constructeurs intelligents*
(``union``, ``concat``, ``star``) maintiennent une forme normale :

* l'union est aplatie, sans doublon, triée (associativité, commutativité,
  idempotence : « similarité » de Brzozowski, qui garantit un nombre fini de
  dérivées) ;
* ``∅`` est absorbant pour la concaténation et neutre pour l'union ;
* ``ε`` est neutre pour la concaténation ; ``(ε|r)* = r*`` ; ``r** = r*``.

Syntaxe d'affichage (celle d'automata-lib) : ``|``, ``*``, ``?``, ``()`` pour ε.
Le langage vide s'affiche ``∅`` (non exprimable en syntaxe automata-lib).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, Optional, Set, Tuple

_SPECIAL = set("|*+?()\\")


class Regex:
    """Classe de base des nœuds d'expression régulière."""

    __slots__ = ()

    # ---- sémantique -----------------------------------------------------
    def nullable(self) -> bool:
        """
        Teste si ε appartient au langage dénoté.

        Complexity
        ----------
        O(taille de l'expression)
        """
        raise NotImplementedError

    def derivative(self, symbol: str) -> "Regex":
        """
        Dérivée de Brzozowski par ``symbol`` : quotient à gauche a^{-1}L.

        Le résultat est normalisé (forme normale de similarité).

        Complexity
        ----------
        O(taille de l'expression) par appel (plus le coût de normalisation).

        References
        ----------
        Brzozowski, « Derivatives of Regular Expressions » (1964).
        """
        raise NotImplementedError

    def symbols(self) -> FrozenSet[str]:
        """Ensemble des symboles apparaissant dans l'expression."""
        raise NotImplementedError

    def size(self) -> int:
        """Nombre de nœuds de l'arbre."""
        raise NotImplementedError

    def simplify(self) -> "Regex":
        """
        Forme normale : applique les constructeurs intelligents de bas en haut.

        Complexity
        ----------
        O(taille * log taille)
        """
        current = self
        for _ in range(8):
            nxt = current._simplify_once()
            if nxt == current:
                return nxt
            current = nxt
        return current

    def _simplify_once(self) -> "Regex":
        return self

    # ---- affichage ------------------------------------------------------
    def __str__(self) -> str:
        return _fmt(self, 0)

    # ---- conversions ----------------------------------------------------
    def to_dfa(self, input_symbols: Optional[Iterable[str]] = None):
        """
        DFA complet équivalent, par l'automate des dérivées de Brzozowski.

        Les états sont les dérivées successives (nommées par leur écriture).

        Complexity
        ----------
        O(n * |Sigma|) dérivées, n = nombre de dérivées distinctes (fini).
        """
        from ..fa.dfa import ExtendedDFA

        alphabet = frozenset(input_symbols) if input_symbols is not None else self.symbols()
        missing = self.symbols() - alphabet
        if missing:
            raise ValueError(f"symboles hors alphabet : {sorted(missing)}")

        start = self.simplify()
        names: Dict[Regex, str] = {}

        def name(r: Regex) -> str:
            return names.setdefault(r, str(r))

        transitions: dict = {}
        queue = [start]
        seen = {start}
        head = 0
        while head < len(queue):
            current = queue[head]
            head += 1
            row = {}
            for a in sorted(alphabet):
                nxt = current.derivative(a)
                row[a] = name(nxt)
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
            transitions[name(current)] = row

        return ExtendedDFA(
            states=frozenset(transitions),
            input_symbols=alphabet,
            transitions=transitions,
            initial_state=name(start),
            final_states=frozenset(name(r) for r in seen if r.nullable()),
        )

    def to_nfa(self, input_symbols: Optional[Iterable[str]] = None):
        """NFA de Thompson équivalent (voir ``ThompsonMixin.from_regex``)."""
        from ..fa.nfa import ExtendedNFA

        return ExtendedNFA.from_regex(self, input_symbols=input_symbols)

    # ---- Glushkov : positions -------------------------------------------
    def _glushkov(self):
        counter = [1]
        chars: Dict[int, str] = {}
        follow: Dict[int, Set[int]] = {}
        nullable, first, last = _analyse(self, counter, chars, follow)
        return nullable, first, last, follow, chars

    def positions(self) -> Dict[int, str]:
        """Numérotation (à partir de 1) des occurrences de symboles, de gauche à droite."""
        return dict(self._glushkov()[4])

    def firstpos(self) -> FrozenSet[int]:
        """Positions pouvant commencer un mot du langage (Glushkov)."""
        return frozenset(self._glushkov()[1])

    def lastpos(self) -> FrozenSet[int]:
        """Positions pouvant terminer un mot du langage (Glushkov)."""
        return frozenset(self._glushkov()[2])

    def followpos(self) -> Dict[int, FrozenSet[int]]:
        """Pour chaque position i, positions pouvant suivre immédiatement i."""
        return {i: frozenset(s) for i, s in self._glushkov()[3].items()}

    def to_glushkov_nfa(self, input_symbols: Optional[Iterable[str]] = None):
        """
        NFA de Glushkov (sans ε-transition) : états 0 (initial) et 1..n (positions).

        Complexity
        ----------
        O(n^2) dans le pire cas (taille de followpos).
        """
        from ..fa.nfa import ExtendedNFA

        nullable, first, last, follow, chars = self._glushkov()
        alphabet = frozenset(input_symbols) if input_symbols is not None else self.symbols()
        states = {0} | set(chars)
        rows: Dict[int, Dict[str, Set[int]]] = {s: {} for s in states}
        for j in first:
            rows[0].setdefault(chars[j], set()).add(j)
        for i, targets in follow.items():
            for j in targets:
                rows[i].setdefault(chars[j], set()).add(j)
        transitions = {s: {a: frozenset(t) for a, t in row.items()} for s, row in rows.items()}
        finals = set(last) | ({0} if nullable else set())
        return ExtendedNFA(
            states=frozenset(states),
            input_symbols=alphabet,
            transitions=transitions,
            initial_state=0,
            final_states=frozenset(finals),
        )


# ---------------------------------------------------------------------------
# Nœuds
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class Empty(Regex):
    """Langage vide ∅."""

    def nullable(self):
        return False

    def derivative(self, symbol):
        return self

    def symbols(self):
        return frozenset()

    def size(self):
        return 1


@dataclass(frozen=True, slots=True)
class Epsilon(Regex):
    """Mot vide ε."""

    def nullable(self):
        return True

    def derivative(self, symbol):
        return EMPTY

    def symbols(self):
        return frozenset()

    def size(self):
        return 1


@dataclass(frozen=True, slots=True)
class Symbol(Regex):
    """Un symbole de l'alphabet."""

    char: str

    def nullable(self):
        return False

    def derivative(self, symbol):
        return EPSILON if symbol == self.char else EMPTY

    def symbols(self):
        return frozenset({self.char})

    def size(self):
        return 1


@dataclass(frozen=True, slots=True)
class Union(Regex):
    """Union n-aire."""

    items: Tuple[Regex, ...]

    def nullable(self):
        return any(i.nullable() for i in self.items)

    def derivative(self, symbol):
        return union(*(i.derivative(symbol) for i in self.items))

    def symbols(self):
        return frozenset().union(*(i.symbols() for i in self.items))

    def size(self):
        return 1 + sum(i.size() for i in self.items)

    def _simplify_once(self):
        return union(*(i._simplify_once() for i in self.items))


@dataclass(frozen=True, slots=True)
class Concat(Regex):
    """Concaténation n-aire."""

    items: Tuple[Regex, ...]

    def nullable(self):
        return all(i.nullable() for i in self.items)

    def derivative(self, symbol):
        head, rest = self.items[0], concat(*self.items[1:])
        result = concat(head.derivative(symbol), rest)
        if head.nullable():
            result = union(result, rest.derivative(symbol))
        return result

    def symbols(self):
        return frozenset().union(*(i.symbols() for i in self.items))

    def size(self):
        return 1 + sum(i.size() for i in self.items)

    def _simplify_once(self):
        return concat(*(i._simplify_once() for i in self.items))


@dataclass(frozen=True, slots=True)
class Star(Regex):
    """Étoile de Kleene."""

    inner: Regex

    def nullable(self):
        return True

    def derivative(self, symbol):
        return concat(self.inner.derivative(symbol), self)

    def symbols(self):
        return self.inner.symbols()

    def size(self):
        return 1 + self.inner.size()

    def _simplify_once(self):
        return star(self.inner._simplify_once())


EMPTY = Empty()
EPSILON = Epsilon()


# ---------------------------------------------------------------------------
# Constructeurs intelligents
# ---------------------------------------------------------------------------
def union(*items: Regex) -> Regex:
    """Union normalisée (aplatie, dédupliquée, triée, ∅ neutre, ε absorbé si redondant)."""
    flat = []
    for r in items:
        if isinstance(r, Union):
            flat.extend(r.items)
        elif not isinstance(r, Empty):
            flat.append(r)
    uniq = set(flat)
    if EPSILON in uniq and any(r.nullable() for r in uniq if r != EPSILON):
        uniq.discard(EPSILON)
    if not uniq:
        return EMPTY
    if len(uniq) == 1:
        return next(iter(uniq))
    return Union(tuple(sorted(uniq, key=str)))


def concat(*items: Regex) -> Regex:
    """Concaténation normalisée (aplatie, ε neutre, ∅ absorbant)."""
    flat = []
    for r in items:
        if isinstance(r, Concat):
            flat.extend(r.items)
        elif isinstance(r, Empty):
            return EMPTY
        elif not isinstance(r, Epsilon):
            flat.append(r)
    if not flat:
        return EPSILON
    if len(flat) == 1:
        return flat[0]
    return Concat(tuple(flat))


def star(r: Regex) -> Regex:
    """Étoile normalisée (∅* = ε* = ε ; r** = r* ; (ε|r)* = r*)."""
    if isinstance(r, (Empty, Epsilon)):
        return EPSILON
    if isinstance(r, Star):
        return r
    if isinstance(r, Union) and EPSILON in r.items:
        return star(union(*(i for i in r.items if i != EPSILON)))
    return Star(r)


def plus(r: Regex) -> Regex:
    """r+ = r r*."""
    return concat(r, star(r))


def optional(r: Regex) -> Regex:
    """r? = ε | r."""
    return union(EPSILON, r)


# ---------------------------------------------------------------------------
# Affichage
# ---------------------------------------------------------------------------
def _esc(ch: str) -> str:
    return "\\" + ch if ch in _SPECIAL else ch


def _fmt(r: Regex, ctx: int) -> str:
    """ctx : 0 = niveau union, 1 = opérande de concaténation, 2 = opérande postfixe."""
    if isinstance(r, Empty):
        return "∅"
    if isinstance(r, Epsilon):
        return "()"
    if isinstance(r, Symbol):
        return _esc(r.char)
    if isinstance(r, Star):
        text = _fmt(r.inner, 2) + "*"
        return f"({text})" if ctx >= 2 else text
    if isinstance(r, Union):
        if EPSILON in r.items:
            rest = [i for i in r.items if i != EPSILON]
            node = rest[0] if len(rest) == 1 else Union(tuple(rest))
            text = _fmt(node, 2) + "?"
            return f"({text})" if ctx >= 2 else text
        text = "|".join(_fmt(i, 0) for i in r.items)
        return f"({text})" if ctx >= 1 else text
    if isinstance(r, Concat):
        text = "".join(_fmt(i, 1) for i in r.items)
        return f"({text})" if ctx >= 2 else text
    raise TypeError(r)


# ---------------------------------------------------------------------------
# Analyse de Glushkov
# ---------------------------------------------------------------------------
def _analyse(node: Regex, counter, chars, follow):
    """Retourne (nullable, firstpos, lastpos) et remplit ``chars`` / ``follow``."""
    if isinstance(node, (Empty,)):
        return False, set(), set()
    if isinstance(node, Epsilon):
        return True, set(), set()
    if isinstance(node, Symbol):
        i = counter[0]
        counter[0] += 1
        chars[i] = node.char
        follow[i] = set()
        return False, {i}, {i}
    if isinstance(node, Union):
        nullable, first, last = False, set(), set()
        for item in node.items:
            n, f, l = _analyse(item, counter, chars, follow)
            nullable |= n
            first |= f
            last |= l
        return nullable, first, last
    if isinstance(node, Concat):
        n1, f1, l1 = True, set(), set()
        for item in node.items:
            n2, f2, l2 = _analyse(item, counter, chars, follow)
            for i in l1:
                follow[i] |= f2
            first = f1 | (f2 if n1 else set())
            last = l2 | (l1 if n2 else set())
            n1, f1, l1 = n1 and n2, first, last
        return n1, f1, l1
    if isinstance(node, Star):
        _, f, l = _analyse(node.inner, counter, chars, follow)
        for i in l:
            follow[i] |= f
        return True, f, l
    raise TypeError(node)
