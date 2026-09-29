from automata_extensions.fa import ExtendedDFA


def test_is_prefix_closed_false(d):
    assert d.is_prefix_closed() is False


def test_is_prefix_closed_true_universal():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states={"q0"},
    )
    assert dfa.is_prefix_closed() is True


def test_prefix_closed_sublanguage_contains_empty_word(d):
    sub = d.prefix_closed_sublanguage()
    assert sub.is_prefix_closed() is True
    assert sub.accepts_input("")


def test_prefix_closed_sublanguage_accepts_prefix_of_accepted_word(d):
    sub = d.prefix_closed_sublanguage()
    assert not d.accepts_input("aa")
    assert sub.accepts_input("aa")
