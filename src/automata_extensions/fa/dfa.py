# dfa.py
"""ExtendedDFA : automate fini déterministe étendu."""
from automata.fa.dfa import DFA
from .base import ExtendedFA


class ExtendedDFA(ExtendedFA, DFA):
    """DFA d'automata-lib enrichi par les mixins de ``ExtendedFA``."""
    __slots__ = ()
