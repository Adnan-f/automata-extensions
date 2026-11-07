import random

import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedGNFA, ExtendedNFA


def _rand_dfa(rng, size):
    st = [str(i) for i in range(size)]
    return ExtendedDFA(states=set(st), input_symbols={"a", "b"},
                       transitions={s: {a: rng.choice(st) for a in "ab"} for s in st},
                       initial_state="0", final_states={s for s in st if rng.random() < 0.4})


def _rand_nfa(rng, size):
    st = [str(i) for i in range(size)]
    trans = {}
    for s in st:
        row = {}
        for a in ("a", "b", ""):
            targets = {t for t in st if rng.random() < 0.22}
            if targets:
                row[a] = targets
        trans[s] = row
    return ExtendedNFA(states=set(st), input_symbols={"a", "b"}, transitions=trans,
                       initial_state="0", final_states={s for s in st if rng.random() < 0.4})


def _edges(fa):
    return {(p, q) for p in fa.states for q in fa.successors_graph(p)}


# ------------------------------------------------------------------- SCC
def test_scc_pdf_value(d):
    assert d.strongly_connected_components() == [frozenset({"0", "1", "2"})]
    assert d.is_strongly_connected() is True


def test_scc_chain_gives_one_component_per_state_in_reverse_topological_order():
    chain = ExtendedDFA(states={"a", "b", "c"}, input_symbols={"x"},
                        transitions={"a": {"x": "b"}, "b": {"x": "c"}, "c": {"x": "c"}},
                        initial_state="a", final_states={"c"})
    comps = chain.strongly_connected_components()
    assert comps == [frozenset({"c"}), frozenset({"b"}), frozenset({"a"})]   # puits d'abord
    assert chain.is_strongly_connected() is False


def test_scc_two_cycles_and_unreachable_state():
    dfa = ExtendedDFA(states={"1", "2", "3", "4", "z"}, input_symbols={"x", "y"},
                      transitions={"1": {"x": "2", "y": "1"}, "2": {"x": "1", "y": "3"},
                                   "3": {"x": "4", "y": "3"}, "4": {"x": "3", "y": "4"},
                                   "z": {"x": "z", "y": "1"}},
                      initial_state="1", final_states={"4"})
    comps = dfa.strongly_connected_components()
    assert set(comps) == {frozenset({"1", "2"}), frozenset({"3", "4"}), frozenset({"z"})}
    assert comps.index(frozenset({"3", "4"})) < comps.index(frozenset({"1", "2"}))


def test_scc_single_state_and_gnfa(d):
    one = ExtendedDFA(states={"q"}, input_symbols={"a"}, transitions={"q": {"a": "q"}},
                      initial_state="q", final_states={"q"})
    assert one.strongly_connected_components() == [frozenset({"q"})] and one.is_strongly_connected()
    g = ExtendedGNFA.from_dfa(d)
    comps = g.strongly_connected_components()
    assert frozenset({"0", "1", "2"}) in comps                       # les états du DFA d'origine
    assert len(comps) == 3                                           # + start et end isolés
    assert not g.is_strongly_connected()


def test_scc_deep_chain_has_no_recursion_limit():
    n = 3000
    names = [f"s{i}" for i in range(n)]
    dfa = ExtendedDFA(states=set(names), input_symbols={"x"},
                      transitions={names[i]: {"x": names[min(i + 1, n - 1)]} for i in range(n)},
                      initial_state="s0", final_states={names[-1]})
    assert len(dfa.strongly_connected_components()) == n


@pytest.mark.parametrize("seed", range(60))
def test_random_scc_matches_mutual_reachability_definition(seed):
    rng = random.Random(seed)
    fa = (_rand_nfa if seed % 2 else _rand_dfa)(rng, rng.randint(1, 7))
    comps = fa.strongly_connected_components()
    assert set().union(*comps) == set(fa.states) and sum(map(len, comps)) == len(fa.states)
    reach = {s: fa.reachable_states(s) for s in fa.states}
    for comp in comps:
        for u in comp:
            for v in comp:
                assert v in reach[u]
    for u in fa.states:                                              # maximalité
        for v in fa.states:
            same = any(u in c and v in c for c in comps)
            assert same == (v in reach[u] and u in reach[v])
    where = {s: i for i, c in enumerate(comps) for s in c}           # ordre topologique inverse
    for p, q in _edges(fa):
        assert where[q] <= where[p]


