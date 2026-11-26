import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedGNFA, ExtendedNFA


def test_is_deterministic(d, n):
    assert d.is_deterministic() is True
    assert n.is_deterministic() is False                      # ε-transition


def test_is_deterministic_nfa_variants():
    single = ExtendedNFA(states={"p", "q"}, input_symbols={"a"},
                         transitions={"p": {"a": {"q"}}, "q": {}},
                         initial_state="p", final_states={"q"})
    multi = ExtendedNFA(states={"p", "q", "r"}, input_symbols={"a"},
                        transitions={"p": {"a": {"q", "r"}}, "q": {}, "r": {}},
                        initial_state="p", final_states={"q"})
    assert single.is_deterministic() is True
    assert multi.is_deterministic() is False


def test_is_deterministic_partial_dfa_and_gnfa(d):
    partial = ExtendedDFA(states={"q0"}, input_symbols={"a", "b"},
                          transitions={"q0": {"a": "q0"}}, initial_state="q0",
                          final_states={"q0"}, allow_partial=True)
    assert partial.is_deterministic() is True
    assert ExtendedGNFA.from_dfa(d).is_deterministic() is False


def test_accepts_alias(d, n):
    assert d.accepts("aaa") is True and d.accepts("a") is False
    assert n.accepts("a") is True


def test_execution_trace_dfa_pdf_value(d):
    assert d.execution_trace("aab") == [("0", "a", "1"), ("1", "a", "2"), ("2", "b", "2")]
    assert d.execution_trace("") == []


def test_execution_trace_dfa_blocked_and_unknown_symbol():
    partial = ExtendedDFA(states={"q0", "q1"}, input_symbols={"a", "b"},
                          transitions={"q0": {"a": "q1"}, "q1": {}}, initial_state="q0",
                          final_states={"q1"}, allow_partial=True)
    assert partial.execution_trace("aab") == [("q0", "a", "q1")]   # bloqué sur le 2e 'a'
    assert partial.execution_trace("zz") == []


def test_execution_trace_nfa(n):
    trace = n.execution_trace("ab")
    assert trace[0] == (frozenset({"p", "r"}), "a", frozenset({"p", "q", "r"}))
    assert trace[1] == (frozenset({"p", "q", "r"}), "b", frozenset({"q"}))


def test_execution_trace_nfa_stops_on_empty_set(n):
    trace = n.execution_trace("bbb")
    assert len(trace) == 1 and trace[0][2] == frozenset()


def test_run_dfa(d):
    assert d.run("aaa") == "0 → 1 → 2 → 0 → accept"
    assert d.run("aab") == "0 → 1 → 2 → 2 → reject"
    assert d.run("") == "0 → accept"
    assert d.run("ab", sep=" -> ") == "0 -> 1 -> 1 -> reject"


def test_run_dfa_blocked_and_unknown_symbol():
    partial = ExtendedDFA(states={"q0", "q1"}, input_symbols={"a"},
                          transitions={"q0": {"a": "q1"}, "q1": {}}, initial_state="q0",
                          final_states={"q1"}, allow_partial=True)
    assert partial.run("aa") == "q0 → q1 → reject"
    assert partial.run("z") == "q0 → reject"


def test_run_nfa(n):
    assert n.run("a") == "{p, r} → {p, q, r} → accept"
    assert n.run("") == "{p, r} → accept"


def test_run_gnfa_not_supported(d):
    with pytest.raises(TypeError):
        ExtendedGNFA.from_dfa(d).run("a")
