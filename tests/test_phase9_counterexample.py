import itertools
import random

import pytest
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from automata_extensions.fa import ExtendedDFA, ExtendedGNFA, ExtendedNFA


def _rand_dfa(rng, size):
    st = [str(i) for i in range(size)]
    return ExtendedDFA(states=set(st), input_symbols={"a", "b"},
                       transitions={s: {a: rng.choice(st) for a in "ab"} for s in st},
                       initial_state="0", final_states={s for s in st if rng.random() < 0.4})


def _rand_nfa(rng, size):
    st = [str(i) for i in range(size)]
    trans = {}
    for s in st:
        row = {}
        for a in ("a", "b", ""):
            targets = {t for t in st if rng.random() < 0.25}
            if targets:
                row[a] = targets
        trans[s] = row
    return ExtendedNFA(states=set(st), input_symbols={"a", "b"}, transitions=trans,
                       initial_state="0", final_states={s for s in st if rng.random() < 0.4})


def _shortlex(alphabet, max_len):
    for length in range(max_len + 1):
        for letters in itertools.product(sorted(alphabet), repeat=length):
            yield "".join(letters)


# ------------------------------------------------------------- shortest_word
def test_shortest_word_basic(d):
    assert d.shortest_word() == ""                                   # d accepte ε
    assert ExtendedDFA.from_regex("(a|b)*abb").shortest_word() == "abb"
    assert ExtendedDFA.from_regex("b|aa", input_symbols={"a", "b"}).shortest_word() == "b"


def test_shortest_word_is_lexicographically_smallest_among_shortest():
    assert ExtendedDFA.from_regex("(a|b)(a|b)").shortest_word() == "aa"
    assert ExtendedDFA.from_regex("(b|a)b*").shortest_word() == "a"


def test_shortest_word_empty_language_and_nfa(n):
    empty = ExtendedDFA(states={"q"}, input_symbols={"a"}, transitions={"q": {"a": "q"}},
                        initial_state="q", final_states=set())
    assert empty.shortest_word() is None
    assert n.shortest_word() == ""                                   # p -ε-> r, et r est final


def test_shortest_word_partial_dfa_and_gnfa(d):
    partial = ExtendedDFA(states={"q0", "q1"}, input_symbols={"a", "b"},
                          transitions={"q0": {"b": "q1"}, "q1": {}}, initial_state="q0",
                          final_states={"q1"}, allow_partial=True)
    assert partial.shortest_word() == "b"
    with pytest.raises(TypeError):
        ExtendedGNFA.from_dfa(d).shortest_word()


# --------------------------------------------------------- distinguishing_word
def test_distinguishing_word_equivalent_returns_none(d):
    assert d.distinguishing_word(d) is None
    assert d.distinguishing_word(d.minimize()) is None
    assert d.distinguishing_word(d.brzozowski_minimize()) is None


def test_distinguishing_word_known_values(d):
    assert d.distinguishing_word(d.complement()) == ""               # le mot vide départage
    other = ExtendedDFA.count_mod({"a", "b"}, 3, remainders={1})
    assert d.distinguishing_word(other) == ""
    abb = ExtendedDFA.from_regex("(a|b)*abb")
    assert abb.distinguishing_word(ExtendedDFA.from_regex("(a|b)*ab")) == "ab"


def test_distinguishing_word_witness_really_distinguishes(d):
    other = ExtendedDFA.from_regex("(a|b)*aba", input_symbols={"a", "b"})
    w = d.distinguishing_word(other)
    assert d.accepts_input(w) != other.accepts_input(w)


def test_distinguishing_word_different_alphabets():
    only_a = ExtendedDFA.from_regex("a*", input_symbols={"a"})
    over_ab = ExtendedDFA.from_regex("a*", input_symbols={"a", "b"})
    everything = ExtendedDFA.from_regex("(a|b)*", input_symbols={"a", "b"})
    assert only_a.distinguishing_word(over_ab) is None               # b est rejeté des deux côtés
    assert only_a.distinguishing_word(everything) == "b"
    assert everything.distinguishing_word(only_a) == "b"


def test_distinguishing_word_accepts_pure_automata_lib_objects(d, n):
    pure_dfa = DFA(**d.input_parameters)
    pure_nfa = NFA(**n.input_parameters)
    assert d.distinguishing_word(pure_dfa) is None
    assert n.distinguishing_word(pure_nfa) is None
    assert d.distinguishing_word(pure_nfa) is not None
    assert n.distinguishing_word(d) == d.distinguishing_word(n)


def test_distinguishing_word_errors(d):
    with pytest.raises(TypeError):
        d.distinguishing_word(ExtendedGNFA.from_dfa(d))
    with pytest.raises(TypeError):
        d.distinguishing_word("not an automaton")


@pytest.mark.parametrize("seed", range(60))
def test_random_distinguishing_word_matches_brute_force(seed):
    rng = random.Random(seed)
    make = lambda: (_rand_nfa if rng.random() < 0.5 else _rand_dfa)(rng, rng.randint(1, 3))
    x, y = make(), make()
    witness = x.distinguishing_word(y)
    expected = next((w for w in _shortlex("ab", 8) if x.accepts_input(w) != y.accepts_input(w)), None)
    assert witness == expected, (witness, expected)
    # None  <=>  langages égaux (vérifié indépendamment par l'équivalence de DFA)
    to_dfa = lambda fa: fa.determinize() if fa._nondeterministic else fa
    assert (witness is None) == to_dfa(x).is_equivalent(to_dfa(y))


@pytest.mark.parametrize("seed", range(40))
def test_random_shortest_word_matches_brute_force(seed):
    rng = random.Random(seed)
    fa = (_rand_nfa if seed % 2 else _rand_dfa)(rng, rng.randint(1, 3))
    expected = next((w for w in _shortlex("ab", 8) if fa.accepts_input(w)), None)
    assert fa.shortest_word() == expected
