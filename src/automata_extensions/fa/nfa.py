# nfa.py
"""ExtendedNFA : automate fini non déterministe étendu."""
from automata.fa.nfa import NFA
from .base import ExtendedFA


class ExtendedNFA(ExtendedFA, NFA):
    """NFA d'automata-lib enrichi par les mixins de ``ExtendedFA``."""

    __slots__ = ()
    _nondeterministic = True
