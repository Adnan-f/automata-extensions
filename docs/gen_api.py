#!/usr/bin/env python
"""Génère docs/API.md (méthodes, disponibilité, résumé, complexité) depuis les docstrings.

    python docs/gen_api.py            # écrit docs/API.md
    python docs/gen_api.py --check    # ne génère rien : échoue si une méthode publique
                                      # n'a pas de docstring (les complexités manquantes
                                      # sont seulement signalées)

La source de vérité reste le code : ce fichier n'est jamais édité à la main.
"""

from __future__ import annotations

import inspect
import re
import sys
from collections import defaultdict
from pathlib import Path

from automata_extensions import ExtendedDFA, ExtendedGNFA, ExtendedNFA
from automata_extensions.algebra import TransitionMonoid
from automata_extensions.equations import EquationSystem
from automata_extensions.exercises import Exercise
from automata_extensions.grammar import DerivationStep, Grammar, ParseTree
from automata_extensions.regex import Regex

OUT = Path(__file__).resolve().parent / "API.md"
FA_CLASSES = [(ExtendedDFA, "DFA"), (ExtendedNFA, "NFA"), (ExtendedGNFA, "GNFA")]
OTHER_CLASSES = [Grammar, DerivationStep, ParseTree, Regex, EquationSystem, TransitionMonoid, Exercise]
COMPLEXITY = re.compile(r"Complexity\n-+\n(.*?)(?:\n\s*\n|\Z)", re.S)


def _callable(cls, name):
    raw = inspect.getattr_static(cls, name)
    if isinstance(raw, property):
        return raw.fget
    if isinstance(raw, (classmethod, staticmethod)):
        return raw.__func__
    return raw if inspect.isfunction(raw) else None


def _doc(func):
    doc = inspect.getdoc(func) or ""
    lines = [ln for ln in doc.splitlines() if ln.strip()]
    summary = lines[0].strip() if lines else ""
    match = COMPLEXITY.search(doc)
    return summary, (" ".join(match.group(1).split()) if match else "")


def _owner(cls, name):
    for klass in cls.__mro__:
        if name in klass.__dict__:
            return klass
    return None


def _cell(text):
    return text.replace("|", "\\|") or "—"


def collect():
    """module -> nom -> {'classes': {...}, 'func': ...}."""
    modules = defaultdict(dict)
    for cls, label in FA_CLASSES:
        for name in dir(cls):
            if name.startswith("_"):
                continue
            owner = _owner(cls, name)
            if owner is None or not owner.__module__.startswith("automata_extensions"):
                continue
            func = _callable(owner, name)
            if func is None:
                continue
            entry = modules[owner.__module__].setdefault(name, {"classes": set(), "func": func})
            entry["classes"].add(label)
    return modules


def render(modules) -> str:
    out = ["# Référence de l'API", "",
           "Généré par `python docs/gen_api.py` à partir des docstrings — ne pas éditer à la main.",
           "La colonne *Disponible sur* indique les classes (DFA, NFA, GNFA) qui possèdent la méthode.", ""]
    missing_doc, missing_cx = [], []
    for module in sorted(modules):
        short = module.replace("automata_extensions.", "")
        out += [f"## `{short}`", "", "| Méthode | Disponible sur | Résumé | Complexité |", "|---|---|---|---|"]
        for name in sorted(modules[module]):
            entry = modules[module][name]
            summary, complexity = _doc(entry["func"])
            if not summary:
                missing_doc.append(f"{short}.{name}")
            elif not complexity:
                missing_cx.append(f"{short}.{name}")
            order = [lbl for _, lbl in FA_CLASSES if lbl in entry["classes"]]
            out.append(f"| `{name}` | {', '.join(order)} | {_cell(summary)} | {_cell(complexity)} |")
        out.append("")
    out += ["## Autres classes", ""]
    for cls in OTHER_CLASSES:
        out += [f"### `{cls.__name__}`", "", "| Méthode | Résumé | Complexité |", "|---|---|---|"]
        for name in sorted(n for n in dir(cls) if not n.startswith("_")):
            func = _callable(cls, name)
            if func is None or getattr(func, "__module__", "") is None:
                continue
            if not getattr(func, "__module__", "").startswith("automata_extensions"):
                continue
            summary, complexity = _doc(func)
            if not summary:
                missing_doc.append(f"{cls.__name__}.{name}")
            out.append(f"| `{name}` | {_cell(summary)} | {_cell(complexity)} |")
        out.append("")
    render.missing_doc, render.missing_cx = missing_doc, missing_cx
    return "\n".join(out) + "\n"


def main(argv) -> int:
    text = render(collect())
    missing_doc, missing_cx = render.missing_doc, render.missing_cx
    if "--check" in argv:
        print(f"méthodes publiques sans docstring : {len(missing_doc)}")
        for item in missing_doc:
            print(f"  - {item}")
        print(f"méthodes sans section « Complexity » (information) : {len(missing_cx)}")
        return 1 if missing_doc else 0
    OUT.write_text(text, encoding="utf-8")
    print(f"{OUT} écrit ({text.count(chr(10))} lignes) ; "
          f"{len(missing_doc)} sans docstring, {len(missing_cx)} sans complexité")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
