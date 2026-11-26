from automata_extensions.fa import ExtendedDFA


def test_has_cycle_true(d):
    assert d.has_cycle() is True


def test_has_cycle_from_specific_state(d):
    assert d.has_cycle_from("0") is True


def test_no_cycle_acyclic():
    dfa = ExtendedDFA(
        states={"q0", "q1", "q2"}, input_symbols={"a"},
        transitions={"q0": {"a": "q1"}, "q1": {"a": "q2"}, "q2": {}},
        initial_state="q0", final_states={"q2"}, allow_partial=True,
    )
    assert dfa.has_cycle() is False


def test_self_loop_is_cycle():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states={"q0"},
    )
    assert dfa.has_cycle() is True


def test_is_empty_true_when_no_accessible_final():
    dfa = ExtendedDFA(
        states={"q0", "q1"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}, "q1": {"a": "q1"}},
        initial_state="q0", final_states={"q1"}, allow_partial=True,
    )
    assert dfa.is_empty() is True


def test_is_empty_false(d):
    assert d.is_empty() is False


def test_is_finite_true_acyclic_useful_part():
    dfa = ExtendedDFA(
        states={"q0", "q1", "q2"}, input_symbols={"a"},
        transitions={"q0": {"a": "q1"}, "q1": {"a": "q2"}, "q2": {}},
        initial_state="q0", final_states={"q1", "q2"}, allow_partial=True,
    )
    assert dfa.is_finite() is True


def test_is_finite_false_cycle_on_useful_states(d):
    assert d.is_finite() is False


def test_is_finite_true_when_empty():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states=set(), allow_partial=True,
    )
    assert dfa.is_finite() is True
    assert dfa.is_empty() is True
