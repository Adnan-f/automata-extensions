from automata.fa.nfa import NFA

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


def _roundtrip_equivalent(fa, regex):
    """Vérifie que ``regex`` dénote bien le langage de ``fa`` (via automata-lib)."""
    rebuilt = ExtendedDFA.from_nfa(NFA.from_regex(regex, input_symbols=set(fa.input_symbols)))
    reference = fa if not fa._nondeterministic else fa.determinize()
    return reference.is_equivalent(rebuilt)


def test_to_regex_dfa(d):
    assert _roundtrip_equivalent(d, d.to_regex())


def test_to_regex_nfa(n):
    assert _roundtrip_equivalent(n, n.to_regex())


def test_to_regex_single_state_universal():
    dfa = ExtendedDFA(
        states={"q0"}, input_symbols={"a"},
        transitions={"q0": {"a": "q0"}},
        initial_state="q0", final_states={"q0"},
    )
    assert _roundtrip_equivalent(dfa, dfa.to_regex())


def test_to_regex_with_inaccessible_state():
    dfa = ExtendedDFA(
        states={"q0", "q1", "q2"}, input_symbols={"a"},
        transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}, "q2": {"a": "q2"}},
        initial_state="q0", final_states={"q1"},
    )
    assert _roundtrip_equivalent(dfa, dfa.to_regex())
