import random

import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedGNFA, ExtendedNFA

WORDS = ["", "a", "b", "aa", "ab", "ba", "bb", "aab", "aba", "abb", "bab", "aaa", "abab", "bbba"]


def test_pdf_values(d):
    assert d.left_quotient_word("a").accepts_input("aa") is True
    assert d.right_quotient_word("a").accepts_input("aa") is True


def test_quotient_by_empty_word_is_identity_language(d):
    assert d.left_quotient_word("").is_equivalent(d)
    assert d.right_quotient_word("").is_equivalent(d)


def test_quotient_does_not_modify_original(d):
    before = (d.states, d.initial_state, d.final_states)
    d.left_quotient_word("a")
    d.right_quotient_word("a")
    assert (d.states, d.initial_state, d.final_states) == before


def test_left_quotient_blocking_word_gives_empty_language():
    partial = ExtendedDFA(states={"q0", "q1"}, input_symbols={"a", "b"},
                          transitions={"q0": {"a": "q1"}, "q1": {}}, initial_state="q0",
                          final_states={"q1"}, allow_partial=True)
    assert partial.left_quotient_word("b").is_empty()
    assert partial.left_quotient_word("aa").is_empty()
    assert partial.left_quotient_word("zzz").is_empty()


def test_quotient_nfa_with_epsilon(n):
    lq = n.left_quotient_word("a")
    assert isinstance(lq, ExtendedNFA)
    for u in WORDS:
        assert lq.accepts_input(u) == n.accepts_input("a" + u)


def test_quotient_gnfa_not_supported(d):
    g = ExtendedGNFA.from_dfa(d)
    with pytest.raises(TypeError):
        g.left_quotient_word("a")
    with pytest.raises(TypeError):
        g.right_quotient_word("a")


def _random_dfa(rng):
    size = rng.randint(1, 5)
    st = [str(i) for i in range(size)]
    return ExtendedDFA(states=set(st), input_symbols={"a", "b"},
                       transitions={s: {a: rng.choice(st) for a in "ab"} for s in st},
                       initial_state="0", final_states={s for s in st if rng.random() < 0.4})


def _random_nfa(rng):
    size = rng.randint(1, 5)
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


@pytest.mark.parametrize("seed", range(30))
@pytest.mark.parametrize("kind", ["dfa", "nfa"])
def test_random_quotients_match_definition(seed, kind):
    rng = random.Random(seed)
    fa = _random_dfa(rng) if kind == "dfa" else _random_nfa(rng)
    for w in ["", "a", "b", "ab", "ba", "aab"]:
        lq, rq = fa.left_quotient_word(w), fa.right_quotient_word(w)
        for u in WORDS:
            assert lq.accepts_input(u) == fa.accepts_input(w + u), ("left", w, u)
            assert rq.accepts_input(u) == fa.accepts_input(u + w), ("right", w, u)
