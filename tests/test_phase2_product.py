from automata_extensions.fa import ExtendedDFA


def _dfa_a():
    # mots contenant au moins un 'a'
    return ExtendedDFA(
        states={"s0", "s1"}, input_symbols={"a", "b"},
        transitions={"s0": {"a": "s1", "b": "s0"}, "s1": {"a": "s1", "b": "s1"}},
        initial_state="s0", final_states={"s1"},
    )


def _dfa_b():
    # mots contenant au moins un 'b'
    return ExtendedDFA(
        states={"t0", "t1"}, input_symbols={"a", "b"},
        transitions={"t0": {"a": "t0", "b": "t1"}, "t1": {"a": "t1", "b": "t1"}},
        initial_state="t0", final_states={"t1"},
    )


def test_intersection_basic(d):
    assert d.intersection(d).is_equivalent(d)


def test_intersection_disjoint_alphabets_raise():
    dfa2 = ExtendedDFA(
        states={"z"}, input_symbols={"x"},
        transitions={"z": {"x": "z"}}, initial_state="z", final_states={"z"},
    )
    import pytest
    with pytest.raises(ValueError):
        _dfa_a().intersection(dfa2)


def test_intersection_contains_a_and_b():
    inter = _dfa_a().intersection(_dfa_b())
    assert inter.accepts_input("ab")
    assert inter.accepts_input("ba")
    assert not inter.accepts_input("aa")
    assert not inter.accepts_input("")


def test_product_lazy_only_reachable_pairs():
    # deux automates à 3 états chacun mais seuls quelques couples sont accessibles
    a = ExtendedDFA(
        states={"a0", "a1", "a2"}, input_symbols={"x"},
        transitions={"a0": {"x": "a1"}, "a1": {"x": "a1"}, "a2": {"x": "a2"}},
        initial_state="a0", final_states={"a1"},
    )
    b = ExtendedDFA(
        states={"b0", "b1"}, input_symbols={"x"},
        transitions={"b0": {"x": "b1"}, "b1": {"x": "b1"}},
        initial_state="b0", final_states={"b1"},
    )
    prod = a.product(b, is_final=lambda s1, s2: s1 == "a1" and s2 == "b1")
    # a2 n'est jamais atteint depuis (a0,b0) -> aucun couple (a2, *) ne doit exister
    assert not any(pair[0] == "a2" for pair in prod.states)
