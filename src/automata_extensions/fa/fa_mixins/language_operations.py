"""LanguageOperationsMixin : union, concaténation, étoile de Kleene (items 42, 45, 46).

Construction directe par ajout d'epsilon-transitions (indépendante des
méthodes ``union``/``concatenate``/``kleene_star`` d'automata-lib), utilisable
aussi bien sur un DFA que sur un NFA, puisqu'elle ne vit qu'au niveau
``ExtendedFA``. Le résultat est toujours un ``ExtendedNFA``.
"""

from __future__ import annotations


def _fresh_name(base: str, taken: set) -> str:
    name = base
    suffix = 0
    while name in taken:
        suffix += 1
        name = f"{base}{suffix}"
    return name


def _prefixed_transitions(fa, prefix: str) -> dict:
    """Renomme tous les états de ``fa`` en les préfixant, pour les rendre disjoints."""
    rename = {s: f"{prefix}{s}" for s in fa.states}
    new_transitions = {}
    for source, row in fa.transitions.items():
        new_row = {}
        for symbol, target in row.items():
            targets = target if fa._nondeterministic else {target}
            new_row[symbol] = frozenset(rename[t] for t in targets)
        new_transitions[rename[source]] = new_row
    return rename, new_transitions


class LanguageOperationsMixin:
    """Union, concaténation et étoile de Kleene, construites par epsilon-transitions."""

    def union(self, other):
        """
        Union des langages : L(self) ∪ L(other), par construction directe.

        Un nouvel état initial est relié par epsilon-transition aux deux
        anciens états initiaux.

        Parameters
        ----------
        other : FA

        Returns
        -------
        NFA
            Nouvel ``ExtendedNFA``.

        Complexity
        ----------
        O(|Q1| + |Q2|)

        References
        ----------
        Hopcroft, Motwani, Ullman — opérations rationnelles.
        """
        from ..nfa import ExtendedNFA

        rename_a, trans_a = _prefixed_transitions(self, "A_")
        rename_b, trans_b = _prefixed_transitions(other, "B_")

        states = set(trans_a) | set(trans_b)
        start = _fresh_name("__union_start__", states)

        transitions = {**trans_a, **trans_b}
        transitions[start] = {
            "": frozenset({rename_a[self.initial_state], rename_b[other.initial_state]})
        }

        finals = {rename_a[s] for s in self._final_states_set()} | \
                 {rename_b[s] for s in other._final_states_set()}

        return ExtendedNFA(
            states=frozenset(states | {start}),
            input_symbols=frozenset(self.input_symbols | other.input_symbols),
            transitions=transitions,
            initial_state=start,
            final_states=frozenset(finals),
        )

    def concatenation(self, other):
        """
        Concaténation des langages : L(self) . L(other).

        Chaque état final de ``self`` reçoit une epsilon-transition vers
        l'état initial de ``other``.

        Parameters
        ----------
        other : FA

        Returns
        -------
        NFA
            Nouvel ``ExtendedNFA``.

        Complexity
        ----------
        O(|Q1| + |Q2|)
        """
        from ..nfa import ExtendedNFA

        rename_a, trans_a = _prefixed_transitions(self, "A_")
        rename_b, trans_b = _prefixed_transitions(other, "B_")

        transitions = {**trans_a, **trans_b}
        for s in self._final_states_set():
            key = rename_a[s]
            bucket = transitions.setdefault(key, {})
            bucket[""] = frozenset(bucket.get("", set()) | {rename_b[other.initial_state]})

        return ExtendedNFA(
            states=frozenset(set(trans_a) | set(trans_b)),
            input_symbols=frozenset(self.input_symbols | other.input_symbols),
            transitions=transitions,
            initial_state=rename_a[self.initial_state],
            final_states=frozenset(rename_b[s] for s in other._final_states_set()),
        )

    def kleene_star(self):
        """
        Étoile de Kleene de L(self).

        Un nouvel état initial, final (pour accepter le mot vide), relié
        par epsilon-transition à l'ancien état initial ; chaque ancien état
        final reçoit une epsilon-transition de retour vers lui.

        Returns
        -------
        NFA
            Nouvel ``ExtendedNFA``.

        Complexity
        ----------
        O(|Q|)
        """
        from ..nfa import ExtendedNFA

        rename, trans = _prefixed_transitions(self, "A_")
        states = set(trans)
        start = _fresh_name("__star_start__", states)

        transitions = dict(trans)
        transitions[start] = {"": frozenset({rename[self.initial_state]})}
        for s in self._final_states_set():
            key = rename[s]
            bucket = transitions.setdefault(key, {})
            bucket[""] = frozenset(bucket.get("", set()) | {start})

        return ExtendedNFA(
            states=frozenset(states | {start}),
            input_symbols=frozenset(self.input_symbols),
            transitions=transitions,
            initial_state=start,
            final_states=frozenset({start}),
        )
