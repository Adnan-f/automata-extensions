import itertools
import random

import pytest

from automata_extensions import parse_regex
from automata_extensions.equations import EquationSystem, arden
from automata_extensions.fa import ExtendedDFA, ExtendedGNFA, ExtendedNFA
from automata_extensions.regex import EMPTY, EPSILON, Symbol


def _rand_dfa(rng, size):
    st = [str(i) for i in range(size)]
    return ExtendedDFA(states=set(st), input_symbols={"a", "b"},
                       transitions={s: {a: rng.choice(st) for a in "ab"} for s in st},
                       initial_state="0", final_states={s for s in st if rng.random() < 0.4})


def _language_of(regex, alphabet=("a", "b")):
    return ExtendedDFA.from_regex(regex, input_symbols=alphabet)


def _label(g):
    return g.transitions[g.initial_state][g.final_state]


# ------------------------------------------------------- GNFA : item 39
def test_eliminate_state_one_step(d):
    g = ExtendedGNFA.from_dfa(d)
    h = g.eliminate_state("1")
    assert isinstance(h, ExtendedGNFA) and "1" not in h.states and len(h.states) == len(g.states) - 1
    assert "1" in g.states                                              # l'original n'est pas modifié
    assert h.initial_state == g.initial_state and h.final_state == g.final_state


def test_eliminate_state_errors(d):
    g = ExtendedGNFA.from_dfa(d)
    for bad in (g.initial_state, g.final_state, "nope"):
        with pytest.raises(ValueError):
            g.eliminate_state(bad)


def test_eliminate_states_gives_two_state_gnfa_with_correct_regex(d):
    two = ExtendedGNFA.from_dfa(d).eliminate_states()
    assert len(two.states) == 2
    assert _language_of(_label(two)).is_equivalent(d)


def test_eliminate_states_order_changes_text_not_language(d):
    g = ExtendedGNFA.from_dfa(d)
    results = set()
    for order in itertools.permutations(["0", "1", "2"]):
        label = _label(g.eliminate_states(order))
        assert _language_of(label).is_equivalent(d)
        results.add(label)
    assert len(results) > 1                                             # écritures différentes
    with pytest.raises(ValueError):
        g.eliminate_states(["0", "1"])


def test_eliminate_states_empty_language_gives_none():
    dfa = ExtendedDFA(states={"q"}, input_symbols={"a"}, transitions={"q": {"a": "q"}},
                      initial_state="q", final_states=set())
    assert _label(ExtendedGNFA.from_dfa(dfa).eliminate_states()) is None


@pytest.mark.parametrize("seed", range(40))
def test_random_gnfa_elimination_matches_language_and_library(seed):
    from automata.fa.gnfa import GNFA
    rng = random.Random(seed)
    dfa = _rand_dfa(rng, rng.randint(1, 5))
    if dfa.is_empty():
        return
    g = ExtendedGNFA.from_dfa(dfa)
    middle = [s for s in g.states if s not in (g.initial_state, g.final_state)]
    rng.shuffle(middle)
    mine = _label(g.eliminate_states(middle))
    assert _language_of(mine).is_equivalent(dfa)
    assert _language_of(GNFA.from_dfa(dfa).to_regex()).is_equivalent(_language_of(mine))


# -------------------------------------------------- Arden : items 57-58
def test_arden_lemma():
    a, b = Symbol("a"), Symbol("b")
    assert str(arden(a, b)) == "a*b"
    assert arden(EMPTY, b) == b                                         # X = ∅X | b  =>  X = b
    assert arden(a, EMPTY) == EMPTY
    assert arden(EPSILON, b) == b                                       # plus petite solution
    assert str(arden(parse_regex("a|b").simplify(), parse_regex("c").simplify())) == "(a|b)*c"


def test_arden_is_a_solution_of_the_equation():
    for a_text, b_text in [("a", "b"), ("ab", "c|d"), ("a|b", "()"), ("a*", "b")]:
        a, b = parse_regex(a_text).simplify(), parse_regex(b_text).simplify()
        x = arden(a, b)
        from automata_extensions.regex import concat, union
        lhs, rhs = _language_of(str(x), "abcd"), _language_of(str(union(concat(a, x), b)), "abcd")
        assert lhs.is_equivalent(rhs)


def test_equation_system_of_automaton(d):
    system = d.to_equations()
    assert isinstance(system, EquationSystem)
    # termes dans l'ordre des variables (X0, X1, X2), puis la constante
    assert str(system) == "X0 = bX0 | aX1 | ε\nX1 = bX1 | aX2\nX2 = aX0 | bX2"
    assert d.to_equations().variables == ("0", "1", "2")


def test_equation_system_solution_is_the_language_of_each_state(d):
    solution = d.to_equations().solve()
    assert set(solution) == {"0", "1", "2"}
    assert _language_of(str(solution["0"])).is_equivalent(d)
    for state, expression in solution.items():                          # X_q = langage depuis q
        from_state = ExtendedDFA(**{**d.input_parameters, "initial_state": state})
        assert _language_of(str(expression)).is_equivalent(from_state)


def test_equation_system_order_and_errors(d):
    system = d.to_equations()
    for order in itertools.permutations(["0", "1", "2"]):
        assert _language_of(str(system.solve(order)["0"])).is_equivalent(d)
    with pytest.raises(ValueError):
        system.solve(["0", "1"])
    with pytest.raises(ValueError):
        system.solve(["0", "1", "x"])


def test_equation_system_nfa_with_epsilon_and_gnfa(n, d):
    solution = n.to_equations().solve()
    assert _language_of(str(solution["p"])).is_equivalent(n.determinize())
    with pytest.raises(TypeError):
        ExtendedGNFA.from_dfa(d).to_equations()


def test_equation_system_unsolvable_state_gives_empty_language():
    dfa = ExtendedDFA(states={"q0", "q1"}, input_symbols={"a"},
                      transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}},
                      initial_state="q0", final_states=set())
    assert dfa.to_equations().solve()["q0"] == EMPTY


@pytest.mark.parametrize("seed", range(40))
def test_random_equation_systems(seed):
    rng = random.Random(seed)
    dfa = _rand_dfa(rng, rng.randint(1, 5))
    states = sorted(dfa.states)
    rng.shuffle(states)
    solution = dfa.to_equations().solve(states)
    complete = dfa.complete()
    for state in dfa.states:
        from_state = ExtendedDFA(**{**complete.input_parameters, "initial_state": state})
        expression = solution[state]
        if from_state.is_empty():
            assert expression == EMPTY
        else:
            assert _language_of(str(expression)).is_equivalent(from_state)
