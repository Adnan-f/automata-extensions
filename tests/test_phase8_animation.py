import json
import os
import re
import shutil
import subprocess
import textwrap

import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedGNFA, ExtendedNFA
from automata_extensions.utils.render import render_diagram

HAS_DOT = shutil.which("dot") is not None


def _data(page: str) -> dict:
    raw = re.search(r'<script id="automaton-data" type="application/json">(.*?)</script>', page, re.S)
    return json.loads(raw.group(1))


# ------------------------------------------------------------------ contenu
def test_animate_dfa_steps_and_verdict(d):
    page = d.animate("aab")
    data = _data(page)
    assert data["word"] == "aab" and data["accepted"] is False
    assert [s["consumed"] for s in data["steps"]] == [0, 1, 2, 3]
    assert [s["active"] for s in data["steps"]] == [["s0"], ["s1"], ["s2"], ["s2"]]
    assert data["steps"][1]["edges"] == ["s0_s1"]
    assert data["steps"][0]["note"] == "État initial : 0"
    assert data["steps"][1]["note"] == "Lecture de « a » : 0 → 1"
    assert "Lecture du mot « aab »" in page


def test_animate_accepted_word(d):
    assert _data(d.animate("aaa"))["accepted"] is True


def test_animate_empty_word_title_and_single_step(d):
    page = d.animate("")
    assert "Lecture du mot « ε »" in page
    data = _data(page)
    assert len(data["steps"]) == 1 and data["accepted"] is True


def test_animate_nfa_shows_all_active_states(n):
    data = _data(n.animate("ab"))
    assert data["steps"][0]["active"] == ["s0", "s2"]                  # p, r (ε-fermeture)
    assert data["steps"][1]["active"] == ["s0", "s1", "s2"]
    assert "États initiaux" in data["steps"][0]["note"]
    assert data["accepted"] is True


def test_animate_blocked_dfa_and_unknown_symbol():
    partial = ExtendedDFA(states={"q0", "q1"}, input_symbols={"a"},
                          transitions={"q0": {"a": "q1"}, "q1": {}}, initial_state="q0",
                          final_states={"q1"}, allow_partial=True)
    data = _data(partial.animate("aa"))
    assert data["steps"][-1]["blocked"] is True and "Blocage" in data["steps"][-1]["note"]
    assert data["accepted"] is False
    assert _data(partial.animate("z"))["steps"][-1]["blocked"] is True


def test_animate_nfa_dies_when_no_active_state(n):
    data = _data(n.animate("bbb"))
    assert data["steps"][-1]["active"] == [] and "plus aucun état actif" in data["steps"][-1]["note"]


def test_animate_ids_are_consistent_with_svg(n):
    page = n.animate("abab")
    data = _data(page)
    svg_ids = set(re.findall(r'id="((?:n|e)_[^"]+)"', page))
    for step in data["steps"]:
        for sid in step["active"]:
            assert f"n_{sid}" in svg_ids
        for key in step["edges"]:
            assert f"e_{key}" in svg_ids


def test_animate_is_self_contained(d):
    page = d.animate("ab")
    assert page.startswith("<!DOCTYPE html>")
    assert not re.search(r'(src|href)\s*=\s*"https?://', page)
    assert "<link" not in page and page.count("<script") == 2


def test_animate_escapes_hostile_state_names_and_words():
    evil = "</script><img src=x onerror=alert(1)>"
    dfa = ExtendedDFA(states={evil, 'q"1'}, input_symbols={"a", "<"},
                      transitions={evil: {"a": 'q"1', "<": evil}, 'q"1': {"a": evil, "<": 'q"1'}},
                      initial_state=evil, final_states={'q"1'})
    page = dfa.animate("a<a")
    assert page.count("</script>") == 2 and "<img" not in page
    assert _data(page)["word"] == "a<a"


