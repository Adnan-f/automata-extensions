import random
import shutil
import subprocess

import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedGNFA, ExtendedNFA
from automata_extensions.fa.fa_mixins.visualisation import (dot_quote, state_label,
                                                            tex_escape)

HAS_DOT = shutil.which("dot") is not None
HAS_LATEX = shutil.which("pdflatex") is not None
needs_dot = pytest.mark.skipif(not HAS_DOT, reason="binaire Graphviz « dot » absent")
needs_latex = pytest.mark.skipif(not HAS_LATEX, reason="pdflatex absent")

PDF_DOT = [
    "digraph {", "\trankdir=LR", "\t__start__ [shape=point style=invis]", "\t__start__ -> s0",
    "\ts0 [label=0 shape=doublecircle]", "\ts1 [label=1 shape=circle]", "\ts2 [label=2 shape=circle]",
    "\ts0 -> s0 [label=b]", "\ts0 -> s1 [label=a]", "\ts1 -> s1 [label=b]",
    "\ts1 -> s2 [label=a]", "\ts2 -> s0 [label=a]", "\ts2 -> s2 [label=b]", "}"]


# ------------------------------------------------------------------ helpers
def test_state_label():
    assert state_label("q0") == "q0" and state_label(3) == "3"
    assert state_label(frozenset({"b", "a", "10", "2"})) == "{2,10,a,b}"
    assert state_label(("a", frozenset({"x"}))) == "(a,{x})"


def test_dot_quote():
    assert dot_quote("abc") == "abc" and dot_quote("0") == "0" and dot_quote("-1.5") == "-1.5"
    assert dot_quote("a b") == '"a b"' and dot_quote("ε") == '"ε"'
    assert dot_quote('a"b') == '"a\\"b"' and dot_quote("a\\b") == '"a\\\\b"'


def test_tex_escape():
    assert tex_escape("a_b") == r"a\_b" and tex_escape("50%") == r"50\%"
    assert tex_escape("ε") == r"$\varepsilon$"
    assert tex_escape("{x}&$#") == r"\{x\}\&\$\#"
    assert "textbackslash" in tex_escape("a\\b")


# ---------------------------------------------------------------------- dot
def test_dot_matches_pdf_exactly(d):
    assert d.dot().splitlines() == PDF_DOT


def test_dot_merges_parallel_edges_and_marks_epsilon(n):
    text = n.dot()
    assert '[label="ε"]' in text
    assert "label=a" in text and "label=b" in text
    nfa = ExtendedNFA(states={"p", "q"}, input_symbols={"a", "b"},
                      transitions={"p": {"a": {"q"}, "b": {"q"}}, "q": {}},
                      initial_state="p", final_states={"q"})
    assert nfa.dot().count("->") == 2                       # __start__ -> s0 et UNE seule arête p->q
    assert '[label="a,b"]' in nfa.dot()


def test_dot_natural_state_order():
    states = {f"q{i}" for i in (1, 2, 10, 11)}
    dfa = ExtendedDFA(states=states, input_symbols={"a"},
                      transitions={s: {"a": s} for s in states},
                      initial_state="q1", final_states={"q10"})
    labels = [line.split("label=")[1].split()[0] for line in dfa.dot().splitlines()
              if "shape=circle" in line or "shape=doublecircle" in line]
    assert labels == ["q1", "q2", "q10", "q11"]


def test_dot_frozenset_states_after_minimize(d):
    m = d.minimize()
    assert "{0}" in m.dot() and "frozenset" not in m.dot()


def test_dot_gnfa_labels(d):
    text = ExtendedGNFA.from_dfa(d).dot()
    assert "label=start" in text and "label=end" in text


def test_dot_is_deterministic_and_pure(d):
    assert d.dot() == d.dot()


# ------------------------------------------------------------------ graphviz
def test_graph_object_matches_dot(d):
    graphviz = pytest.importorskip("graphviz")
    g = d.graph()
    assert isinstance(g, graphviz.Digraph)
    assert g.source.strip() == d.dot()


@needs_dot
def test_svg_png_pdf_real_render(d):
    pytest.importorskip("graphviz")
    assert d.svg().lstrip().startswith("<?xml") and "<svg" in d.svg()
    assert d.png().startswith(b"\x89PNG")
    assert d.pdf().startswith(b"%PDF")


@needs_dot
def test_save_by_extension(d, tmp_path):
    pytest.importorskip("graphviz")
    for name, magic in [("a.png", b"\x89PNG"), ("a.pdf", b"%PDF"), ("a.svg", b"<?xml")]:
        path = d.save(tmp_path / name)
        assert path.read_bytes().lstrip().startswith(magic)
    assert (d.save(tmp_path / "a.dot")).read_text().startswith("digraph {")
    assert "\\documentclass" in d.save(tmp_path / "a.tex").read_text()


def test_save_unknown_extension(d, tmp_path):
    with pytest.raises(ValueError):
        d.save(tmp_path / "a.xyz")


def test_missing_dot_binary_gives_clear_error(d, monkeypatch):
    pytest.importorskip("graphviz")
    monkeypatch.setenv("PATH", "")
    with pytest.raises(RuntimeError, match="Graphviz"):
        d.svg()
    assert d._repr_svg_() is None                           # Jupyter : repli silencieux


@needs_dot
def test_repr_svg_for_jupyter(d):
    pytest.importorskip("graphviz")
    assert "<svg" in d._repr_svg_()


