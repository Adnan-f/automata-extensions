from automata_extensions.fa import ExtendedDFA


def test_is_included_in_self(d):
    assert d.is_included_in(d) is True


def test_is_equivalent_self(d):
    assert d.is_equivalent(d) is True


def test_strict_inclusion():
    # L1 : mots contenant "a" ; L2 : Sigma* (univers)
    l1 = ExtendedDFA(
        states={"s0", "s1"}, input_symbols={"a", "b"},
        transitions={"s0": {"a": "s1", "b": "s0"}, "s1": {"a": "s1", "b": "s1"}},
        initial_state="s0", final_states={"s1"},
    )
    universe = ExtendedDFA(
        states={"u0"}, input_symbols={"a", "b"},
        transitions={"u0": {"a": "u0", "b": "u0"}},
        initial_state="u0", final_states={"u0"},
    )
    assert l1.is_included_in(universe) is True
    assert universe.is_included_in(l1) is False
    assert l1.is_equivalent(universe) is False


def test_equivalent_via_minify(d):
    assert d.is_equivalent(d.minify()) is True


def test_empty_language_included_in_anything(d):
    empty = ExtendedDFA(
        states={"q0"}, input_symbols={"a", "b"},
        transitions={"q0": {"a": "q0", "b": "q0"}},
        initial_state="q0", final_states=set(),
    )
    assert empty.is_included_in(d) is True
