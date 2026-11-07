"""MinimizationMixin : distinguabilité, classes de Myhill-Nerode, minimisation (items 29-32)."""

from __future__ import annotations

from itertools import combinations
from typing import Dict, FrozenSet, List, Optional, Set, TypeVar

from ...utils.ordering import sort_states, state_label

DFAType = TypeVar("DFAType")


class MinimizationMixin:
    """
    Minimisation par l'algorithme de remplissage de table (table-filling).

    Suppose un DFA complet et accessible (on le complète/élague en interne
    si besoin) pour que la table de paires soit bien définie sur tous les
    états.
    """

    def pair_table(self) -> Dict[FrozenSet, Optional[int]]:
        """
        Table de distinguabilité complète, avec le numéro de round de marquage.

        Une paire ``{p, q}`` reçoit le round ``0`` si exactement un des deux états est
        final ; sinon le round ``r`` si, pour un symbole ``a``, la paire
        ``{δ(p,a), δ(q,a)}`` a été marquée au round ``r-1`` (les marques d'un round
        n'utilisent que celles des rounds précédents). Une paire jamais marquée vaut
        ``None`` : les deux états sont équivalents.

        Le round d'une paire est la **longueur du plus court mot** qui distingue les deux
        états (``0`` : le mot vide).

        Returns
        -------
        dict
            ``frozenset({p, q}) -> round`` (``int``) ou ``None``, pour les états de
            l'automate complété.

        Complexity
        ----------
        O(|Q|^2 * |Sigma|) par round, au plus |Q|^2 rounds.

        References
        ----------
        Hopcroft, Motwani, Ullman — algorithme de remplissage de table.
        """
        complete_self = self.complete()
        states = sort_states(complete_self.states)
        finals = set(complete_self.final_states)
        symbols = sorted(complete_self.input_symbols)
        table: Dict[FrozenSet, Optional[int]] = {}
        for p, q in combinations(states, 2):
            table[frozenset((p, q))] = 0 if (p in finals) != (q in finals) else None

        round_number = 0
        while True:
            round_number += 1
            newly_marked = []
            for pair, mark in table.items():
                if mark is not None:
                    continue
                p, q = tuple(pair)
                for symbol in symbols:
                    tp = complete_self.transitions[p][symbol]
                    tq = complete_self.transitions[q][symbol]
                    if tp != tq and table[frozenset((tp, tq))] is not None:
                        newly_marked.append(pair)
                        break
            if not newly_marked:
                return table
            for pair in newly_marked:
                table[pair] = round_number

    def distinguishable_states(self) -> Set[FrozenSet]:
        """
        Ensemble des paires d'états distinguables (celles marquées dans ``pair_table``).

        Returns
        -------
        set of frozenset
            Chaque élément est une paire {p, q} distinguable.

        Complexity
        ----------
        Celle de ``pair_table``.
        """
        return {pair for pair, mark in self.pair_table().items() if mark is not None}

    def pair_table_str(self, show_round: bool = False) -> str:
        """
        Table de distinguabilité en ASCII (triangle inférieur).

        La première ligne liste les colonnes (tous les états sauf le dernier), puis une
        ligne par état (sauf le premier) donne, pour chaque colonne plus petite, le numéro
        de round (``show_round=True``) ou ``X`` (distinguables) ; ``-`` : équivalents.
        Exemple pour le DFA « nombre de a multiple de 3 » : ``' 0 1\\n1 0\\n2 0 1'``.

        Parameters
        ----------
        show_round : bool
            Afficher le numéro de round plutôt que ``X``.

        Returns
        -------
        str

        Complexity
        ----------
        O(|Q|^2) après le calcul de ``pair_table``.
        """
        table = self.pair_table()
        states = sort_states(self.complete().states)
        if len(states) < 2:
            return ""

        def cell(mark: Optional[int]) -> str:
            return "-" if mark is None else (str(mark) if show_round else "X")

        lines = [" ".join([""] + [state_label(s) for s in states[:-1]])]
        for i in range(1, len(states)):
            entries = [cell(table[frozenset((states[i], states[j]))]) for j in range(i)]
            lines.append(" ".join([state_label(states[i])] + entries))
        return "\n".join(lines)

    def print_pair_table(self, show_round: bool = True) -> None:
        """Affiche ``pair_table_str`` (avec les numéros de round par défaut)."""
        print(self.pair_table_str(show_round=show_round))

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
            Nouveau DFA minimal, restreint aux états utiles.

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