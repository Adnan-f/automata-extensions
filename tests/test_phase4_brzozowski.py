def test_brzozowski_equivalent_to_minimize(d):
    b = d.brzozowski_minimize()
    m = d.minimize()
    assert b.is_equivalent(d)
    assert len(b.states) == len(m.states)


def test_brzozowski_on_already_minimal(d):
    assert d.is_minimal() is True
    b = d.brzozowski_minimize()
    assert len(b.states) == len(d.states)


def test_brzozowski_merges_equivalent_states():
    from automata_extensions.fa import ExtendedDFA
    dfa = ExtendedDFA(
        states={"q0", "q1", "q2"}, input_symbols={"a"},
        transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}, "q2": {"a": "q2"}},
        initial_state="q0", final_states={"q1"}, allow_partial=True,
    )
    b = dfa.brzozowski_minimize()
    assert b.is_equivalent(dfa)
    assert len(b.states) == 2  # q2 inaccessible + fusion éventuelle
