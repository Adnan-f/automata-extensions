from automata_extensions.fa import ExtendedNFA


def _a():
    return ExtendedNFA(
        states={"p0", "p1"}, input_symbols={"a", "b"},
        transitions={"p0": {"a": {"p1"}}, "p1": {}},
        initial_state="p0", final_states={"p1"},
    )


def _b():
    return ExtendedNFA(
        states={"q0", "q1"}, input_symbols={"a", "b"},
        transitions={"q0": {"b": {"q1"}}, "q1": {}},
        initial_state="q0", final_states={"q1"},
    )


def test_union_accepts_either():
    u = _a().union(_b())
    assert u.accepts_input("a")
    assert u.accepts_input("b")
    assert not u.accepts_input("ab")
    assert not u.accepts_input("")


def test_concatenation_accepts_ab():
    c = _a().concatenation(_b())
    assert c.accepts_input("ab")
    assert not c.accepts_input("a")
    assert not c.accepts_input("b")
    assert not c.accepts_input("ba")


def test_kleene_star_accepts_empty_and_repetitions():
    k = _a().kleene_star()
    assert k.accepts_input("")
    assert k.accepts_input("a")
    assert k.accepts_input("aa")
    assert k.accepts_input("aaa")
    assert not k.accepts_input("b")


def test_language_operations_on_dfa_too(d):
    # LanguageOperationsMixin est aussi disponible sur ExtendedDFA (héritage de ExtendedFA)
    star = d.kleene_star()
    assert star.accepts_input("")
