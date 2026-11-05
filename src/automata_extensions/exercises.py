"""Générateur d'exercices corrigés automatiquement (§2.5 du cahier des charges).

Quatre types d'exercices, reproductibles grâce à une graine :

* ``dfa_to_regex`` : donner une expression régulière d'un automate ;
* ``regex_to_dfa`` : construire un DFA à partir d'une expression régulière ;
* ``minimize``     : minimiser un DFA (volontairement redondant) ;
* ``determinize``  : déterminiser un NFA (avec ε-transitions).

La correction ne compare pas des textes : elle teste l'*équivalence des
langages*. Toute réponse correcte est donc acceptée, et une réponse fausse
reçoit un **mot contre-exemple** (``distinguishing_word``) qu'on peut vérifier
à la main.

Exemple ::

    ex = generate("minimize", seed=3)
    print(ex.statement)
    ex.check(mon_dfa)          # True / False
    ex.feedback(mon_dfa)       # None si juste, sinon une explication
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import FrozenSet, Optional, Sequence

from .fa.dfa import ExtendedDFA
from .fa.nfa import ExtendedNFA
from .regex import Regex, concat, star, union
from .regex.ast import Symbol

KINDS = ("dfa_to_regex", "regex_to_dfa", "minimize", "determinize")
_MAX_ATTEMPTS = 500


# ---------------------------------------------------------------------------
# Description textuelle d'un automate
# ---------------------------------------------------------------------------
def describe(fa) -> str:
    """Description en français d'un DFA/NFA : états, alphabet, initial, finals, transitions."""
    states = sorted(map(str, fa.states), key=lambda s: (len(s), s))
    lines = [f"États : {', '.join(states)}",
             f"Alphabet : {', '.join(sorted(fa.input_symbols))}",
             f"État initial : {fa.initial_state}",
             f"États finaux : {', '.join(sorted(map(str, fa.final_states), key=lambda s: (len(s), s)))}",
             "Transitions :"]
    rows = []
    for src, row in fa.transitions.items():
        for symbol, target in row.items():
            for dst in (target if fa._nondeterministic else {target}):
                rows.append((str(src), "ε" if symbol == "" else symbol, str(dst)))
    for src, symbol, dst in sorted(rows, key=lambda r: ((len(r[0]), r[0]), r[1], (len(r[2]), r[2]))):
        lines.append(f"  {src} --{symbol}--> {dst}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Générateurs aléatoires
# ---------------------------------------------------------------------------
def _names(n: int) -> list:
    return [f"q{i}" for i in range(n)]


def random_dfa(rng: random.Random, size: int, alphabet: Sequence[str]) -> ExtendedDFA:
    """DFA complet aléatoire (états ``q0..``), langage ni vide ni universel."""
    states = _names(size)
    for _ in range(_MAX_ATTEMPTS):
        dfa = ExtendedDFA(
            states=set(states), input_symbols=set(alphabet),
            transitions={s: {a: rng.choice(states) for a in alphabet} for s in states},
            initial_state="q0", final_states={s for s in states if rng.random() < 0.4})
        if not dfa.is_empty() and not dfa.is_universal():
            return dfa
    raise RuntimeError("impossible de générer un DFA non trivial")


def random_nfa(rng: random.Random, size: int, alphabet: Sequence[str]) -> ExtendedNFA:
    """NFA aléatoire avec quelques ε-transitions (états ``q0..``), langage non trivial."""
    states = _names(size)
    for _ in range(_MAX_ATTEMPTS):
        transitions = {}
        for s in states:
            row = {}
            for a in list(alphabet) + [""]:
                targets = {t for t in states if rng.random() < (0.45 if a else 0.15)}
                if targets:
                    row[a] = frozenset(targets)
            transitions[s] = row
        nfa = ExtendedNFA(states=set(states), input_symbols=set(alphabet), transitions=transitions,
                          initial_state="q0", final_states={s for s in states if rng.random() < 0.4})
        dfa = nfa.determinize()
        if (not dfa.is_empty() and not dfa.is_universal() and len(dfa.states) >= size
                and any("" in row for row in transitions.values()) and not nfa.is_deterministic()):
            return nfa
    raise RuntimeError("impossible de générer un NFA non trivial")


def random_regex(rng: random.Random, alphabet: Sequence[str], depth: int) -> Regex:
    """Expression régulière aléatoire (AST normalisé)."""
    if depth == 0 or rng.random() < 0.2:
        return Symbol(rng.choice(list(alphabet)))
    op = rng.choice(["concat", "concat", "union", "star"])
    if op == "star":
        return star(random_regex(rng, alphabet, depth - 1))
    left, right = random_regex(rng, alphabet, depth - 1), random_regex(rng, alphabet, depth - 1)
    return concat(left, right) if op == "concat" else union(left, right)


def _bloat(rng: random.Random, minimal: ExtendedDFA) -> ExtendedDFA:
    """DFA équivalent mais redondant : états dupliqués (atteignables) + un état inaccessible."""
    states = sorted(minimal.states)
    transitions = {s: dict(minimal.transitions[s]) for s in states}
    finals = set(minimal.final_states)
    next_id = len(states)
    for original in rng.sample(states, k=min(2, len(states))):
        copy = f"q{next_id}"
        next_id += 1
        transitions[copy] = dict(minimal.transitions[original])
        if original in finals:
            finals.add(copy)
        redirect = [(s, a) for s in states for a, t in transitions[s].items() if t == original]
        if redirect:                                         # au moins un arc redirigé : la copie est atteignable
            s, a = rng.choice(redirect)
            transitions[s][a] = copy
    ghost = f"q{next_id}"                                    # inaccessible
    transitions[ghost] = {a: rng.choice(states) for a in minimal.input_symbols}
    all_states = set(transitions)
    result = ExtendedDFA(states=all_states, input_symbols=set(minimal.input_symbols),
                         transitions=transitions, initial_state="q0",
                         final_states=finals | ({ghost} if rng.random() < 0.5 else set()))
    return result


# ---------------------------------------------------------------------------
# Exercice
# ---------------------------------------------------------------------------
def _display(word: str) -> str:
    return "ε" if word == "" else word


@dataclass(frozen=True)
class Exercise:
    """
    Un exercice : énoncé, objet donné, une solution de référence et sa correction.

    Attributes
    ----------
    kind : str
        Un élément de ``KINDS``.
    seed : int
        Graine : ``generate(kind, seed)`` redonne exactement le même exercice.
    statement : str
        Énoncé en français, avec l'objet donné.
    given : object
        L'automate (``dfa_to_regex``, ``minimize``, ``determinize``) ou
        l'expression (``regex_to_dfa``) fournis à l'étudiant.
    solution : object
        Une réponse correcte (expression ou automate selon le type).
    alphabet : frozenset of str
    """

    kind: str
    seed: int
    statement: str
    given: object
    solution: object
    alphabet: FrozenSet[str]

    # ---- correction ------------------------------------------------------
    def _reference(self) -> ExtendedDFA:
        if self.kind == "dfa_to_regex":
            return self.given
        return self.solution

    def _candidate(self, answer):
        """Convertit la réponse en automate ; lève ``ValueError`` si elle est invalide."""
        if self.kind == "dfa_to_regex":
            if not isinstance(answer, str):
                raise ValueError("une expression régulière (texte) est attendue")
            return ExtendedDFA.from_regex(answer, input_symbols=self.alphabet)
        if isinstance(answer, str):
            raise ValueError("un automate est attendu, pas un texte")
        from .fa.fa_mixins.counterexample import _coerce
        try:
            return _coerce(answer)
        except TypeError as error:
            raise ValueError(str(error)) from error

    def feedback(self, answer) -> Optional[str]:
        """
        Correction commentée.

        Returns
        -------
        str or None
            ``None`` si la réponse est correcte ; sinon une explication
            (mot contre-exemple, automate non déterministe, non minimal...).
        """
        try:
            candidate = self._candidate(answer)
        except ValueError as error:
            return f"Réponse invalide : {error}."
        word = self._reference().distinguishing_word(candidate)
        if word is not None:
            reference_accepts = self._reference().accepts_input(word)
            who = "la solution l'accepte mais pas votre réponse" if reference_accepts \
                else "votre réponse l'accepte mais pas la solution"
            return f"Votre réponse et la solution diffèrent sur le mot « {_display(word)} » : {who}."
        if self.kind in ("regex_to_dfa", "minimize", "determinize") and not candidate.is_deterministic():
            return "Le langage est correct, mais l'automate doit être déterministe."
        if self.kind == "minimize":
            complete = candidate.complete()
            if not complete.is_minimal():
                needed = len(self.solution.states)
                return (f"Le langage est correct, mais l'automate n'est pas minimal "
                        f"({len(complete.states)} états au lieu de {needed}).")
        return None

    def check(self, answer) -> bool:
        """Vrai si la réponse est correcte (voir ``feedback``)."""
        return self.feedback(answer) is None

    def __str__(self) -> str:
        return self.statement


def generate(kind: str, seed: int = 0, alphabet: Sequence[str] = ("a", "b")) -> Exercise:
    """
    Génère un exercice reproductible.

    Parameters
    ----------
    kind : str
        ``dfa_to_regex``, ``regex_to_dfa``, ``minimize`` ou ``determinize``.
    seed : int
        Même graine, même exercice.
    alphabet : sequence of str
        Alphabet (``a``, ``b`` par défaut).

    Raises
    ------
    ValueError
        Type d'exercice inconnu.
    """
    if kind not in KINDS:
        raise ValueError(f"type d'exercice inconnu : {kind!r} (attendu : {', '.join(KINDS)})")
    rng = random.Random(f"{kind}:{seed}")
    alphabet = tuple(alphabet)
    frozen_alphabet = frozenset(alphabet)

    if kind == "dfa_to_regex":
        for _ in range(_MAX_ATTEMPTS):
            dfa = random_dfa(rng, rng.choice([3, 3, 4]), alphabet)
            if dfa.is_minimal():
                break
        statement = ("Donnez une expression régulière du langage reconnu par l'automate "
                     f"déterministe suivant.\n\n{describe(dfa)}")
        return Exercise(kind, seed, statement, dfa, dfa.to_regex_optimum(), frozen_alphabet)

    if kind == "regex_to_dfa":
        for _ in range(_MAX_ATTEMPTS):
            regex = random_regex(rng, alphabet, depth=3)
            text = str(regex)
            if not 5 <= len(text) <= 16:
                continue
            dfa = ExtendedDFA.from_regex(text, input_symbols=alphabet)
            if not dfa.is_empty() and not dfa.is_universal() and 3 <= len(dfa.residuals()) <= 6:
                break
        statement = ("Construisez un automate fini déterministe reconnaissant le langage de "
                     f"l'expression régulière suivante : {text}")
        return Exercise(kind, seed, statement, text, dfa.residual_automaton(), frozen_alphabet)

    if kind == "minimize":
        for _ in range(_MAX_ATTEMPTS):
            base = random_dfa(rng, rng.choice([3, 4]), alphabet).residual_automaton()
            if len(base.states) >= 3:
                break
        bloated = _bloat(rng, base)
        solution = bloated.residual_automaton()
        statement = ("Minimisez l'automate déterministe suivant (donnez l'automate minimal "
                     f"équivalent).\n\n{describe(bloated)}")
        return Exercise(kind, seed, statement, bloated, solution, frozen_alphabet)

    nfa = random_nfa(rng, 3, alphabet)
    statement = ("Déterminisez l'automate non déterministe suivant (donnez un automate "
                 f"déterministe équivalent ; « ε » désigne une transition spontanée).\n\n{describe(nfa)}")
    return Exercise(kind, seed, statement, nfa, nfa.determinize(), frozen_alphabet)
