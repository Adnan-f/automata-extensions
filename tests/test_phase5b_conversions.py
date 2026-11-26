import random

import pytest
from automata.fa.nfa import NFA

from automata_extensions.fa import ExtendedDFA, ExtendedNFA
from automata_extensions.regex import parse

REGEXES = ["a", "ab", "a|b", "a*", "(a|b)*abb", "a?b+", "(ab|ba)*", "a*b*|b*a*", "()",
           "(a|b)*a(a|b)", "b*(ab*ab*a)*b*"]


def _pure(regex, alphabet):
    """Référence : automata-lib pur."""
    return ExtendedDFA.from_nfa(NFA.from_regex(regex, input_symbols=alphabet))


@pytest.mark.parametrize("regex", REGEXES)
def test_to_dfa_equivalent_to_automata_lib(regex):
    alphabet = {"a", "b"}
    mine = parse(regex).to_dfa(alphabet)
    assert mine.is_complete()
    assert mine.is_equivalent(_pure(regex, alphabet))


@pytest.mark.parametrize("regex", REGEXES)
def test_thompson_equivalent_to_automata_lib(regex):
    alphabet = {"a", "b"}
    mine = ExtendedNFA.from_regex(regex, input_symbols=alphabet)
    assert mine.determinize().is_equivalent(_pure(regex, alphabet))


@pytest.mark.parametrize("regex", REGEXES)
def test_glushkov_equivalent_and_epsilon_free(regex):
    alphabet = {"a", "b"}
    nfa = parse(regex).to_glushkov_nfa(alphabet)
    assert all("" not in row for row in nfa.transitions.values())
    assert nfa.determinize().is_equivalent(_pure(regex, alphabet))


def test_thompson_structure():
    assert len(ExtendedNFA.from_regex("a").states) == 2
    assert len(ExtendedNFA.from_regex("ab").states) == 4
    assert len(ExtendedNFA.from_regex("a|b").states) == 6
    assert len(ExtendedNFA.from_regex("a*").states) == 4
    assert len(ExtendedNFA.from_regex("(a|b)*abb").states) == 14
    nfa = ExtendedNFA.from_regex("(a|b)*abb")
    assert len(nfa.final_states) == 1
    for row in nfa.transitions.values():          # <= 2 transitions sortantes par état
        assert sum(len(t) for t in row.values()) <= 2


def test_thompson_accepts_regex_ast_and_checks_alphabet():
    nfa = ExtendedNFA.from_regex(parse("ab*"), input_symbols={"a", "b", "c"})
    assert nfa.accepts_input("abbb") and not nfa.accepts_input("c")
    with pytest.raises(ValueError):
        ExtendedNFA.from_regex("abc", input_symbols={"a", "b"})


def test_dfa_from_regex_class_and_alphabet():
    dfa = ExtendedDFA.from_regex("a(b|c)*", input_symbols={"a", "b", "c"})
    assert type(dfa) is ExtendedDFA
    assert dfa.accepts_input("abcb") and not dfa.accepts_input("b")
    with pytest.raises(ValueError):
        ExtendedDFA.from_regex("abc", input_symbols={"a"})


def test_derivative_dfa_is_finite_and_small():
    # (a|b)*abb : automate minimal classique à 4 états
    dfa = parse("(a|b)*abb").to_dfa()
    assert len(dfa.states) == 4
    assert dfa.is_minimal()


def test_empty_language_regex_dfa():
    from automata_extensions.regex import EMPTY
    dfa = EMPTY.to_dfa({"a"})
    assert dfa.is_empty()


def test_glushkov_positions_textbook():
    r = parse("(a|b)*abb")
    assert r.positions() == {1: "a", 2: "b", 3: "a", 4: "b", 5: "b"}
    assert r.firstpos() == {1, 2, 3}
    assert r.lastpos() == {5}
    assert r.followpos() == {
        1: {1, 2, 3}, 2: {1, 2, 3}, 3: {4}, 4: {5}, 5: set()}
    assert len(r.to_glushkov_nfa().states) == 6


def _random_dfa(rng, n):
    states = [str(i) for i in range(n)]
    transitions = {s: {a: rng.choice(states) for a in "ab"} for s in states}
    finals = {s for s in states if rng.random() < 0.4}
    return ExtendedDFA(states=set(states), input_symbols={"a", "b"},
                       transitions=transitions, initial_state="0", final_states=finals)


@pytest.mark.parametrize("seed", range(25))
def test_random_roundtrip_all_regex_methods(seed):
    """Sur des DFA aléatoires, chaque méthode DFA->regex redonne le même langage."""
    rng = random.Random(seed)
    dfa = _random_dfa(rng, rng.randint(1, 5))
    methods = ["to_regex", "to_regex_arden", "to_regex_optimum", "to_regex_arden_optimum"]
    for name in methods:
        regex = getattr(dfa, name)()
        if dfa.is_empty():
            assert regex is None or name in ("to_regex", "to_regex_arden")
            continue
        assert regex is not None
        assert _pure(regex, {"a", "b"}).is_equivalent(dfa), (name, regex)
