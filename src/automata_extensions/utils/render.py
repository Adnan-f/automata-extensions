"""render_diagram : rendu d'un graphe pygraphviz via le binaire Graphviz en sous-processus.

Évite le crash natif qui peut survenir quand ``pygraphviz`` et ``manim``
(av/ffmpeg) chargent, dans le même processus, des versions différentes des
bibliothèques zlib/cairo/png.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union


def _find_binary(prog: str) -> Path:
    found = shutil.which(prog)
    if found:
        return Path(found)
    env_root = Path(sys.executable).parent
    windows = sys.platform.startswith("win")
    candidates = [env_root / (f"{prog}.exe" if windows else prog)]
    if windows:
        candidates.append(env_root.parent / "Library" / "bin" / f"{prog}.exe")
        candidates.append(env_root / "Library" / "bin" / f"{prog}.exe")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Binaire Graphviz introuvable : {prog!r}. Installez Graphviz "
        f"(Arch Linux : sudo pacman -S graphviz).")


def render_diagram(agraph: Union[str, object], filename, prog: str = "dot",
                   fmt: Optional[str] = None) -> Path:
    """
    Rend un graphe en image en appelant le binaire Graphviz en sous-processus.

    Parameters
    ----------
    agraph : AGraph or str
        Un objet ayant une méthode ``string()`` (ex. ``pygraphviz.AGraph``,
        retourné par ``dfa.show_diagram()``) ou directement du texte DOT.
    filename : str or Path
        Fichier de sortie ; son extension fixe le format si ``fmt`` est omis.
    prog : str
        Moteur de rendu (``dot``, ``neato``, ``circo``...).
    fmt : str, optional
        Format explicite (``png``, ``svg``, ``pdf``...).

    Returns
    -------
    pathlib.Path

    Raises
    ------
    FileNotFoundError
        Binaire Graphviz introuvable.
    RuntimeError
        Échec du rendu (message d'erreur de Graphviz).
    """
    path = Path(filename)
    fmt = fmt or path.suffix.lstrip(".") or "png"
    binary = _find_binary(prog)
    source = agraph if isinstance(agraph, str) else agraph.string()
    result = subprocess.run([str(binary), f"-T{fmt}", "-o", str(path)],
                            input=source, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"Échec du rendu Graphviz :\n{result.stderr}")
    return path
