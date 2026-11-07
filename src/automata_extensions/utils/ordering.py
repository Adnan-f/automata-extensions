"""Ordres et libellés déterministes pour les états (indépendants de la graine de hachage)."""

from __future__ import annotations

import re
from typing import Iterable, List

_NATURAL = re.compile(r"(\d+)")


def natural_key(text: str):
    """Tri « naturel » : ``q2 < q10``."""
    return [int(part) if part.isdigit() else part for part in _NATURAL.split(text)]


def state_label(state) -> str:
    """
    Texte lisible et *stable* d'un état : ``frozenset({'0','1'})`` s'écrit ``{0,1}``,
    ``('a','b')`` s'écrit ``(a,b)``, le reste via ``str``.
    """
    if isinstance(state, (set, frozenset)):
        return "{" + ",".join(sorted((state_label(s) for s in state), key=natural_key)) + "}"
    if isinstance(state, tuple):
        return "(" + ",".join(state_label(s) for s in state) + ")"
    return str(state)


def sort_states(states: Iterable) -> List:
    """États triés de façon déterministe (tri naturel sur leur libellé)."""
    return sorted(states, key=lambda s: natural_key(state_label(s)))
