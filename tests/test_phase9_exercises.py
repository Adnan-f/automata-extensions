import re

import pytest

from automata_extensions.exercises import KINDS, Exercise, describe, generate
from automata_extensions.fa import ExtendedDFA, ExtendedNFA

SEEDS = range(25)


def _word_in_feedback(message: str) -> str:
    raw = re.search(r"« (.*?) »", message).group(1)
    return "" if raw == "ε" else raw


# ------------------------------------------------------------- génération
@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("seed", SEEDS)
def test_solution_is_accepted_and_generation_is_reproducible(kind, seed):
    ex = generate(kind, seed)
    assert isinstance(ex, Exercise) and ex.kind == kind and ex.seed == seed
    assert ex.statement.strip() and str(ex) == ex.statement
    assert ex.check(ex.solution) is True and ex.feedback(ex.solution) is None
    again = generate(kind, seed)
    assert again.statement == ex.statement
    if isinstance(ex.solution, str):
        assert again.solution == ex.solution
    else:
        assert again.solution.distinguishing_word(ex.solution) is None


def test_different_seeds_give_different_exercises():
    statements = {generate("minimize", seed).statement for seed in range(10)}
    assert len(statements) >= 8


@pytest.mark.parametrize("seed", SEEDS)
def test_generated_exercises_are_well_posed(seed):
    dfa_ex = generate("dfa_to_regex", seed)
    assert dfa_ex.given.is_minimal() and not dfa_ex.given.is_empty() and not dfa_ex.given.is_universal()

    regex_ex = generate("regex_to_dfa", seed)
    assert regex_ex.given in regex_ex.statement and 5 <= len(regex_ex.given) <= 16
    assert regex_ex.solution.is_complete() and regex_ex.solution.is_minimal()

    min_ex = generate("minimize", seed)
    assert len(min_ex.given.states) > len(min_ex.solution.states)              # redondant
    assert min_ex.given.accessible_states() != set(min_ex.given.states)        # état inaccessible
    assert min_ex.solution.is_complete() and min_ex.solution.is_minimal()
    assert min_ex.given.distinguishing_word(min_ex.solution) is None

    det_ex = generate("determinize", seed)
    assert not det_ex.given.is_deterministic() and "ε" in det_ex.statement
    assert det_ex.solution.is_deterministic()


def test_unknown_kind_and_custom_alphabet():
    with pytest.raises(ValueError):
        generate("nope")
    for kind in KINDS:
        for seed in range(4):
            ex = generate(kind, seed, alphabet=("a", "b", "c"))
            assert ex.alphabet == {"a", "b", "c"} and ex.check(ex.solution)


# ---------------------------------------------------------------- correction
@pytest.mark.parametrize("seed", range(15))
def test_wrong_regex_gets_a_valid_counterexample(seed):
    ex = generate("dfa_to_regex", seed)
    wrong = ex.given.complement().to_regex_optimum() or "()"
    message = ex.feedback(wrong)
    assert message and "diffèrent sur le mot" in message and ex.check(wrong) is False
    word = _word_in_feedback(message)
    candidate = ExtendedDFA.from_regex(wrong, input_symbols=ex.alphabet)
    assert ex.given.accepts_input(word) != candidate.accepts_input(word)
    assert ("la solution l'accepte" in message) == ex.given.accepts_input(word)


def test_any_equivalent_regex_is_accepted():
    ex = generate("dfa_to_regex", 2)
    for alternative in (ex.given.to_regex(), ex.given.to_regex_arden(), ex.given.to_regex_arden_optimum()):
        assert ex.check(alternative)


@pytest.mark.parametrize("seed", range(10))
def test_minimize_rejects_non_minimal_and_accepts_partial_minimal(seed):
    ex = generate("minimize", seed)
    assert ex.check(ex.given) is False
    assert "pas minimal" in ex.feedback(ex.given)
    assert ex.check(ex.solution.minimize()) is True                  # minimal sans état puits : accepté


@pytest.mark.parametrize("seed", range(10))
def test_determinize_and_regex_to_dfa_require_deterministic_answers(seed):
    det = generate("determinize", seed)
    assert "déterministe" in det.feedback(det.given)                 # le NFA donné est équivalent mais pas un DFA
    assert det.check(det.solution.minimize())                        # n'importe quel DFA équivalent convient

    rx = generate("regex_to_dfa", seed)
    thompson = ExtendedNFA.from_regex(rx.given, input_symbols=rx.alphabet)
    assert "déterministe" in rx.feedback(thompson)
    assert rx.check(thompson.determinize())


def test_invalid_answers_are_reported_not_raised():
    ex = generate("dfa_to_regex", 0)
    for bad in ("(a", "a|", "abc", 42, None, ex.given):              # syntaxe, symbole hors alphabet, types
        assert ex.feedback(bad).startswith("Réponse invalide")
        assert ex.check(bad) is False
    auto_ex = generate("minimize", 0)
    assert auto_ex.feedback("a*").startswith("Réponse invalide")
    assert auto_ex.feedback(42).startswith("Réponse invalide")


def test_wrong_automaton_counterexample_for_minimize():
    ex = generate("minimize", 5)
    wrong = ex.solution.complement()
    message = ex.feedback(wrong)
    word = _word_in_feedback(message)
    assert ex.solution.accepts_input(word) != wrong.accepts_input(word)


def test_describe_lists_everything(n):
    text = describe(n)
    assert "État initial : p" in text and "États finaux : q, r" in text
    assert "p --ε--> r" in text and "p --a--> p" in text and "p --a--> q" in text
