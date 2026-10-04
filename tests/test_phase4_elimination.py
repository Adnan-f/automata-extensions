def test_remove_epsilon_transitions_preserves_acceptance(n):
    n2 = n.remove_epsilon_transitions()
    assert "" not in n2.input_symbols
    for word in ("a", "aa", "b", "aab", "aba"):
        assert n2.accepts_input(word) == n.accepts_input(word)


def test_remove_epsilon_transitions_no_epsilon_to_begin_with():
    from automata_extensions.fa import ExtendedNFA
    nfa = ExtendedNFA(
        states={"q0", "q1"}, input_symbols={"a"},
        transitions={"q0": {"a": {"q1"}}, "q1": {"a": {"q1"}}},
        initial_state="q0", final_states={"q1"},
    )
    n2 = nfa.remove_epsilon_transitions()
    assert n2.accepts_input("a")
    assert not n2.accepts_input("")


def test_remove_epsilon_final_via_epsilon_chain():
    from automata_extensions.fa import ExtendedNFA
    nfa = ExtendedNFA(
        states={"a", "b"}, input_symbols={"x"},
        transitions={"a": {"": {"b"}}, "b": {}},
        initial_state="a", final_states={"b"},
    )
    n2 = nfa.remove_epsilon_transitions()
    assert n2.accepts_input("")  # a atteint b (final) par epsilon
