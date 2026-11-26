from automata_extensions.fa import ExtendedDFA


def test_is_complete_true(d):
    assert d.is_complete() is True


def test_complete_noop_if_already_complete(d):
    d2 = d.complete()
    assert d2.states == d.states
    assert d2.is_complete() is True


def test_incomplete_dfa_gets_trap():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a", "b"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states={"q0"}, allow_partial=True,
    )
    assert dfa.is_complete() is False
    completed = dfa.complete()
    assert completed.is_complete() is True
    assert completed.states == {"q0", "__trap__"}
    assert completed.accepts_input("a")
    assert not completed.accepts_input("b")
    # ne modifie pas l'original
    assert dfa.is_complete() is False


def test_complete_trap_name_collision():
    dfa = ExtendedDFA(
        states={"q0", "q1", "__trap__"}, input_symbols={"a", "b"},
        transitions={
            "q0": {"a": "q1"},
            "q1": {"a": "q1", "b": "q1"},
            "__trap__": {"a": "__trap__", "b": "__trap__"},
        },
        initial_state="q0", final_states={"q1"}, allow_partial=True,
    )
    assert dfa.is_complete() is False  # q0 manque 'b'
    completed = dfa.complete()
    assert completed.is_complete() is True
    assert "__trap___1" in completed.states


def test_single_state_dfa_already_complete():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states={"q0"},
    )
    assert dfa.is_complete() is True
    assert dfa.complete().states == {"q0"}
