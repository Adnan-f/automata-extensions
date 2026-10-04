def test_epsilon_closure_single_state(n):
    assert n.epsilon_closure("p") == {"p", "r"}


def test_epsilon_closure_no_epsilon_transitions(n):
    assert n.epsilon_closure("q") == {"q"}


def test_epsilon_closure_of_set(n):
    assert n.epsilon_closure_of_set({"p", "q"}) == {"p", "q", "r"}


def test_epsilon_closure_chain():
    from automata_extensions.fa import ExtendedNFA
    nfa = ExtendedNFA(
        states={"a", "b", "c"}, input_symbols={"x"},
        transitions={"a": {"": {"b"}}, "b": {"": {"c"}}, "c": {}},
        initial_state="a", final_states={"c"},
    )
    assert nfa.epsilon_closure("a") == {"a", "b", "c"}
