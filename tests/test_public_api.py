"""API publique, conventions du cahier des charges (immuabilité, composition), métadonnées."""

import importlib
import importlib.metadata
import re

import pytest
from automata.fa.dfa import DFA

import automata_extensions
from automata_extensions import ExtendedDFA, ExtendedFA, ExtendedGNFA, ExtendedNFA

SUBMODULES = ["fa", "regex", "grammar", "algebra", "equations", "exercises",
              "utils.patches", "utils.render", "utils.ordering"]


def test_all_exports_exist_and_are_the_right_things():
    for name in automata_extensions.__all__:
        assert hasattr(automata_extensions, name), name
    assert issubclass(ExtendedDFA, ExtendedFA) and issubclass(ExtendedDFA, DFA)
    assert issubclass(ExtendedGNFA, ExtendedFA) and issubclass(ExtendedNFA, ExtendedFA)


def test_version_matches_installed_metadata_and_is_semver():
    version = automata_extensions.__version__
    assert re.fullmatch(r"\d+\.\d+\.\d+", version)
    assert importlib.metadata.version("automata-extensions") == version


@pytest.mark.parametrize("name", SUBMODULES)
def test_submodules_import(name):
    assert importlib.import_module(f"automata_extensions.{name}")


def test_cached_method_patch_is_active_for_pure_automata_lib_objects():
    pure = DFA(states={"q"}, input_symbols={"a"}, transitions={"q": {"a": "q"}},
               initial_state="q", final_states={"q"})
    assert all((pure - pure).isempty() for _ in range(30))        # RuntimeError sans le correctif


TRANSFORMATIONS = ["trim", "complete", "complement", "minimize", "brzozowski_minimize", "reverse",
                   "kleene_star", "residual_automaton", "prefix_closed_sublanguage", "copy"]


@pytest.mark.parametrize("name", TRANSFORMATIONS)
def test_transformations_never_modify_self_and_return_new_objects(d, name):
    before = d.input_parameters
    result = getattr(d, name)()
    assert d.input_parameters == before
    assert result is not d


def test_nfa_transformations_are_non_destructive(n):
    before = n.input_parameters
    for name in ["trim", "reverse", "determinize", "remove_epsilon_transitions", "kleene_star",
                 "left_quotient_word", "to_equations"]:
        args = ("a",) if name == "left_quotient_word" else ()
        assert getattr(n, name)(*args) is not n
    assert n.input_parameters == before


def test_composition_from_the_specification(d):
    """Exemples de composition du cahier des charges (§5)."""
    assert d.trim().minimize().to_regex()                                   # dfa.trim().minimize().to_regex()
    chained = d.reverse().determinize().minimize()                          # dfa.reverse().determinize().minimize()
    assert chained.is_equivalent(d)                                         # le langage est son propre miroir
    again = d.complement().complement()
    assert again.is_equivalent(d) and again is not d


def test_every_algorithm_family_is_reachable_from_the_top_level_package():
    from automata_extensions import Grammar, parse_regex
    assert Grammar.from_string("S -> a").generates("a")
    assert str(parse_regex("a|b").simplify()) == "a|b"
