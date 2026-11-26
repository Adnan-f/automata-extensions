from automata_extensions.fa import ExtendedDFA


def test_isomorphic_to_self(d):
    assert d.is_isomorphic_to(d) is True


def test_isomorphic_to_renamed_copy():
    renamed = ExtendedDFA(
        states={"X", "Y", "Z"}, input_symbols={"a", "b"},
        transitions={
            "X": {"a": "Y", "b": "X"},
            "Y": {"a": "Z", "b": "Y"},
            "Z": {"a": "X", "b": "Z"},
        },
        initial_state="X", final_states={"X"},
    )

    def rebuild():
        return ExtendedDFA(
            states={"0", "1", "2"}, input_symbols={"a", "b"},
            transitions={
                "0": {"a": "1", "b": "0"},
                "1": {"a": "2", "b": "1"},
                "2": {"a": "0", "b": "2"},
            },
            initial_state="0", final_states={"0"},
        )

    assert rebuild().is_isomorphic_to(renamed) is True


def test_not_isomorphic_different_size(d):
    smaller = ExtendedDFA(
        states={"q0"}, input_symbols={"a", "b"},
        transitions={"q0": {"a": "q0", "b": "q0"}},
        initial_state="q0", final_states={"q0"},
    )
    assert d.is_isomorphic_to(smaller) is False


def test_not_isomorphic_different_finality():
    a = ExtendedDFA(
        states={"q0", "q1"}, input_symbols={"a"},
        transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}},
        initial_state="q0", final_states={"q1"},
    )
    b = ExtendedDFA(
        states={"q0", "q1"}, input_symbols={"a"},
        transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}},
        initial_state="q0", final_states={"q0"},
    )
    assert a.is_isomorphic_to(b) is False


def test_isomorphic_requires_same_alphabet(d):
    other = ExtendedDFA(
        states={"0", "1", "2"}, input_symbols={"x", "y"},
        transitions={
            "0": {"x": "1", "y": "0"},
            "1": {"x": "2", "y": "1"},
            "2": {"x": "0", "y": "2"},
        },
        initial_state="0", final_states={"0"},
    )
    assert d.is_isomorphic_to(other) is False
