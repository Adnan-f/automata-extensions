"""ExtendedNFA : automate fini non déterministe étendu."""

from automata.fa.nfa import NFA

from .base import ExtendedFA
from .nfa_mixins.determinization import DeterminizationMixin
from .nfa_mixins.elimination import EliminationMixin
from .nfa_mixins.epsilon import EpsilonMixin
from .nfa_mixins.execution import NFAExecutionMixin
from .nfa_mixins.grammar_nfa import GrammarNFAMixin
from .nfa_mixins.thompson import ThompsonMixin


class ExtendedNFA(
    NFAExecutionMixin,
    GrammarNFAMixin,
    ThompsonMixin,
    DeterminizationMixin,
    EliminationMixin,
    EpsilonMixin,
    ExtendedFA,
    NFA,
):
    """NFA d'automata-lib enrichi par les mixins de ``ExtendedFA``."""

    __slots__ = ()
    _nondeterministic = True