"""project() : homomorphisme de mots (renommage, fusion, effacement) — vérifié par un oracle indépendant."""

import itertools
import random

import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedGNFA, ExtendedNFA


def _image_has_preimage(fa, mapping, word):
    """
    Oracle indépendant de ``project`` : existe-t-il un mot w de L(fa) avec h(w) = word ?

    Parcours de l'espace (état, position dans ``word``) : un symbole effacé ou une
    ε-transition ne fait pas avancer la position, un symbole envoyé sur ``word[i]`` l'avance.
    """
    seen = {(fa.initial_state, 0)}
    stack = [(fa.initial_state, 0)]
    while stack:
        state, i = stack.pop()
        if i == len(word) and state in fa.final_states:
            return True
        for symbol, target in fa.transitions.get(state, {}).items():
            image = "" if symbol == "" else mapping.get(symbol, symbol)
            if image is None or image == "":
                step = 0
            elif i < len(word) and word[i] == image:
                step = 1
            else:
                continue
            for nxt in (target if fa._nondeterministic else {target}):
                if (nxt, i + step) not in seen:
                    seen.add((nxt, i + step))
                    stack.append((nxt, i + step))
    return False


def _words(alphabet, max_len):
    for length in range(max_len + 1):
        for letters in itertools.product(sorted(alphabet), repeat=length):
            yield "".join(letters)


# ------------------------------------------------------------- valeurs du PDF
def test_pdf_example_erasing_a_symbol(d):
    projected = d.project({"a": "x", "b": None})
    assert projected.accepts_input("xxx") is True                      # valeur du PDF (§20)
    assert [projected.accepts_input(w) for w in ("", "x", "xx", "xxxxxx")] == [True, False, False, True]


def test_erasing_a_symbol_gives_an_nfa_with_epsilon_transitions(d):
    projected = d.project({"a": "x", "b": None})
    assert type(projected) is ExtendedNFA and projected.input_symbols == {"x"}
    assert any("" in row for row in projected.transitions.values())


# --------------------------------------------------------- classe du résultat
def test_injective_renaming_keeps_a_dfa(d):
    renamed = d.project({"a": "x", "b": "y"})
    assert type(renamed) is ExtendedDFA and renamed.input_symbols == {"x", "y"}
    assert renamed.accepts_input("xxx") and not renamed.accepts_input("xy")
    assert d.input_symbols == {"a", "b"}                               # l'original n'est pas modifié


def test_merging_symbols_with_same_target_stays_deterministic():
    dfa = ExtendedDFA(states={"s", "t"}, input_symbols={"a", "b"},
                      transitions={"s": {"a": "t", "b": "t"}, "t": {"a": "t", "b": "t"}},
                      initial_state="s", final_states={"t"})
    merged = dfa.project({"a": "x", "b": "x"})
    assert type(merged) is ExtendedDFA and merged.accepts_input("x") and not merged.accepts_input("")


def test_merging_symbols_with_different_targets_gives_an_nfa(d):
    merged = d.project({"a": "x", "b": "x"})
    assert type(merged) is ExtendedNFA
    # tout mot x^k est l'image d'un mot de L : il suffit de choisir des b (neutres) : x^k vient de b^k
    assert all(merged.accepts_input("x" * k) for k in range(6))


def test_symbols_missing_from_the_map_are_kept(d):
    kept = d.project({"a": "x"})
    assert kept.input_symbols == {"x", "b"} and kept.accepts_input("xbxbx")


def test_nfa_stays_an_nfa_and_keeps_its_epsilon_transitions(n):
    projected = n.project({"a": "x"})
    assert type(projected) is ExtendedNFA and projected.input_symbols == {"x", "b"}
    assert projected.transitions["p"][""] == frozenset({"r"})
    assert projected.accepts_input("xx") == n.accepts_input("aa")


def test_erasing_everything_gives_an_empty_alphabet_nfa(d):
    erased = d.project({"a": None, "b": None})
    assert erased.input_symbols == frozenset()
    assert erased.accepts_input("") is True                            # L est non vide


def test_gnfa_is_not_supported(d):
    with pytest.raises(TypeError):
        ExtendedGNFA.from_dfa(d).project({"a": "x"})


# ------------------------------------------------- propriété contre un oracle
def _random_dfa(rng):
    size = rng.randint(1, 4)
    st = [str(i) for i in range(size)]
    return ExtendedDFA(states=set(st), input_symbols={"a", "b", "c"},
                       transitions={s: {a: rng.choice(st) for a in "abc"} for s in st},
                       initial_state="0", final_states={s for s in st if rng.random() < 0.4})


def _random_nfa(rng):
    size = rng.randint(1, 4)
    st = [str(i) for i in range(size)]
    trans = {}
    for s in st:
        row = {}
        for a in ("a", "b", "c", ""):
            targets = {t for t in st if rng.random() < 0.2}
            if targets:
                row[a] = frozenset(targets)
        trans[s] = row
    return ExtendedNFA(states=set(st), input_symbols={"a", "b", "c"}, transitions=trans,
                       initial_state="0", final_states={s for s in st if rng.random() < 0.4})


@pytest.mark.parametrize("seed", range(80))
def test_random_projection_matches_the_independent_oracle(seed):
    rng = random.Random(seed)
    fa = (_random_nfa if seed % 2 else _random_dfa)(rng)
    mapping = {a: rng.choice(["x", "y", "z", None]) for a in "abc"}
    projected = fa.project(mapping)
    alphabet = {v for v in mapping.values() if v is not None}
    assert projected.input_symbols == alphabet
    for word in _words(alphabet, 4):
        assert projected.accepts_input(word) == _image_has_preimage(fa, mapping, word), (mapping, word)
