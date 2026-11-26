"""automata_extensions : extension pédagogique de automata-lib 9.2.0."""

from .utils.patches import patch_cached_method

# Appliqué dès l'import : corrige aussi les DFA/NFA purs d'automata-lib.
patch_cached_method()

__version__ = "0.1.0"
