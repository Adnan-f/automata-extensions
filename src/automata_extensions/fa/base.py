"""ExtendedFA : couche commune à ExtendedDFA / ExtendedNFA / ExtendedGNFA.

Règle du projet : tout algorithme qui ne dépend que de ``states``,
``transitions``, ``initial_state`` et ``final_states`` est écrit ici (via des
mixins) ; seuls les algorithmes spécifiques au déterminisme ou aux
ε-transitions vont dans ``dfa.py`` / ``nfa.py`` / ``gnfa.py``.
"""

from __future__ import annotations

from typing import Any, Dict

from automata.fa.fa import FA
from .fa_mixins.accessibility import AccessibilityMixin
from .fa_mixins.cycle import CycleMixin
from .fa_mixins.graph import GraphMixin
from .fa_mixins.traversal import TraversalMixin


class ExtendedFA(
    CycleMixin,
    AccessibilityMixin,
    TraversalMixin,
    GraphMixin,
    FA,
):
    """Base commune des automates finis étendus.

    Les mixins seront ajoutés ici, *avant* ``FA`` dans la liste des parents
    (leur ordre détermine la priorité des méthodes, cf. MRO).
    """

    __slots__ = ()  # aucun état propre : tout l'état vient de DFA/NFA/GNFA

    @property
    def input_parameters(self) -> Dict[str, Any]:
        """Attributs publics permettant de reconstruire l'automate.

        automata-lib ne lit que ``self.__slots__`` de la classe la plus dérivée ;
        avec des sous-classes déclarant ``__slots__ = ()`` on obtiendrait un
        dictionnaire vide. On parcourt donc tout le MRO.

        Returns
        -------
        dict
            Nom d'attribut -> valeur (états, alphabet, transitions, ...).

        Complexity
        ----------
        O(|MRO| + nombre d'attributs)
        """
        params: Dict[str, Any] = {}
        for klass in type(self).__mro__:
            slots = klass.__dict__.get("__slots__", ())
            if isinstance(slots, str):
                slots = (slots,)
            for name in slots:
                if not name.startswith("_") and name not in params:
                    params[name] = getattr(self, name)
        return params