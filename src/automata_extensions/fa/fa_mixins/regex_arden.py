"""ArdenMixin : conversion automate -> regex par résolution d'un système d'équations
de langages via le lemme d'Arden (items 54, 57, 58).

Contrairement à ``RegexMixin.to_regex`` (qui délègue à ``GNFA`` d'automata-lib),
cette implémentation est entièrement indépendante : c'est un véritable ajout,
automata-lib ne proposant aucune résolution par le lemme d'Arden.
"""

from __future__ import annotations

_CONST = object()  # sentinelle représentant le terme constant (epsilon) d'une équation


def _is_empty(r):
    """``None`` représente le langage vide (∅)."""
    return r is None


def _is_epsilon(r):
    return r == ""


def _fully_parenthesized(r: str) -> bool:
    """Teste si ``r`` est de la forme ``(...)`` avec une seule paire englobante."""
    if not (r.startswith("(") and r.endswith(")")):
        return False
    depth = 0
    for i, ch in enumerate(r):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and i != len(r) - 1:
                return False
    return True


def _wrap_if_union(r: str) -> str:
    """Parenthèse ``r`` s'il contient un ``|`` de premier niveau non déjà protégé."""
    if "|" in r and not _fully_parenthesized(r):
        return f"({r})"
    return r


def _wrap_for_star(r: str) -> str:
    """Parenthèse ``r`` avant de lui appliquer une étoile, sauf s'il est atomique."""
    if len(r) == 1 or _fully_parenthesized(r):
        return r
    return f"({r})"


def _union(a, b):
    if _is_empty(a):
        return b
    if _is_empty(b):
        return a
    if a == b:
        return a
    # epsilon dans une union s'écrit « () » (un opérande vide est invalide)
    a = "()" if _is_epsilon(a) else a
    b = "()" if _is_epsilon(b) else b
    return f"{a}|{b}"


def _concat(a, b):
    if _is_empty(a) or _is_empty(b):
        return None
    if _is_epsilon(a):
        return b
    if _is_epsilon(b):
        return a
    return f"{_wrap_if_union(a)}{_wrap_if_union(b)}"


def _star(a):
    if _is_empty(a) or _is_epsilon(a):
        return ""
    return f"{_wrap_for_star(a)}*"


class ArdenMixin:
    """Résolution du système d'équations de langages associé à un automate."""

    def to_regex_arden(self) -> str:
        """
        Expression régulière dénotant L(self), par le lemme d'Arden.

        Pour chaque état q, on pose l'équation X_q = union_{(a,q') in delta}
        a·X_q' , plus un terme constant epsilon si q est final. On élimine
        les variables une à une (en substituant X_q dans les équations qui
        la référencent, après avoir résolu une éventuelle auto-référence par
        le lemme d'Arden : X = AX ∪ B => X = A*B), jusqu'à ne garder que
        l'équation de l'état initial.

        Returns
        -------
        str or None
            Expression régulière équivalente (peut différer syntaxiquement
            de ``to_regex()`` tout en dénotant le même langage). ``None`` si
            le langage est vide (aucune regex d'automata-lib ne l'exprime).

        Complexity
        ----------
        O(|Q|^3) dans le pire cas (taille des expressions potentiellement
        exponentielle).

        References
        ----------
        Lemme d'Arden ; Hopcroft, Motwani, Ullman.
        """
        source = self if not self._nondeterministic else self.remove_epsilon_transitions()
        finals = source._final_states_set()

        equations = {}
        for q in source.states:
            eq = {}
            row = source.transitions.get(q, {})
            for symbol, target in row.items():
                targets = target if source._nondeterministic else {target}
                for t in targets:
                    eq[t] = _union(eq.get(t), symbol)
            if q in finals:
                eq[_CONST] = ""
            equations[q] = eq

        to_eliminate = [q for q in source.states if q != source.initial_state]
        for q in to_eliminate:
            eq_q = equations.pop(q)
            self_coeff = eq_q.pop(q, None)
            star_self = _star(self_coeff)
            resolved = {
                target: _concat(star_self, coeff) for target, coeff in eq_q.items()
            }

            for p, eq_p in equations.items():
                coeff_to_q = eq_p.pop(q, None)
                if coeff_to_q is None:
                    continue
                for target, coeff in resolved.items():
                    added = _concat(coeff_to_q, coeff)
                    eq_p[target] = _union(eq_p.get(target), added)

        final_eq = equations[source.initial_state]
        self_coeff = final_eq.pop(source.initial_state, None)
        star_self = _star(self_coeff)
        constant = final_eq.pop(_CONST, None)
        return _concat(star_self, constant)
