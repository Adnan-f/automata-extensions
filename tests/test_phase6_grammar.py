import pytest

from automata_extensions.grammar import (Grammar, NotDerivableError, Production)


def test_from_string_basic_and_str_roundtrip():
    g = Grammar.from_string("S -> aS | b")
    assert g.start == "S"
    assert g.nonterminals == {"S"} and g.terminals == {"a", "b"}
    assert str(g) == "S -> aS | b"
    assert Grammar.from_string(str(g)) == g


@pytest.mark.parametrize("eps", ["ε", "λ", "()", ""])
def test_from_string_epsilon_spellings(eps):
    g = Grammar.from_string(f"S -> aS | {eps}")
    assert Production("S", ()) in g.productions
    assert str(g) == "S -> aS | ε"


def test_from_string_multiline_comments_and_start():
    g = Grammar.from_string("# commentaire\nS -> aA\n\nA -> bA | b", start="A")
    assert g.start == "A"
    assert g.nonterminals == {"S", "A"}
    assert str(g).splitlines()[0].startswith("A ->")


@pytest.mark.parametrize("bad", ["S aS", "ab -> a", "s -> a", "", "S -> aεb"])
def test_from_string_errors(bad):
    with pytest.raises(ValueError):
        Grammar.from_string(bad)


def test_validation_errors():
    with pytest.raises(ValueError):
        Grammar({"S"}, {"S"}, set(), "S")                  # N ∩ T non vide
    with pytest.raises(ValueError):
        Grammar({"S"}, {"a"}, set(), "X")                  # axiome inconnu
    with pytest.raises(ValueError):
        Grammar({"S"}, {"a"}, {Production("S", ("z",))}, "S")  # symbole inconnu
    with pytest.raises(ValueError):
        Grammar({"S"}, {"a"}, {Production("T", ("a",))}, "S")  # lhs inconnu


def test_linearity_classification():
    right = Grammar.from_string("S -> aS | b")
    left = Grammar.from_string("S -> Sa | b")
    cf = Grammar.from_string("S -> aSb | ε")
    mixed = Grammar.from_string("S -> aA | Ab\nA -> a")
    assert right.is_right_linear() and not right.is_left_linear()
    assert left.is_left_linear() and not left.is_right_linear()
    assert not cf.is_regular()
    assert not mixed.is_regular()
    assert Grammar.from_string("S -> a").is_regular()


def test_reverse_swaps_linearity():
    g = Grammar.from_string("S -> abS | c")
    assert g.reverse().is_left_linear()
    assert g.reverse().reverse() == g


def test_derive_right_linear():
    g = Grammar.from_string("S -> aS | b")
    step = g.derive("aab")
    assert step.sequence() == "S => aS => aaS => aab"
    assert step.word() == "aab"
    assert [str(r) for r in step.rules()] == ["S -> aS", "S -> aS", "S -> b"]
    assert step.is_complete()


def test_derive_left_linear():
    g = Grammar.from_string("S -> Sa | b")
    step = g.derive("baa")
    assert step.sequence() == "S => Sa => Saa => baa"
    assert step.word() == "baa"


def test_derive_epsilon_word_and_generates():
    g = Grammar.from_string("S -> aS | ε")
    assert g.derive("").sequence() == "S => ε"
    assert g.derive("").word() == ""
    assert g.generates("aaa") and not g.generates("ab")


def test_derive_not_derivable_and_non_regular():
    g = Grammar.from_string("S -> aS | b")
    with pytest.raises(NotDerivableError):
        g.derive("aa")
    with pytest.raises(NotDerivableError):
        g.derive("")
    with pytest.raises(ValueError):
        Grammar.from_string("S -> aSb | ε").derive("ab")


def test_derive_handles_unit_rule_cycles():
    g = Grammar.from_string("S -> A | a\nA -> S | b")
    assert g.generates("a") and g.generates("b") and not g.generates("c")


def test_partial_form_word_raises():
    g = Grammar.from_string("S -> aS | b")
    step = g.derive("ab")
    first = step.steps()[1]
    assert not first.is_complete()
    with pytest.raises(ValueError):
        first.word()


def test_parse_tree():
    g = Grammar.from_string("S -> aS | b")
    tree = g.derive("aab").parse_tree()
    assert tree.symbol == "S"
    assert tree.word() == "aab"
    assert tree.leaves() == ["a", "a", "b"]
    assert tree.depth() == 3
    dot = tree.to_dot()
    assert dot.startswith("digraph {") and dot.count("->") == 5
    assert str(tree).splitlines()[0] == "S"


def test_parse_tree_epsilon_leaf():
    tree = Grammar.from_string("S -> aS | ε").derive("a").parse_tree()
    assert tree.leaves() == ["a", "ε"] and tree.word() == "a"
