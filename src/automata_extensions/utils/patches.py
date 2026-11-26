"""Correctifs appliqués à des dépendances d'automata-lib (sans toucher à leur code source)."""

from __future__ import annotations

import cached_method as _cm

_PATCH_FLAG = "_automata_extensions_patched"


def patch_cached_method() -> bool:
    """
    Corrige le bug « Bound object has been garbage collected » de ``cached_method``.

    Problème
    --------
    ``cached_method.__get__`` renvoie un simple callable qui ne garde qu'une
    référence *faible* vers l'automate. Sur un objet temporaire sans nom, comme
    dans ``(d - d).isempty()``, l'automate peut être collecté entre l'accès à la
    méthode et son appel, d'où ``RuntimeError``.

    Solution
    --------
    ``__get__`` est remplacé par une version qui renvoie un callable refermé
    *fortement* sur l'instance le temps de l'appel. Le cache reste inchangé
    (référence faible, donc pas de cycle).

    Returns
    -------
    bool
        ``True`` si le patch vient d'être appliqué, ``False`` s'il l'était déjà.

    Complexity
    ----------
    O(1)
    """
    cls = _cm.cached_method
    if getattr(cls, _PATCH_FLAG, False):
        return False

    original_get = cls.__get__

    def __get__(self, instance, owner=None):
        method = original_get(self, instance, owner)
        if instance is None:
            return method

        def bound(*args, **kwargs):
            # ``instance`` est capturé par la fermeture : il reste vivant
            # tant que ce callable existe, donc pendant tout l'appel.
            return method(*args, **kwargs)

        for name in ("cache_info", "cache_clear", "cache_parameters"):
            if hasattr(method, name):
                setattr(bound, name, getattr(method, name))
        bound.__wrapped__ = method
        bound.__doc__ = getattr(method, "__doc__", None)
        bound.__name__ = getattr(method, "__name__", "cached_method")
        bound._keep_alive = instance  # référence forte explicite
        return bound

    cls.__get__ = __get__
    setattr(cls, _PATCH_FLAG, True)
    return True
