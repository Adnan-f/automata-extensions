#!/usr/bin/env python
"""Génère les figures du README dans docs/img/ avec la bibliothèque elle-même.

    python docs/make_figures.py

Nécessite le binaire Graphviz (`dot`) pour les SVG. Les animations HTML sont produites en Python pur.
"""

from __future__ import annotations

from pathlib import Path

import graphviz

from automata_extensions import ExtendedDFA, ExtendedNFA, Grammar

IMG = Path(__file__).resolve().parent / "img"
IMG.mkdir(exist_ok=True)

d = ExtendedDFA(
    states={"0", "1", "2"}, input_symbols={"a", "b"},
    transitions={"0": {"a": "1", "b": "0"}, "1": {"a": "2", "b": "1"}, "2": {"a": "0", "b": "2"}},
    initial_state="0", final_states={"0"},
)
abb = ExtendedDFA.from_regex("(a|b)*abb").residual_automaton()      # états q0..q3 lisibles
thompson = ExtendedNFA.from_regex("(a|b)*abb")
tree = Grammar.from_string("S -> aS | b").derive("aab").parse_tree()

d.save(IMG / "dfa_mod3.svg")
abb.save(IMG / "dfa_abb.svg")
thompson.save(IMG / "thompson_abb.svg")
(IMG / "parse_tree.svg").write_bytes(graphviz.Source(tree.to_dot()).pipe(format="svg"))
d.animate("aab", path=IMG / "animation_dfa.html")
thompson.animate("abb", path=IMG / "animation_nfa.html")

for path in sorted(IMG.iterdir()):
    print(f"{path.relative_to(IMG.parent.parent)}  ({path.stat().st_size} octets)")
