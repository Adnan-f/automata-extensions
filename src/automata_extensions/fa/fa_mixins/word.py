"""WordMixin : reconnaissance d'un mot et trace lisible (items 15, 16)."""

from __future__ import annotations


class WordMixin:
    """``accepts`` (alias pédagogique) et ``run`` (trace textuelle)."""

    def accepts(self, word: str) -> bool:
        """
        Alias pédagogique de ``accepts_input``.

        Complexity
        ----------
        O(|mot|) pour un DFA ; O(|mot| * |Q|^2) pour un NFA.
        """
        return self.accepts_input(word)

    def run(self, word: str, sep: str = " → ") -> str:
        """
        Exécution de ``word`` sous forme de texte, ex. ``0 → 1 → 2 → 0 → accept``.

        Pour un DFA, la chaîne des états traversés ; pour un NFA, la chaîne des
        *ensembles* d'états actifs (ε-fermés), ex. ``{p, r} → {p, q, r} → accept``.
        Si l'automate se bloque (transition absente), la chaîne s'arrête là.
        Le dernier élément est ``accept`` ou ``reject``.

        Raises
        ------
        TypeError
            Pour un GNFA (pas de simulation pas à pas).

        Complexity
        ----------
        Celle de ``execution_trace``.
        """
        if not hasattr(self, "execution_trace"):
            raise TypeError("run n'est pas défini pour ce type d'automate (GNFA)")
        trace = self.execution_trace(word)
        chain = [self._format_config(self._trace_start())]
        chain += [self._format_config(step[2]) for step in trace]
        chain.append("accept" if self.accepts_input(word) else "reject")
        return sep.join(chain)
