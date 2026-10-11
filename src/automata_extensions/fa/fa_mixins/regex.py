"""RegexMixin : conversion automate -> expression régulière (item 53).

Implémenté comme un simple wrapper autour de ``automata.fa.gnfa.GNFA``
(élimination d'états), conformément à la consigne du cahier des charges :
ne jamais réimplémenter un algorithme déjà fourni par automata-lib.
"""

from __future__ import annotations


class RegexMixin:
    """Conversion vers une expression régulière via élimination d'états (GNFA)."""

    def to_regex(self) -> str:
        """
        Expression régulière dénotant L(self).

        Wrapper : délègue à ``automata.fa.gnfa.GNFA.from_dfa(...).to_regex()``
        d'automata-lib (élimination d'états). Un NFA est d'abord déterminisé.

        Returns
        -------
        str
            Expression régulière équivalente.

        Complexity
        ----------
        O(|Q|^3) (élimination d'états, taille des expressions pouvant
        croître exponentiellement dans le pire cas).

        References
        ----------
        Hopcroft, Motwani, Ullman — construction du GNFA par élimination d'états.
        """
        from automata.fa.gnfa import GNFA

        source = self if not self._nondeterministic else self.determinize()
        return GNFA.from_dfa(source).to_regex()
