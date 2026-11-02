import random

import pytest

from automata_extensions.algebra import TransitionMonoid
from automata_extensions.fa import ExtendedDFA

WORDS = ["", "a", "b", "aa", "ab", "ba", "bb", "aab", "aba", "abb", "bab", "aaa", "abab", "bbba"]


def _random_dfa(rng):
    size = rng.randint(1, 5)
    st = [str(i) for i in range(size)]
    return ExtendedDFA(states=set(st), input_symbols={"a", "b"},
                       transitions={s: {a: rng.choice(st) for a in "ab"} for s in st},
                       initial_state="0", final_states={s for s in st if rng.random() < 0.4})


# ------------------------------------------------------------ résiduels
def test_residual_automaton_pdf_value(d):
    r = d.residual_automaton()
    assert sorted(map(str, r.states)) == ["q0", "q1", "q2"]
    assert r.is_equivalent(d) and r.is_complete() and r.is_minimal()


def test_residuals_representatives(d):
    assert d.residuals() == {"q0": "", "q1": "a", "q2": "aa"}


def test_residual_automaton_merges_equivalent_states():
    dfa = ExtendedDFA(states={"s", "x", "y"}, input_symbols={"a"},
                      transitions={"s": {"a": "x"}, "x": {"a": "y"}, "y": {"a": "x"}},
                      initial_state="s", final_states={"x", "y"})
    assert len(dfa.residual_automaton().states) == 2          # x ~ y


def test_residual_automaton_empty_language():
    empty = ExtendedDFA(states={"q0", "q1"}, input_symbols={"a"},
                        transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}},
                        initial_state="q0", final_states=set())
    r = empty.residual_automaton()
    assert r.states == {"q0"} and r.is_empty()


@pytest.mark.parametrize("seed", range(25))
def test_random_residuals_are_left_quotients(seed):
    dfa = _random_dfa(random.Random(seed))
    r = dfa.residual_automaton()
    assert r.is_equivalent(dfa)
    assert r.is_isomorphic_to(dfa.minimize())
    for name, word in dfa.residuals().items():
        params = dict(r.input_parameters)
        params["initial_state"] = name
        state_language = ExtendedDFA(**params)
        assert state_language.is_equivalent(dfa.left_quotient_word(word)), (name, word)


# ------------------------------------------------------------ monoïde
def test_syntactic_monoid_pdf_value(d):
    m = d.syntactic_monoid()
    assert isinstance(m, TransitionMonoid) and len(m) == 3
    assert [m.shortest_word(e) for e in m] == ["", "a", "aa"]      # Z/3Z


def test_syntactic_monoid_of_counting_language_is_a_group(d):
    m = d.syntactic_monoid()
    assert m.is_group() and m.is_commutative()
    assert m.idempotents() == [m.identity]
    assert not m.is_aperiodic() and not d.is_star_free()


def test_star_free_classification():
    assert ExtendedDFA.from_regex("(a|b)*abb").is_star_free()
    assert ExtendedDFA.from_regex("(ab)*", input_symbols={"a", "b"}).is_star_free()
    assert not ExtendedDFA.from_regex("(aa)*", input_symbols={"a", "b"}).is_star_free()
    assert ExtendedDFA.from_regex("a*", input_symbols={"a"}).is_star_free()


def test_monoid_element_of_and_multiply(d):
    m = d.syntactic_monoid()
    assert m.element_of("") == m.identity
    assert m.element_of("b") == m.identity                         # b est neutre pour d
    assert m.element_of("aaa") == m.identity
    assert m.multiply(m.element_of("a"), m.element_of("aa")) == m.identity
    assert m.shortest_word(m.element_of("abab")) == "aa"
    with pytest.raises(ValueError):
        m.element_of("z")


def test_transition_monoid_vs_syntactic_with_redundant_states():
    # x et y équivalents : le monoïde de transitions garde 3 états, le syntaxique en fusionne 2.
    dfa = ExtendedDFA(states={"s", "x", "y"}, input_symbols={"a"},
                      transitions={"s": {"a": "x"}, "x": {"a": "y"}, "y": {"a": "x"}},
                      initial_state="s", final_states={"x", "y"})
    assert len(dfa.transition_monoid().states) == 3
    assert len(dfa.syntactic_monoid().states) == 2


def test_monoid_empty_and_universal_languages():
    empty = ExtendedDFA(states={"q0"}, input_symbols={"a", "b"},
                        transitions={"q0": {"a": "q0", "b": "q0"}},
                        initial_state="q0", final_states=set())
    assert len(empty.syntactic_monoid()) == 1
    assert empty.is_star_free()


@pytest.mark.parametrize("seed", range(25))
def test_random_monoid_is_homomorphism_and_syntactic_congruence(seed):
    dfa = _random_dfa(random.Random(seed))
    m = dfa.syntactic_monoid()
    # homomorphisme : element(uv) = element(u) puis element(v)
    for u in WORDS:
        for v in WORDS[:6]:
            assert m.element_of(u + v) == m.multiply(m.element_of(u), m.element_of(v))
    # fermeture : le produit de deux éléments reste dans le monoïde
    elements = list(m)
    for f in elements:
        for g in elements:
            assert m.multiply(f, g) in m
    # congruence syntaxique : même élément => indiscernables dans tous les contextes
    for u in WORDS:
        for v in WORDS:
            if m.element_of(u) == m.element_of(v):
                for x in WORDS[:7]:
                    for y in WORDS[:7]:
                        assert dfa.accepts_input(x + u + y) == dfa.accepts_input(x + v + y)
    # le monoïde syntaxique n'est jamais plus grand que celui du DFA complet non minimisé
    assert len(m) <= len(dfa.transition_monoid())
