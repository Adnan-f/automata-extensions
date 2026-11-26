"""Régression : langage vide (trim / minimize / prefix_closed_sublanguage / brzozowski)."""
from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def _empty_dfa():
    return ExtendedDFA(states={"q0", "q1"}, input_symbols={"a"},
                       transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}},
                       initial_state="q0", final_states=set())


def test_trim_empty_language_keeps_initial_state():
    t = _empty_dfa().trim()
    assert t.states == {"q0"} and t.is_empty()


def test_minimize_empty_language_single_state():
    m = _empty_dfa().minimize()
    assert len(m.states) == 1 and m.is_empty()


def test_brzozowski_empty_language_single_state():
    b = _empty_dfa().brzozowski_minimize()
    assert len(b.states) == 1 and b.is_empty()


def test_prefix_closed_sublanguage_empty_language():
    assert _empty_dfa().prefix_closed_sublanguage().is_empty()


def test_trim_empty_nfa():
    nfa = ExtendedNFA(states={"p", "q"}, input_symbols={"a"},
                      transitions={"p": {"a": {"q"}}, "q": {}},
                      initial_state="p", final_states=set())
    assert nfa.trim().states == {"p"}


def test_trim_non_empty_unchanged_behaviour(d):
    assert d.trim().states == d.states
