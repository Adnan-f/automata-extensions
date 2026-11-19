"""MorphismMixin : morphismes d'automates, projection d'alphabet, quotient par une application."""

from __future__ import annotations

from typing import Callable, Mapping, Optional, TypeVar

FAType = TypeVar("FAType")


class MorphismMixin:
    """Morphismes d'automates (item 61), projection de symboles, fusion d'états."""

    def is_morphism_to(self, other, state_map: Mapping) -> bool:
        """
        Teste si ``state_map`` est un morphisme d'automate valide de ``self`` vers ``other``.

        Un morphisme préserve les transitions : pour tout état p et symbole
        a, si delta_self(p, a) = q alors delta_other(state_map[p], a) doit
        contenir state_map[q]. Il doit aussi envoyer l'état initial sur
        l'état initial et les états finaux sur des états finaux.

        Parameters
        ----------
        other : FA
            Automate cible.
        state_map : Mapping
            Application des états de ``self`` vers les états de ``other``.

        Returns
        -------
        bool

        Complexity
        ----------
        O(|Q| * |Sigma|)
        """
        if state_map.get(self.initial_state) != other.initial_state:
            return False
        self_finals = self._final_states_set()
        other_finals = other._final_states_set()
        for s in self_finals:
            if state_map.get(s) not in other_finals:
                return False
        for source, row in self.transitions.items():
            mapped_source = state_map.get(source)
            for symbol, target in row.items():
                targets = target if self._nondeterministic else {target}
                other_row = other.transitions.get(mapped_source, {})
                other_targets = other_row.get(symbol)
                if other_targets is None:
                    return False
                other_targets = (
                    other_targets if other._nondeterministic else {other_targets}
                )
                for t in targets:
                    if state_map.get(t) not in other_targets:
                        return False
        return True

    def project(self, symbol_map):
        """
        Relabellise ou efface les symboles d'entrée (homomorphisme de mots).

        Chaque symbole ``a`` est remplacé par ``symbol_map[a]`` (inchangé s'il est absent
        de ``symbol_map``) ; ``None`` **efface** le symbole : la transition devient une
        ε-transition. Les ε-transitions existantes sont conservées.

        Le résultat est un **NFA** dès qu'il peut être non déterministe : symbole effacé
        (ε-transition) ou deux symboles fusionnés vers des cibles différentes. Un simple
        renommage injectif d'un DFA reste un DFA (partiel si besoin).

        Parameters
        ----------
        symbol_map : Mapping[str, Optional[str]]
            Association symbole d'origine -> nouveau symbole (ou ``None`` pour effacer).

        Returns
        -------
        FA
            Nouvel automate : même classe que ``self`` si le résultat reste déterministe,
            sinon un ``ExtendedNFA``. Il reconnaît ``{h(w) : w dans L}``.

        Raises
        ------
        TypeError
            Pour un GNFA.

        Complexity
        ----------
        O(|Q| * |Sigma|)
        """
        from automata.fa.gnfa import GNFA

        if isinstance(self, GNFA):
            raise TypeError("project n'est pas défini pour un GNFA")

        new_symbols = {symbol_map.get(a, a) for a in self.input_symbols} - {None}
        rows = {}
        erased = False
        for source, row in self.transitions.items():
            new_row = {}
            for symbol, target in row.items():
                new_symbol = "" if symbol == "" else symbol_map.get(symbol, symbol)
                if new_symbol is None:
                    erased = True
                    new_symbol = ""
                targets = set(target) if self._nondeterministic else {target}
                new_row.setdefault(new_symbol, set()).update(targets)
            rows[source] = new_row

        nondeterministic = self._nondeterministic or erased or any(
            len(targets) > 1 for row in rows.values() for targets in row.values())

        if not nondeterministic:
            params = dict(self.input_parameters)
            params["input_symbols"] = frozenset(new_symbols)
            params["transitions"] = {
                source: {symbol: next(iter(targets)) for symbol, targets in row.items()}
                for source, row in rows.items()}
            if "allow_partial" in params:
                params["allow_partial"] = True
            return self.__class__(**params)

        from ..nfa import ExtendedNFA

        nfa_class = self.__class__ if self._nondeterministic else ExtendedNFA
        return nfa_class(
            states=frozenset(self.states), input_symbols=frozenset(new_symbols),
            transitions={source: {symbol: frozenset(targets) for symbol, targets in row.items()}
                         for source, row in rows.items()},
            initial_state=self.initial_state,
            final_states=frozenset(self._final_states_set()))

    def quotient_by(self: FAType, state_map: Mapping) -> FAType:
        """
        Fusionne des états selon une application donnée.

        Contrairement à ``minimize``, ``state_map`` n'a pas besoin d'être
        une congruence : la fusion est appliquée telle quelle.

        Parameters
        ----------
        state_map : Mapping
            Association ancien état -> nouvel état (représentant de classe).

        Returns
        -------
        FA
            Nouvel automate sur les états fusionnés.

        Complexity
        ----------
        O(|Q| * |Sigma|)
        """
        new_states = set(state_map.values())
        new_transitions: dict = {}
        for source, row in self.transitions.items():
            mapped_source = state_map.get(source, source)
            new_row = new_transitions.setdefault(mapped_source, {})
            for symbol, target in row.items():
                if self._nondeterministic:
                    mapped_targets = {state_map.get(t, t) for t in target}
                    existing = new_row.get(symbol, set())
                    if not isinstance(existing, (set, frozenset)):
                        existing = {existing}
                    new_row[symbol] = set(existing) | mapped_targets
                else:
                    new_row[symbol] = state_map.get(target, target)

        params = dict(self.input_parameters)
        params["states"] = frozenset(new_states)
        params["transitions"] = new_transitions
        params["initial_state"] = state_map.get(self.initial_state, self.initial_state)
        if "final_states" in params:
            params["final_states"] = frozenset(
                state_map.get(s, s) for s in self._final_states_set()
            )
        else:
            params["final_state"] = state_map.get(self.final_state, self.final_state)
        if "allow_partial" in params:
            params["allow_partial"] = True
        return self.__class__(**params)
