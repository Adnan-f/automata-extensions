import random

import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedGNFA, ExtendedNFA
from automata_extensions.grammar import NotDerivableError


def test_pdf_example_to_grammar_and_derivation(d):
    g = d.to_grammar()
    assert type(g).__name__ == "Grammar"
    assert str(g) == "0 -> a1 | b0 | ε\n1 -> a2 | b1\n2 -> a0 | b2"
    step = d.derivation_tree("aaa")
    assert step.sequence() == "0 => a1 => aa2 => aaa0 => aaa"      # valeur du PDF
    assert (step.word(), step.sequence()) == ("aaa", "0 => a1 => aa2 => aaa0 => aaa")


def test_derivation_tree_rejected_word(d):
    with pytest.raises(NotDerivableError):
        d.derivation_tree("a")


def test_from_grammar_string_corrects_pdf_example():
    # Le PDF indique False pour "aab" : c'est une erreur, S => aS => aaS => aab.
    nfa = ExtendedNFA.from_grammar_string("S -> aS | b")
    assert nfa.accepts_input("aab") is True
    assert nfa.accepts_input("b") and not nfa.accepts_input("aa") and not nfa.accepts_input("")


def test_from_grammar_multi_terminal_rules():
    nfa = ExtendedNFA.from_grammar_string("S -> abS | c")
    assert nfa.accepts_input("ababc") and nfa.accepts_input("c")
    assert not nfa.accepts_input("abab") and not nfa.accepts_input("abc" + "b")


def test_from_grammar_left_linear():
    nfa = ExtendedNFA.from_grammar_string("S -> Sa | b")        # b a*
    assert nfa.accepts_input("baa") and nfa.accepts_input("b")
    assert not nfa.accepts_input("ab") and not nfa.accepts_input("")


def test_from_grammar_epsilon_and_unit_rules():
    nfa = ExtendedNFA.from_grammar_string("S -> A | a\nA -> bA | ε")
    assert nfa.accepts_input("") and nfa.accepts_input("bbb") and nfa.accepts_input("a")
    assert not nfa.accepts_input("ab")


def test_from_grammar_rejects_non_regular():
    with pytest.raises(ValueError):
        ExtendedNFA.from_grammar_string("S -> aSb | ε")


def test_to_grammar_gnfa_not_supported(d):
    with pytest.raises(TypeError):
        ExtendedGNFA.from_dfa(d).to_grammar()


def test_to_grammar_name_collision_between_state_and_symbol():
    dfa = ExtendedDFA(
        states={"a", "b"}, input_symbols={"a", "b"},
        transitions={"a": {"a": "b", "b": "a"}, "b": {"a": "a", "b": "b"}},
        initial_state="a", final_states={"b"},
    )
    g = dfa.to_grammar()
    assert not (g.nonterminals & g.terminals)
    assert g.to_nfa().determinize().is_equivalent(dfa)


def test_to_grammar_with_epsilon_transitions(n):
    g = n.to_grammar()
    assert g.to_nfa().determinize().is_equivalent(n.determinize())
    for w in ("", "a", "aa", "ab", "abb", "b", "ba"):
        assert g.generates(w) == n.accepts_input(w)


def _random_dfa(rng, size):
    states = [str(i) for i in range(size)]
    return ExtendedDFA(
        states=set(states), input_symbols={"a", "b"},
        transitions={s: {a: rng.choice(states) for a in "ab"} for s in states},
        initial_state="0", final_states={s for s in states if rng.random() < 0.4})


@pytest.mark.parametrize("seed", range(25))
def test_random_grammar_roundtrips(seed):
    rng = random.Random(seed)
    dfa = _random_dfa(rng, rng.randint(1, 5))
    right, left = dfa.to_grammar(), dfa.to_left_grammar()
    assert right.is_right_linear() and left.is_left_linear()
    assert right.to_nfa().determinize().is_equivalent(dfa)
    assert left.to_nfa().determinize().is_equivalent(dfa)
    # la dérivation redonne le mot, et existe exactement pour les mots acceptés
    for w in ["", "a", "b", "ab", "ba", "aab", "abba", "bbbb"]:
        assert right.generates(w) == dfa.accepts_input(w) == left.generates(w)
        if dfa.accepts_input(w):
            assert dfa.derivation_tree(w).word() == w
            assert left.derive(w).word() == w
            assert dfa.derivation_tree(w).parse_tree().word() == w
