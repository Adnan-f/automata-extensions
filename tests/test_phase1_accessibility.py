import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedGNFA


def test_accessible_states_all(d):
    assert d.accessible_states() == {"0", "1", "2"}


def test_is_accessible(d):
    assert d.is_accessible("2") is True


def test_inaccessible_state_excluded():
    dfa = ExtendedDFA(
        states={"q0", "q1", "unreachable"}, input_symbols={"a"},
        transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}, "unreachable": {"a": "unreachable"}},
        initial_state="q0", final_states={"q1"},
    )
    assert dfa.accessible_states() == {"q0", "q1"}
    assert dfa.is_accessible("unreachable") is False


def test_coaccessible_states_all(d):
    assert d.coaccessible_states() == {"0", "1", "2"}


def test_dead_state_not_coaccessible():
    dfa = ExtendedDFA(
        states={"q0", "q1", "dead"}, input_symbols={"a", "b"},
        transitions={
            "q0": {"a": "q1", "b": "dead"},
            "q1": {"a": "q1", "b": "q1"},
            "dead": {"a": "dead", "b": "dead"},
        },
        initial_state="q0", final_states={"q1"},
    )
    assert dfa.is_coaccessible("dead") is False
    assert dfa.is_coaccessible("q0") is True


def test_useful_states_and_trim():
    dfa = ExtendedDFA(
        states={"q0", "q1", "dead", "unreachable"}, input_symbols={"a", "b"},
        transitions={
            "q0": {"a": "q1", "b": "dead"},
            "q1": {"a": "q1", "b": "q1"},
            "dead": {"a": "dead", "b": "dead"},
            "unreachable": {"a": "unreachable", "b": "unreachable"},
        },
        initial_state="q0", final_states={"q1"}, allow_partial=True,
    )
    assert dfa.useful_states() == {"q0", "q1"}
    trimmed = dfa.trim()
    assert trimmed.states == {"q0", "q1"}
    assert trimmed.is_trim() is True
    assert dfa.is_trim() is False
    # trim() ne modifie pas l'automate d'origine
    assert dfa.states == {"q0", "q1", "dead", "unreachable"}


def test_trim_already_minimal(d):
    assert d.is_trim() is True
    assert d.trim().states == d.states


def test_induced_subautomaton_requires_initial(d):
    with pytest.raises(ValueError):
        d.induced_subautomaton({"1", "2"})


def test_induced_subautomaton_basic(d):
    sub = d.induced_subautomaton({"0", "1"})
    assert sub.states == {"0", "1"}
    assert sub.accepts_input("")


def test_gnfa_final_state_handled():
    from automata_extensions.fa import ExtendedDFA
    dfa = ExtendedDFA(
        states={"0", "1"}, input_symbols={"a"},
        transitions={"0": {"a": "1"}, "1": {"a": "1"}},
        initial_state="0", final_states={"1"},
    )
    g = ExtendedGNFA.from_dfa(dfa)
    assert g._final_states_set() == {g.final_state}
