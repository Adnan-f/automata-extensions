"""ExtendedDFA : automate fini déterministe étendu."""

from automata.fa.dfa import DFA

from .base import ExtendedFA
from .dfa_mixins.completeness import CompletenessMixin
from .dfa_mixins.complement import ComplementMixin
from .dfa_mixins.product import ProductMixin
from .dfa_mixins.union import UnionMixin
from .dfa_mixins.difference import DifferenceMixin
from .dfa_mixins.inclusion import InclusionMixin


class ExtendedDFA(
    InclusionMixin,
    DifferenceMixin,
    UnionMixin,
    ProductMixin,
    ComplementMixin,
    CompletenessMixin,
    ExtendedFA,
    DFA,
):
    """DFA d'automata-lib enrichi par les mixins de ``ExtendedFA``."""

    __slots__ = ()