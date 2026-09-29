"""MinimizationMixin : distinguabilité, classes de Myhill-Nerode, minimisation (items 29-32)."""

from __future__ import annotations

from itertools import combinations
from typing import Dict, FrozenSet, List, Set, TypeVar

DFAType = TypeVar("DFAType")


class MinimizationMixin:
    """
    Minimisation par l'algorithme de remplissage de table (table-filling).

    Suppose un DFA complet et accessible (on le complète/élague en interne
    si besoin) pour que la table de paires soit bien définie sur tous les
    états.
    """

    def distinguishable_states(self) -> Set[FrozenSet]:
        """
        Ensemble des paires d'états distinguables.

        Algorithme de remplissage de table : une paire est marquée
        initialement si exactement un des deux états est final, puis on
        propage — une paire (p, q) est distinguable si, pour un symbole a,
        (delta(p, a), delta(q, a)) est déjà marquée distinguable.

        Returns
        -------
        set of frozenset
            Chaque élément est une paire {p, q} distinguable.

        Complexity
        ----------
        O(|Q|^2 * |Sigma|)

        References
        ----------
        Hopcroft, Motwani, Ullman — algorithme de remplissage de table.
        """
        complete_self = self.complete()
        states = sorted(complete_self.states, key=str)
        finals = set(complete_self.final_states)

        marked: Set[FrozenSet] = set()
        pairs = list(combinations(states, 2))

        for p, q in pairs:
            if (p in finals) != (q in finals):
                marked.add(frozenset((p, q)))

        changed = True
        while changed:
            changed = False
            for p, q in pairs:
                pair = frozenset((p, q))
                if pair in marked:
                    continue
                for symbol in complete_self.input_symbols:
                    tp = complete_self.transitions[p][symbol]
                    tq = complete_self.transitions[q][symbol]
                    if tp != tq and frozenset((tp, tq)) in marked:
                        marked.add(pair)
                        changed = True
                        break
        return marked

    def pair_table_str(self, show_round: bool = False) -> str:
        """
        Représentation ASCII triangulaire de la table de distinguabilité.

        Parameters
        ----------
        show_round : bool
            Ignoré ici (conservé pour compatibilité de signature) : cette
            implémentation ne numérote pas les rounds de marquage.

        Returns
        -------
        str
            Une ligne par état (sauf le premier), listant à quel autre état
            il est marqué distinguable.

        Complexity
        ----------
        O(|Q|^2)
        """
        states = sorted(self.states, key=str)
        marked = self.distinguishable_states()
        lines = []
        for i in range(1, len(states)):
            row_marks = []
            for j in range(i):
                row_marks.append("1" if frozenset((states[i], states[j])) in marked else "0")
            lines.append(" ".join(row_marks))
        return "\n".join(lines)

    def equivalence_classes(self) -> List[FrozenSet]:
        """
        Classes d'équivalence de Myhill-Nerode.

        Deux états non distinguables (au sens de ``distinguishable_states``)
        sont dans la même classe.

        Returns
        -------
        list of frozenset
            Partition des états de l'automate complété.

        Complexity
        ----------
        O(|Q|^2 * |Sigma|)
        """
        complete_self = self.complete()
        marked = self.distinguishable_states()
        states = list(complete_self.states)
        parent: Dict = {s: s for s in states}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry

        for p, q in combinations(states, 2):
            if frozenset((p, q)) not in marked:
                union(p, q)

        classes: Dict = {}
        for s in states:
            classes.setdefault(find(s), set()).add(s)
        return [frozenset(c) for c in classes.values()]

    def is_minimal(self) -> bool:
        """
        Teste si l'automate est déjà minimal.

        Un DFA est minimal ssi il est accessible et chaque classe
        d'équivalence de Myhill-Nerode est un singleton.

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q|^2 * |Sigma|)
        """
        if self.accessible_states() != set(self.states):
            return False
        return all(len(c) == 1 for c in self.equivalence_classes())

    def minimize(self: DFAType, keep_original_names: bool = False) -> DFAType:
        """
        DFA minimal équivalent (fusion des états équivalents).

        Parameters
        ----------
        keep_original_names : bool
            Si ``True``, chaque classe fusionnée est nommée par un
            représentant (le plus petit élément, comparé via ``str``)
            plutôt que par le ``frozenset`` de la classe entière.

        Returns
        -------
        DFA
            Nouveau DFA minimal, restreint aux états accessibles.

        Complexity
        ----------
        O(|Q|^2 * |Sigma|)

        References
        ----------
        Hopcroft, Motwani, Ullman.
        """
        complete_self = self.complete()
        classes = complete_self.equivalence_classes()

        def name(cls: FrozenSet):
            return min(cls, key=str) if keep_original_names else cls

        class_of = {}
        for cls in classes:
            for s in cls:
                class_of[s] = name(cls)

        new_states = {class_of[s] for s in complete_self.states}
        new_transitions: Dict = {}
        for cls in classes:
            representative = next(iter(cls))
            row = complete_self.transitions[representative]
            new_transitions[name(cls)] = {
                symbol: class_of[target] for symbol, target in row.items()
            }
        new_initial = class_of[complete_self.initial_state]
        new_finals = {class_of[s] for s in complete_self.final_states}

        result = self.__class__(
            states=frozenset(new_states),
            input_symbols=frozenset(complete_self.input_symbols),
            transitions=new_transitions,
            initial_state=new_initial,
            final_states=frozenset(new_finals),
        )
        return result.trim()