# ------------------------------------------------------------ pair table
def test_pair_table_str_pdf_value(d):
    assert d.pair_table_str(show_round=True) == " 0 1\n1 0\n2 0 1"
    assert d.pair_table_str() == " 0 1\n1 X\n2 X X"


def test_pair_table_and_print(d, capsys):
    assert d.pair_table() == {frozenset("01"): 0, frozenset("02"): 0, frozenset("12"): 1}
    d.print_pair_table()
    assert capsys.readouterr().out == " 0 1\n1 0\n2 0 1\n"
    d.print_pair_table(show_round=False)
    assert capsys.readouterr().out == " 0 1\n1 X\n2 X X\n"


def test_pair_table_marks_equivalent_states_with_none_and_dash():
    dfa = ExtendedDFA(states={"s", "x", "y"}, input_symbols={"a"},
                      transitions={"s": {"a": "x"}, "x": {"a": "y"}, "y": {"a": "x"}},
                      initial_state="s", final_states={"x", "y"})
    assert dfa.pair_table()[frozenset({"x", "y"})] is None
    assert dfa.pair_table_str() == " s x\nx X\ny X -"


def test_pair_table_single_state_is_empty_string():
    one = ExtendedDFA(states={"q"}, input_symbols={"a"}, transitions={"q": {"a": "q"}},
                      initial_state="q", final_states={"q"})
    assert one.pair_table() == {} and one.pair_table_str() == ""


def test_pair_table_partial_dfa_is_completed():
    partial = ExtendedDFA(states={"p", "q"}, input_symbols={"a"}, transitions={"p": {"a": "q"}, "q": {}},
                          initial_state="p", final_states={"q"}, allow_partial=True)
    table = partial.pair_table()
    assert frozenset({"p", "q"}) in table and any("__trap__" in pair for pair in table)


@pytest.mark.parametrize("seed", range(40))
def test_random_pair_round_is_length_of_shortest_distinguishing_word(seed):
    dfa = _rand_dfa(random.Random(seed), random.Random(seed).randint(2, 6))
    complete = dfa.complete()
    for pair, mark in dfa.pair_table().items():
        p, q = tuple(pair)
        from_p = ExtendedDFA(**{**complete.input_parameters, "initial_state": p})
        from_q = ExtendedDFA(**{**complete.input_parameters, "initial_state": q})
        witness = from_p.distinguishing_word(from_q)
        assert (mark is None) == (witness is None)
        if mark is not None:
            assert mark == len(witness)
    assert dfa.distinguishable_states() == {pr for pr, m in dfa.pair_table().items() if m is not None}


# ------------------------------------------------- complement / brzozowski
def test_complement_minify_and_retain_names_pdf(d):
    plain = d.complement()
    minified = d.complement(minify=True, retain_names=True)
    assert plain.accepts_input("a") and minified.accepts_input("a")
    assert sorted(minified.states) == ["0", "1", "2"]                  # valeur du PDF
    assert all(isinstance(s, frozenset) for s in d.complement(minify=True).states)


def test_complement_minify_merges_states():
    dfa = ExtendedDFA(states={"s", "x", "y"}, input_symbols={"a"},
                      transitions={"s": {"a": "x"}, "x": {"a": "y"}, "y": {"a": "x"}},
                      initial_state="s", final_states={"x", "y"})
    assert len(dfa.complement().states) == 3
    assert len(dfa.complement(minify=True).states) < 3
    assert dfa.complement(minify=True).is_equivalent(dfa.complement())


def test_brzozowski_on_nfa(n):
    b = n.brzozowski_minimize()
    assert b.is_deterministic() and b.is_equivalent(n.determinize())
    assert len(b.states) == len(n.determinize().residuals())


def test_eliminate_lambda_delegates_to_remove_epsilon_transitions(n):
    a, b = n.eliminate_lambda(), n.remove_epsilon_transitions()
    assert type(a) is ExtendedNFA and a == b
    assert a.transitions == b.transitions and a.final_states == b.final_states
    assert all("" not in row for row in a.transitions.values())
