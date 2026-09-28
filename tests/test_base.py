import pytest

from automata_extensions.fa import (ExtendedDFA, ExtendedFA, ExtendedGNFA,
                                    ExtendedNFA)


def test_hierarchy():
    assert issubclass(ExtendedDFA, ExtendedFA)
    assert issubclass(ExtendedNFA, ExtendedFA)
    assert issubclass(ExtendedGNFA, ExtendedFA)


def test_input_parameters_dfa(d):
    assert sorted(d.input_parameters) == [
        "allow_partial", "final_states", "initial_state",
        "input_symbols", "states", "transitions"]


def test_input_parameters_nfa(n):
    assert sorted(n.input_parameters) == [
        "final_states", "initial_state", "input_symbols", "states", "transitions"]


def test_copy_dfa(d):
    d2 = d.copy()
    assert d2 == d and d2 is not d and type(d2) is ExtendedDFA


def test_copy_nfa(n):
    n2 = n.copy()
    assert n2 == n and n2 is not n and type(n2) is ExtendedNFA


def test_accepts_dfa(d):
    assert d.accepts_input("aaa") and not d.accepts_input("a")


def test_accepts_nfa(n):
    assert n.accepts_input("a")


def test_from_dfa_gnfa(d):
    g = ExtendedGNFA.from_dfa(d)
    assert type(g) is ExtendedGNFA
    assert g.copy().final_state == g.final_state


def test_dfa_still_immutable(d):
    with pytest.raises(AttributeError):
        d.states = set()
