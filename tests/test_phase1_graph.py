def test_successors_graph(d):
    assert d.successors_graph("1") == {"1", "2"}


def test_predecessors_graph(d):
    assert d.predecessors_graph("1") == {"1", "0"}


def test_successors_graph_nfa_multi_target(n):
    # 'p' --a--> {p,q} et 'p' --eps--> {r}
    assert n.successors_graph("p") == {"p", "q", "r"}


def test_predecessors_graph_isolated_target():
    from automata_extensions.fa import ExtendedDFA
    dfa = ExtendedDFA(
        states={"q0", "q1", "q2"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}, "q1": {"a": "q1"}, "q2": {"a": "q1"}},
        initial_state="q0", final_states={"q0"}, allow_partial=True,
    )
    assert dfa.predecessors_graph("q0") == {"q0"}
