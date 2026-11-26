# gnfa.py
"""ExtendedGNFA : automate fini généralisé étendu."""
from automata.fa.gnfa import GNFA
from .base import ExtendedFA


class ExtendedGNFA(ExtendedFA, GNFA):
    """GNFA d'automata-lib enrichi par les mixins de ``ExtendedFA``."""
    __slots__ = ()
