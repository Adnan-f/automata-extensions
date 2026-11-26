from automata.fa.nfa import NFA

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def _equivalent(fa, regex):
    rebuilt = ExtendedDFA.from_nfa(NFA.from_regex(regex, input_symbols=set(fa.input_symbols)))
    reference = fa if not fa._nondeterministic else fa.determinize()
    return reference.is_equivalent(rebuilt)


def test_arden_dfa(d):
    assert _equivalent(d, d.to_regex_arden())


def test_arden_nfa(n):
    assert _equivalent(n, n.to_regex_arden())


def test_arden_single_final_state_loop():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a", "b"},
        transitions={"q0": {"a": "q0", "b": "q0"}},
        initial_state="q0", final_states={"q0"},
    )
    assert _equivalent(dfa, dfa.to_regex_arden())


def test_arden_acyclic():
    dfa = ExtendedDFA(
        states={"q0", "q1", "q2"}, input_symbols={"a", "b"},
        transitions={"q0": {"a": "q1"}, "q1": {"b": "q2"}, "q2": {}},
        initial_state="q0", final_states={"q2"}, allow_partial=True,
    )
    assert dfa.to_regex_arden() == "ab"
    assert _equivalent(dfa, dfa.to_regex_arden())


def test_arden_matches_to_regex_language(d):
    r1 = d.to_regex()
    r2 = d.to_regex_arden()
    a = ExtendedDFA.from_nfa(NFA.from_regex(r1, input_symbols={"a", "b"}))
    b = ExtendedDFA.from_nfa(NFA.from_regex(r2, input_symbols={"a", "b"}))
    assert a.is_equivalent(b)


def test_arden_accepts_empty_word_when_initial_final(d):
    r = d.to_regex_arden()
    rebuilt = NFA.from_regex(r, input_symbols={"a", "b"})
    assert rebuilt.accepts_input("")


def test_arden_empty_language():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states=set(),
    )
    # langage vide : aucune regex d'automata-lib ne l'exprime
    assert dfa.to_regex_arden() is None