@needs_dot
@pytest.mark.parametrize("seed", range(15))
def test_dot_output_is_valid_for_awkward_state_names(seed):
    rng = random.Random(seed)
    names = ['a"b', "x y", "é", "back\\slash", "q_1", "10", "{s}", "a|b", "ε", "<t>", "q;1"]
    states = rng.sample(names, rng.randint(1, 6))
    dfa = ExtendedDFA(states=set(states), input_symbols={"a", "b"},
                      transitions={s: {x: rng.choice(states) for x in "ab"} for s in states},
                      initial_state=states[0], final_states={s for s in states if rng.random() < .4})
    result = subprocess.run(["dot", "-Tsvg"], input=dfa.dot(), text=True, capture_output=True)
    assert result.returncode == 0, result.stderr


# --------------------------------------------------------------------- tikz
def test_tikz_structure(d):
    t = d.tikz()
    assert t.startswith("\\begin{tikzpicture}") and t.rstrip().endswith("\\end{tikzpicture}")
    assert "state,initial,initial text=,accepting" in t         # s0 initial et final
    assert t.count("\\node") == 3 and t.count("edge") == 6
    assert "loop above" in t and "stealth'" not in t


def test_tikz_return_edge_avoids_intermediate_state(d):
    line = next(l for l in d.tikz().splitlines() if "(s2) edge" in l and "(s0)" in l)
    assert "bend" in line                                    # 2 -> 0 ne traverse pas 1


def test_tikz_escapes_special_characters():
    states = {"q_1", "a&b", "50%", "#x"}
    dfa = ExtendedDFA(states=states, input_symbols={"a"}, transitions={s: {"a": s} for s in states},
                      initial_state="q_1", final_states={"#x"})
    t = dfa.tikz()
    assert r"q\_1" in t and r"a\&b" in t and r"50\%" in t and r"\#x" in t


def test_latex_document(d):
    doc = d.latex()
    assert doc.startswith("\\documentclass") and "\\usetikzlibrary{automata}" in doc
    assert doc.rstrip().endswith("\\end{document}")


@needs_latex
@pytest.mark.parametrize("which", ["d", "thompson", "special"])
def test_latex_really_compiles(which, d, tmp_path):
    if which == "d":
        fa = d
    elif which == "thompson":
        fa = ExtendedNFA.from_regex("(a|b)*abb")
    else:
        states = {"q_1", "a&b", "50%", "#x", "$y", "{z}", "ε"}
        fa = ExtendedDFA(states=states, input_symbols={"a"}, transitions={s: {"a": "q_1"} for s in states},
                         initial_state="q_1", final_states={"#x"})
    (tmp_path / "x.tex").write_text(fa.latex(), encoding="utf-8")
    result = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "x.tex"],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout[-1500:]
    assert (tmp_path / "x.pdf").exists()


# ------------------------------------------------------------ layout / bends
def test_layout_columns_follow_bfs_depth(d):
    assert d._viz_layout() == {"0": (0, 0), "1": (1, 0), "2": (2, 0)}


def test_layout_places_unreachable_states_after():
    dfa = ExtendedDFA(states={"a", "b", "z"}, input_symbols={"x"},
                      transitions={"a": {"x": "b"}, "b": {"x": "b"}, "z": {"x": "z"}},
                      initial_state="a", final_states={"b"})
    lay = dfa._viz_layout()
    assert lay["a"] == (0, 0) and lay["b"] == (1, 0) and lay["z"][0] > 1


def test_bends_pair_curve_on_both_directions_and_straight_otherwise():
    dfa = ExtendedDFA(states={"p", "q"}, input_symbols={"a", "b"},
                      transitions={"p": {"a": "q", "b": "p"}, "q": {"a": "p", "b": "q"}},
                      initial_state="p", final_states={"q"})
    bends = dfa._viz_bends(dfa._viz_layout(), dfa._viz_edges())
    assert bends[("p", "q")] > 0 and bends[("q", "p")] > 0   # chacun du « sien » côté
    chain = ExtendedDFA(states={"a", "b"}, input_symbols={"x"},
                        transitions={"a": {"x": "b"}, "b": {"x": "b"}},
                        initial_state="a", final_states={"b"})
    assert chain._viz_bends(chain._viz_layout(), chain._viz_edges())[("a", "b")] == 0.0


def test_no_edge_crosses_another_state_in_thompson_nfa():
    from automata_extensions.fa.fa_mixins.visualisation import _COL_STRETCH, _curve_clearance
    nfa = ExtendedNFA.from_regex("(a|b)*abb")
    layout, edges = nfa._viz_layout(), nfa._viz_edges()
    bends = nfa._viz_bends(layout, edges)
    pos = {s: (c * _COL_STRETCH, r) for s, (c, r) in layout.items()}
    for src, dst, _ in edges:
        if src == dst:
            continue
        others = [p for s, p in pos.items() if s not in (src, dst)]
        # Garantie : l'arête ne touche aucun état. Un état a pour rayon 24 px = 0,2 unité
        # (une unité = 120 px) ; on exige 0,28 (≈ 10 px de jeu). La marge de confort
        # _CLEARANCE (0,42) est un objectif de la recherche, pas toujours atteignable.
        assert _curve_clearance(pos[src], pos[dst], bends[(src, dst)], others) >= 0.28, (src, dst)
