"""Les exemples du README sont exécutés : la valeur après « # -> » doit être celle obtenue.

Seuls les blocs ```python sont testés (un bloc ```python notest est ignoré). Les liens
relatifs du README doivent pointer vers des fichiers existants.
"""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
BLOCKS = re.findall(r"^```python\n(.*?)^```", README, re.S | re.M)
EXPECT = re.compile(r"#\s*->\s*(.+?)\s*$")


def test_readme_has_examples():
    assert len(BLOCKS) >= 6
    assert sum(1 for line in "\n".join(BLOCKS).splitlines() if EXPECT.search(line)) >= 25


def test_readme_examples_produce_the_documented_values():
    """Les blocs partagent un même espace de noms, dans l'ordre du README."""
    namespace: dict = {}
    checked = 0
    for number, block in enumerate(BLOCKS, 1):
        lines = block.splitlines()
        for node in ast.parse(block).body:
            match = EXPECT.search(lines[node.end_lineno - 1])
            if isinstance(node, ast.Expr) and match:
                value = eval(compile(ast.Expression(node.value), f"<README bloc {number}>", "eval"),
                             namespace)
                assert repr(value) == match.group(1), (
                    f"README, bloc {number}, ligne {node.lineno} : "
                    f"documenté {match.group(1)!r}, obtenu {value!r}")
                checked += 1
            else:
                exec(compile(ast.Module([node], []), f"<README bloc {number}>", "exec"), namespace)
    assert checked >= 25


def _local_links():
    links = re.findall(r"\]\((?!https?://|#|mailto:)([^)\s]+)\)", README)
    return sorted({link.split("#")[0] for link in links})


@pytest.mark.parametrize("link", _local_links())
def test_readme_local_links_exist(link):
    assert (ROOT / link).exists(), f"lien cassé dans le README : {link}"