def test_animate_writes_file(d, tmp_path):
    target = tmp_path / "anim.html"
    page = d.animate("aab", path=target)
    assert target.read_text(encoding="utf-8") == page


def test_animate_gnfa_not_supported(d):
    with pytest.raises(TypeError):
        ExtendedGNFA.from_dfa(d).animate("a")


# --------------------------------------------- vrai JavaScript (node + jsdom)
def _jsdom_available() -> bool:
    if not shutil.which("node"):
        return False
    return subprocess.run(["node", "-e", "require('jsdom')"], capture_output=True,
                          env=os.environ).returncode == 0


@pytest.mark.skipif(not _jsdom_available(), reason="node + jsdom absents (NODE_PATH)")
def test_animation_javascript_runs_in_jsdom(d, tmp_path):
    page = tmp_path / "p.html"
    d.animate("aab", path=page)
    script = textwrap.dedent("""
        const { JSDOM } = require("jsdom"); const fs = require("fs");
        const dom = new JSDOM(fs.readFileSync(process.argv[1], "utf8"), { runScripts: "dangerously" });
        const errors = []; dom.window.addEventListener("error", e => errors.push(String(e.message)));
        const d = dom.window.document, $ = id => d.getElementById(id), out = [];
        const snap = () => ({ active: [...d.querySelectorAll(".state.active")].map(e => e.id),
          used: [...d.querySelectorAll(".edge.used")].map(e => e.id),
          counter: $("counter").textContent, verdict: $("verdict").textContent,
          marker: $("e_s0_s1").querySelector("path").getAttribute("marker-end") });
        for (let k = 0; k < 6; k++) { out.push(snap()); if ($("next").disabled) break; $("next").click(); }
        $("reset").click(); out.push(snap());
        console.log(JSON.stringify({ errors, out }));
    """)
    result = subprocess.run(["node", "-e", script, str(page)], capture_output=True, text=True,
                            env=os.environ)
    assert result.returncode == 0, result.stderr
    run = json.loads(result.stdout)
    assert run["errors"] == []
    steps = run["out"]
    assert [s["active"] for s in steps] == [["n_s0"], ["n_s1"], ["n_s2"], ["n_s2"], ["n_s0"]]
    assert steps[1]["used"] == ["e_s0_s1"] and steps[1]["marker"] == "url(#arrow-used)"
    assert steps[0]["marker"] == "url(#arrow)"
    assert steps[3]["verdict"] == "✘ mot rejeté" and steps[3]["counter"] == "4 / 4"
    assert steps[4]["counter"] == "1 / 4"


# ------------------------------------------------------------ render_diagram
@pytest.mark.skipif(not HAS_DOT, reason="binaire Graphviz « dot » absent")
def test_render_diagram_with_dot_text_and_duck_typed_graph(d, tmp_path):
    class FakeAGraph:                                       # imite pygraphviz.AGraph
        def string(self):
            return d.dot()

    for source, name in [(d.dot(), "a.png"), (FakeAGraph(), "b.svg")]:
        out = render_diagram(source, tmp_path / name)
        assert out.exists() and out.stat().st_size > 100
    assert render_diagram(d.dot(), tmp_path / "noext", fmt="svg").read_text().lstrip().startswith("<?xml")


def test_render_diagram_missing_binary(d, tmp_path, monkeypatch):
    monkeypatch.setattr("shutil.which", lambda prog: None)
    monkeypatch.setattr("sys.executable", str(tmp_path / "nowhere" / "python"))
    with pytest.raises(FileNotFoundError, match="Graphviz"):
        render_diagram(d.dot(), tmp_path / "x.png")


@pytest.mark.skipif(not HAS_DOT, reason="binaire Graphviz « dot » absent")
def test_render_diagram_reports_graphviz_errors(tmp_path):
    with pytest.raises(RuntimeError, match="Échec du rendu"):
        render_diagram("digraph { this is not valid", tmp_path / "x.png")
