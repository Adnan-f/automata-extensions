from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def test_optimum_not_longer_than_plain(d):
    assert len(d.to_regex_optimum()) <= len(d.to_regex())
    assert len(d.to_regex_arden_optimum()) <= len(d.to_regex_arden())


def test_optimum_known_value(d):
    assert d.to_regex_optimum() == "(ab*ab*a|b)*"


def test_optimum_nfa_with_epsilon(n):
    r = n.to_regex_optimum()
    assert ExtendedDFA.from_regex(r, input_symbols={"a", "b"}).is_equivalent(n.determinize())


def test_optimum_empty_language_and_unreachable_final():
    dfa = ExtendedDFA(
        states={"q0", "q1"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}, "q1": {"a": "q1"}},
        initial_state="q0", final_states={"q1"},
    )
    assert dfa.to_regex_optimum() is None
    assert dfa.to_regex_arden_optimum() is None


def test_optimum_deterministic_and_large_state_count_sampling():
    # 8 états > max_exhaustive : échantillonnage reproductible (graine fixe)
    states = [str(i) for i in range(8)]
    dfa = ExtendedDFA(
        states=set(states), input_symbols={"a", "b"},
        transitions={s: {"a": states[(int(s) + 1) % 8], "b": s} for s in states},
        initial_state="0", final_states={"0"},
    )
    r1 = dfa.to_regex_optimum()
    r2 = dfa.to_regex_optimum()
    assert r1 == r2
    assert ExtendedDFA.from_regex(r1, input_symbols={"a", "b"}).is_equivalent(dfa)
