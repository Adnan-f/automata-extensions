"""ResidualMixin : automate des résiduels / classes de Myhill-Nerode (items 59, 60)."""

from __future__ import annotations

from typing import Dict, Tuple


class ResidualMixin:
    """Les états sont les résiduels ``u^-1 L`` (quotients à gauche par un mot)."""

    def _residual_structure(self) -> Tuple[Dict, Dict, Dict, Dict]:
        """BFS sur les classes d'équivalence : (noms, mot le plus court, transitions, finals)."""
        c = self.complete()
        c = c.induced_subautomaton(c.accessible_states())
        class_of = {s: cls for cls in c.equivalence_classes() for s in cls}
        symbols = sorted(c.input_symbols)

        start = class_of[c.initial_state]
        names = {start: "q0"}
        words = {"q0": ""}
        transitions: Dict = {}
        queue, head = [start], 0
        while head < len(queue):
            cls = queue[head]
            head += 1
            representative = next(iter(cls))
            row = {}
            for a in symbols:
                target = class_of[c.transitions[representative][a]]
                if target not in names:
                    names[target] = f"q{len(names)}"
                    words[names[target]] = words[names[cls]] + a
                    queue.append(target)
                row[a] = names[target]
            transitions[names[cls]] = row
        finals = {names[cls] for cls in names if next(iter(cls)) in c.final_states}
        return names, words, transitions, finals

    def residuals(self) -> Dict[str, str]:
        """
        Représentants des classes de Myhill-Nerode.

        Returns
        -------
        dict
            Nom du résiduel (``q0``, ``q1``...) -> plus court mot ``u`` dont le
            quotient à gauche ``u^-1 L`` est ce résiduel (``q0`` : mot vide).
            Les noms suivent l'ordre de découverte par BFS (symboles triés).

        Complexity
        ----------
        O(|Q|^2 * |Sigma|)
        """
        return dict(self._residual_structure()[1])

    def residual_automaton(self):
        """
        Automate dont les états sont les résiduels du langage.

        C'est (à renommage près) le DFA minimal complet : ses états ``q0, q1, ...``
        sont numérotés dans l'ordre de découverte par BFS, ``q0`` étant le
        résiduel du mot vide (le langage lui-même).

        Returns
        -------
        DFA
            Nouveau DFA complet et minimal.

        Complexity
        ----------
        O(|Q|^2 * |Sigma|)

        References
        ----------
        Nerode (1958) ; Hopcroft, Motwani, Ullman.
        """
        names, _, transitions, finals = self._residual_structure()
        return self.__class__(
            states=frozenset(transitions),
            input_symbols=frozenset(self.input_symbols),
            transitions=transitions,
            initial_state="q0",
            final_states=frozenset(finals),
        )
