"""Arbres de dérivation de grands mots : aucune opération ne doit dépendre de la récursion."""

import dataclasses
import sys

import pytest

from automata_extensions.grammar import Grammar, ParseTree
from automata_extensions.grammar.grammar import _Node

N = max(4000, 3 * sys.getrecursionlimit())           # bien au-delà de la limite de récursion


def _tree(grammar_text, word):
    return Grammar.from_string(grammar_text).derive(word).parse_tree()


def test_deep_right_linear_tree_supports_every_operation():
    tree = _tree("S -> aS | b", "a" * N + "b")
    assert tree.leaves() == ["a"] * N + ["b"] and tree.word() == "a" * N + "b"
    assert tree.depth() == N + 1
    lines = str(tree).splitlines()
    assert len(lines) == 2 * N + 2 and lines[0] == "S" and lines[-1] == "  " * (N + 1) + "b"
    dot = tree.to_dot()
    assert dot.count("->") == 2 * N + 1 and dot.count("[label=") == 2 * N + 2


def test_deep_left_linear_tree():
    tree = _tree("S -> Sa | b", "b" + "a" * N)
    assert tree.depth() == N + 1 and tree.word() == "b" + "a" * N


def test_deep_tree_ending_with_epsilon():
    tree = _tree("S -> aS | ε", "a" * N)
    assert tree.leaves() == ["a"] * N + ["ε"] and tree.word() == "a" * N


def test_structural_equality_and_hash_on_deep_trees():
    t1 = _tree("S -> aS | b | c", "a" * N + "b")
    t2 = _tree("S -> aS | b | c", "a" * N + "b")
    other = _tree("S -> aS | b | c", "a" * N + "c")
    assert t1 == t2 and t1 is not t2 and hash(t1) == hash(t2)
    assert t1 != other
    assert hash(t1) != hash(other)                            # le hachage tient compte des fils, pas seulement de la racine
    assert len({t1, t2, other}) == 2                          # utilisable comme clé d'ensemble


def test_equality_with_other_types_and_shared_subtrees():
    leaf = ParseTree("a")
    shared = ParseTree("S", (leaf, leaf))                      # le même objet deux fois
    assert shared == ParseTree("S", (ParseTree("a"), ParseTree("a")))
    assert shared != ParseTree("S", (leaf,)) and shared != ParseTree("T", (leaf, leaf))
    assert (leaf == 3) is False and leaf != "a"


def test_single_leaf_tree():
    leaf = ParseTree("x")
    assert leaf.depth() == 0 and leaf.leaves() == ["x"] and str(leaf) == "x"
    assert "->" not in leaf.to_dot()


def test_wide_tree_and_freeze_preserves_order():
    root = _Node("S")
    root.children = [_Node(str(i)) for i in range(N)]
    frozen = root.freeze()
    assert frozen.depth() == 1 and frozen.leaves() == [str(i) for i in range(N)]
    assert isinstance(frozen.children, tuple)


def test_repr_is_short_and_trees_are_immutable():
    tree = _tree("S -> aS | b", "a" * N + "b")
    assert repr(tree) == "ParseTree('S', 2 fils)"
    with pytest.raises(dataclasses.FrozenInstanceError):
        tree.symbol = "T"


def test_dot_numbers_nodes_in_preorder_and_links_each_node_once():
    dot = _tree("S -> aS | b", "ab").to_dot()
    assert 'n0 [label="S" shape=circle]' in dot and "n0 -> n1" in dot and "n0 -> n2" in dot
    assert dot.count("->") == dot.count("[label=") - 1
