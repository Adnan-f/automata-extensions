from automata_extensions.fa import ExtendedDFA


def _dfa_a():
    return ExtendedDFA(
        states={"s0", "s1"}, input_symbols={"a", "b"},
        transitions={"s0": {"a": "s1", "b": "s0"}, "s1": {"a": "s1", "b": "s1"}},
        initial_state="s0", final_states={"s1"},
    )


def _dfa_b():
    return ExtendedDFA(
        states={"t0", "t1"}, input_symbols={"a", "b"},
        transitions={"t0": {"a": "t0", "b": "t1"}, "t1": {"a": "t1", "b": "t1"}},
        initial_state="t0", final_states={"t1"},
    )


def test_union_idempotent(d):
    assert d.union(d).is_equivalent(d)


def test_union_contains_a_or_b():
    u = _dfa_a().union(_dfa_b())
    assert u.accepts_input("a")
    assert u.accepts_input("b")
    assert not u.accepts_input("")


def test_difference_self_is_empty(d):
    assert d.difference(d).is_empty() is True


def test_difference_a_minus_b():
    diff = _dfa_a().difference(_dfa_b())
    assert diff.accepts_input("a")       # contient 'a', pas 'b'
    assert not diff.accepts_input("ab")  # contient les deux -> exclu
    assert not diff.accepts_input("")    # ne contient pas 'a'


def test_union_empty_languages():
    empty1 = ExtendedDFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}}, initial_state="q0", final_states=set(),
    )
    empty2 = ExtendedDFA(
        states={"r0"}, input_symbols={"a"},
        transitions={"r0": {"a": "r0"}}, initial_state="r0", final_states=set(),
    )
    assert empty1.union(empty2).is_empty() is True
