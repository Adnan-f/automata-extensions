from automata_extensions.fa import ExtendedDFA


def test_is_morphism_to_identity(d):
    identity = {s: s for s in d.states}
    assert d.is_morphism_to(d, identity) is True


def test_is_morphism_to_wrong_initial(d):
    bad_map = {s: s for s in d.states}
    bad_map[d.initial_state] = "1"
    assert d.is_morphism_to(d, bad_map) is False


def test_is_morphism_dfa_to_its_minimization(d):
    m = d.minimize(keep_original_names=True)
    identity = {s: s for s in d.states}
    assert d.is_morphism_to(m, identity) is True


def test_project_renames_symbol():
    dfa = ExtendedDFA(
        states={"q0", "q1"}, input_symbols={"a", "b"},
        transitions={"q0": {"a": "q1", "b": "q0"}, "q1": {"a": "q1", "b": "q1"}},
        initial_state="q0", final_states={"q1"}, allow_partial=True,
    )
    projected = dfa.project({"a": "x", "b": "y"})
    assert projected.input_symbols == {"x", "y"}
    assert projected.accepts_input("x")
    assert not projected.accepts_input("y")


def test_project_merging_symbols_yields_nondeterministic_nfa():
    from automata_extensions.fa import ExtendedNFA
    nfa = ExtendedNFA(
        states={"q0", "q1"}, input_symbols={"a", "b"},
        transitions={"q0": {"a": {"q1"}, "b": {"q0"}}, "q1": {"a": {"q1"}}},
        initial_state="q0", final_states={"q1"},
    )
    projected = nfa.project({"a": "x", "b": "x"})
    assert projected.input_symbols == {"x"}
    assert projected.accepts_input("xxx")


def test_quotient_by_merges_states():
    dfa = ExtendedDFA(
        states={"q0", "q1", "q2"}, input_symbols={"a"},
        transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}, "q2": {"a": "q2"}},
        initial_state="q0", final_states={"q1"}, allow_partial=True,
    )
    quotient = dfa.quotient_by({"q0": "q0", "q1": "q0", "q2": "q2"})
    assert quotient.states == {"q0", "q2"}
    assert quotient.initial_state == "q0"
