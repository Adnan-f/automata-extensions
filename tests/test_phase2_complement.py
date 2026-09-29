from automata_extensions.fa import ExtendedDFA


def test_complement_basic(d):
    c = d.complement()
    assert c.accepts_input("a") is True
    assert c.accepts_input("") is False


def test_complement_of_complement_equivalent(d):
    assert d.complement().complement().is_equivalent(d)


def test_complement_on_incomplete_dfa():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a", "b"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states={"q0"}, allow_partial=True,
    )
    c = dfa.complement()
    assert c.accepts_input("b") is True
    assert c.accepts_input("a") is False


def test_is_universal_true():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states={"q0"},
    )
    assert dfa.is_universal() is True


def test_is_universal_false(d):
    assert d.is_universal() is False


def test_is_universal_empty_language():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states=set(),
    )
    assert dfa.is_universal() is False
