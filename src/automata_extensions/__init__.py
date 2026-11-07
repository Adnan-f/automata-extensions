"""automata_extensions : extension pédagogique de automata-lib 9.2.0.

Les classes principales s'importent directement ::

    from automata_extensions import ExtendedDFA, ExtendedNFA

Modules : ``fa`` (automates), ``regex`` (AST, dérivées, positions), ``grammar``
(grammaires régulières, arbres de dérivation), ``algebra`` (monoïdes),
``exercises`` (exercices corrigés), ``utils`` (correctifs, rendu Graphviz).
"""

from .utils.patches import patch_cached_method

# Appliqué dès l'import : corrige aussi les DFA/NFA purs d'automata-lib.
patch_cached_method()

from .fa import ExtendedDFA, ExtendedFA, ExtendedGNFA, ExtendedNFA  # noqa: E402
from .grammar import Grammar  # noqa: E402
from .regex import parse as parse_regex  # noqa: E402

__version__ = "0.1.0"

__all__ = ["ExtendedFA", "ExtendedDFA", "ExtendedNFA", "ExtendedGNFA", "Grammar",
           "parse_regex", "__version__"]
