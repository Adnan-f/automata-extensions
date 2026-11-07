"""ExtendedGNFA : automate fini généralisé étendu."""

from automata.fa.gnfa import GNFA

from .base import ExtendedFA
from .gnfa_mixins.elimination import GNFAEliminationMixin


class ExtendedGNFA(GNFAEliminationMixin, ExtendedFA, GNFA):
    """GNFA d'automata-lib enrichi par les mixins de ``ExtendedFA``."""

    __slots__ = ()