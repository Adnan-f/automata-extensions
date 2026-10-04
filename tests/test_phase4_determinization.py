def test_determinize_preserves_acceptance(n):
    dfa = n.determinize()
    for word in ("a", "aa", "b", "aab", "aba", ""):
        assert dfa.accepts_input(word) == n.accepts_input(word)


def test_to_dfa_alias(n):
    assert n.to_dfa().accepts_input("a") == n.determinize().accepts_input("a")


def test_determinize_already_deterministic_shape():
    from automata_extensions.fa import ExtendedNFA
    nfa = ExtendedNFA(
        states={"q0", "q1"}, input_symbols={"a"},
        transitions={"q0": {"a": {"q1"}}, "q1": {"a": {"q1"}}},
        initial_state="q0", final_states={"q1"},
    )
    dfa = nfa.determinize()
    assert dfa.accepts_input("a")
    assert not dfa.accepts_input("")


def test_determinize_empty_language():
    from automata_extensions.fa import ExtendedNFA
    nfa = ExtendedNFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": {"q0"}}},
        initial_state="q0", final_states=set(),
    )
    dfa = nfa.determinize()
    assert dfa.is_empty()
