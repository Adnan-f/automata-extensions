"""Couverture du cahier des charges et de la documentation PDF.

Chaque entrée référence un item du cahier des charges (projet_automata_06.pdf, §4.1)
ou une section de la documentation (automata_documentation_v1.pdf, partie II).
Ce test échoue dès qu'une méthode annoncée manque : il évite de déclarer « terminé »
sans l'avoir vérifié.
"""

import inspect

import pytest

from automata_extensions import ExtendedDFA, ExtendedGNFA, ExtendedNFA
from automata_extensions.grammar import DerivationStep, Grammar

FA_COMMON = {                                   # présents sur DFA *et* NFA
    "predecessors_graph": "PDF §8 / item 18", "successors_graph": "PDF §8",
    "accessible_states": "item 3", "is_accessible": "item 4",
    "coaccessible_states": "item 5", "is_coaccessible": "item 6",
    "useful_states": "item 7", "is_trim": "item 9", "trim": "item 8",
    "reachable_states": "item 17", "input_parameters": "PDF §9", "copy": "PDF §10",
    "reverse": "item 36", "to_regex": "item 53", "to_regex_arden": "item 54",
    "to_regex_optimum": "PDF §17", "to_regex_arden_optimum": "PDF §17",
    "to_equations": "items 57-58",
    "bfs": "item 2", "dfs": "item 1", "has_cycle": "item 11", "has_cycle_from": "item 12",
    "is_empty": "item 13", "is_finite": "item 14",
    "strongly_connected_components": "item 10", "is_strongly_connected": "item 10",
    "induced_subautomaton": "item 19", "union": "item 42", "concatenation": "item 45",
    "kleene_star": "item 46", "is_deterministic": "item 33", "accepts": "item 15",
    "execution_trace": "item 16", "animate": "PDF §37", "dot": "item 40",
    "tikz": "item 41", "latex": "item 41", "graph": "item 41", "svg": "item 41",
    "png": "item 41", "pdf": "item 41", "left_quotient_word": "item 47",
    "right_quotient_word": "item 48", "to_grammar": "item 55", "derivation_tree": "item 56",
    "is_morphism_to": "item 61", "project": "item 61", "quotient_by": "item 61",
    "brzozowski_minimize": "item 50",
}
DFA_ONLY = {
    "is_complete": "item 20", "complete": "item 21", "complement": "item 22",
    "is_universal": "item 38", "product": "item 23", "intersection": "item 43",
    "difference": "item 44", "is_included_in": "item 24", "is_equivalent": "item 25",
    "is_isomorphic_to": "item 26", "is_prefix_closed": "item 27",
    "prefix_closed_sublanguage": "item 28", "distinguishable_states": "item 29",
    "pair_table": "PDF §14", "pair_table_str": "PDF §14", "print_pair_table": "PDF §14",
    "equivalence_classes": "item 30/59", "is_minimal": "item 31", "minimize": "item 32",
    "residual_automaton": "item 60", "syntactic_monoid": "item 62", "from_regex": "item 49",
}
NFA_ONLY = {
    "determinize": "item 35", "to_dfa": "PDF §21", "epsilon_closure": "item 34",
    "epsilon_closure_of_set": "item 34", "remove_epsilon_transitions": "item 37",
    "from_regex": "item 51", "from_grammar": "item 55", "from_grammar_string": "PDF §44",
}
GNFA_ONLY = {"eliminate_state": "item 39", "eliminate_states": "item 39"}


@pytest.mark.parametrize("name,ref", sorted(FA_COMMON.items()))
@pytest.mark.parametrize("cls", [ExtendedDFA, ExtendedNFA], ids=["DFA", "NFA"])
def test_common_methods_exist(cls, name, ref):
    assert hasattr(cls, name), f"{cls.__name__}.{name} manque ({ref})"


@pytest.mark.parametrize("name,ref", sorted(DFA_ONLY.items()))
def test_dfa_methods_exist(name, ref):
    assert hasattr(ExtendedDFA, name), f"ExtendedDFA.{name} manque ({ref})"


@pytest.mark.parametrize("name,ref", sorted(NFA_ONLY.items()))
def test_nfa_methods_exist(name, ref):
    assert hasattr(ExtendedNFA, name), f"ExtendedNFA.{name} manque ({ref})"


@pytest.mark.parametrize("name,ref", sorted(GNFA_ONLY.items()))
def test_gnfa_methods_exist(name, ref):
    assert hasattr(ExtendedGNFA, name), f"ExtendedGNFA.{name} manque ({ref})"


def test_grammar_objects():
    assert hasattr(DerivationStep, "word") and hasattr(DerivationStep, "sequence")
    assert hasattr(Grammar, "from_string") and hasattr(Grammar, "derive")


def test_complement_signature_matches_pdf():                     # PDF §13
    params = inspect.signature(ExtendedDFA.complement).parameters
    assert {"minify", "retain_names"} <= set(params)


def test_eliminate_lambda_is_usable_on_extended_nfa(n):          # PDF §4 / §41
    assert n.eliminate_lambda().accepts_input("a")
