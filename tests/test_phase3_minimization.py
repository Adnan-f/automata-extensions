from automata_extensions.fa import ExtendedDFA


def test_distinguishable_states(d):
    marked = d.distinguishable_states()
    assert frozenset(("0", "1")) in marked
    assert frozenset(("1", "2")) in marked
    assert frozenset(("0", "2")) in marked


def test_equivalence_classes_all_singletons(d):
    classes = d.equivalence_classes()
    assert sorted(map(sorted, classes)) == [["0"], ["1"], ["2"]]


def test_is_minimal_true(d):
    assert d.is_minimal() is True


def test_is_minimal_false_with_equivalent_states():
    dfa = ExtendedDFA(
        states={"q0", "q1", "q2"}, input_symbols={"a"},
        transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}, "q2": {"a": "q2"}},
        initial_state="q0", final_states={"q1", "q2"}, allow_partial=True,
    )
    assert dfa.is_minimal() is False


def test_is_minimal_false_inaccessible_state():
    dfa = ExtendedDFA(
        states={"q0", "q1"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}, "q1": {"a": "q1"}},
        initial_state="q0", final_states={"q0"}, allow_partial=True,
    )
    assert dfa.is_minimal() is False


def test_minimize_preserves_language(d):
    assert d.minimize().is_equivalent(d)


def test_minimize_keep_original_names(d):
    m = d.minimize(keep_original_names=True)
    assert sorted(m.states) == ["0", "1", "2"]


def test_minimize_merges_equivalent_states():
    dfa = ExtendedDFA(
        states={"q0", "q1", "q2"}, input_symbols={"a"},
        transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}, "q2": {"a": "q2"}},
        initial_state="q0", final_states={"q1"}, allow_partial=True,
    )
    minimized = dfa.minimize()
    assert len(minimized.states) == 2
    assert minimized.is_equivalent(dfa)


def test_minimize_single_state():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states={"q0"},
    )
    m = dfa.minimize()
    assert len(m.states) == 1
    assert m.is_equivalent(dfa)


def test_pair_table_str_runs(d):
    s = d.pair_table_str()
    assert isinstance(s, str) and len(s) > 0
