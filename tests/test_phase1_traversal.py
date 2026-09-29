def test_bfs_dfa(d):
    assert d.bfs() == ["0", "1", "2"]


def test_dfs_iterative_and_recursive_agree(d):
    assert set(d.dfs()) == {"0", "1", "2"}
    assert set(d.dfs(recursive=True)) == {"0", "1", "2"}
    assert d.dfs()[0] == "0"
    assert d.dfs(recursive=True)[0] == "0"


def test_reachable_states_from_arbitrary_state(d):
    assert d.reachable_states("1") == {"0", "1", "2"}


def test_bfs_single_state():
    from automata_extensions.fa import ExtendedDFA
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states={"q0"},
    )
    assert dfa.bfs() == ["q0"]
    assert dfa.dfs(recursive=True) == ["q0"]


def test_bfs_nfa_with_epsilon(n):
    assert set(n.bfs()) == {"p", "q", "r"}
