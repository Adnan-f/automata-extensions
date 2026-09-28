import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


@pytest.fixture
def d():
    """Mots sur {a,b} dont le nombre de a est multiple de 3."""
    return ExtendedDFA(
        states={"0", "1", "2"}, input_symbols={"a", "b"},
        transitions={
            "0": {"a": "1", "b": "0"},
            "1": {"a": "2", "b": "1"},
            "2": {"a": "0", "b": "2"},
        },
        initial_state="0", final_states={"0"},
    )


@pytest.fixture
def n():
    """NFA avec une epsilon-transition."""
    return ExtendedNFA(
        states={"p", "q", "r"}, input_symbols={"a", "b"},
        transitions={
            "p": {"a": {"p", "q"}, "": {"r"}},
            "q": {"b": {"q"}},
            "r": {"a": {"r"}},
        },
        initial_state="p", final_states={"q", "r"},
    )
