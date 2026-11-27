# Supplément d'API : expressions, grammaires et algèbre

Ce supplément complète la référence PDF principale avec les API ajoutées depuis sa première
édition. Les signatures, résumés et complexités de toutes les méthodes d'automates sont aussi
maintenus dans [`API.md`](API.md), généré depuis les docstrings. Les exemples ci-dessous utilisent
un jeu de données commun : exécuter d'abord le bloc de préparation, puis le bloc correspondant à
l'API recherchée. Les résultats peuvent varier dans leur ordre d'affichage lorsque Python
représente un ensemble.

## Préparation

```python
from automata_extensions import ExtendedDFA, ExtendedNFA, parse_regex
from automata_extensions.algebra import TransitionMonoid
from automata_extensions.equations import EquationSystem, arden
from automata_extensions.exercises import KINDS, describe, generate
from automata_extensions.grammar import Grammar, NotDerivableError, Production
from automata_extensions.regex import (
    EMPTY, EPSILON, Concat, Empty, Epsilon, Regex, RegexSyntaxError, Star,
    Symbol, Union, concat, optional, parse, plus, star, union,
)

dfa = ExtendedDFA.from_regex("(a|b)*abb")
nfa = ExtendedNFA.from_regex("(a|b)*abb")
regex = parse("(a|b)*abb")
grammar = Grammar.from_string("S -> aS | b")
assert isinstance(regex, Regex)
assert parse_regex("a*") == parse("a*")
```

## API des automates

Les classes `ExtendedDFA`, `ExtendedNFA` et `ExtendedGNFA` héritent des objets correspondants
d'`automata-lib`. Leurs constructeurs reprennent les paramètres de la bibliothèque d'origine ;
les méthodes suivantes sont les ajouts pédagogiques.

### Mot témoin le plus court

```python
assert dfa.shortest_word() == "abb"
```

### Mot distinguant deux langages

```python
other = ExtendedDFA.from_regex("(a|b)*ab")
assert dfa.distinguishing_word(other) == "ab"
```

### Résiduels et monoïde syntaxique

```python
representatives = dfa.residuals()
monoid = dfa.transition_monoid()
```

### Propriété star-free

```python
dfa.is_star_free()
```

### Système d'équations

```python
system = dfa.to_equations()
solution = system.solve()
```

### Grammaire linéaire à gauche

```python
left_grammar = dfa.to_left_grammar()
assert left_grammar.is_left_linear()
```

### Export DOT

```python
dfa.save("automate.dot")
```

Un GNFA peut être obtenu depuis un DFA. L'élimination d'un état renvoie un nouvel automate ;
`eliminate_states` laisse les deux états d'entrée/sortie nécessaires à l'expression résultante.

```python
from automata_extensions.fa.gnfa import ExtendedGNFA

gnfa = ExtendedGNFA.from_dfa(dfa)
intermediate = next(
    state for state in gnfa.states
    if state != gnfa.initial_state and state not in gnfa.final_states
)
without_one_state = gnfa.eliminate_state(intermediate)
two_state_gnfa = gnfa.eliminate_states()
```

## Expressions régulières

`parse` et `parse_regex` analysent `|`, `*`, `+`, `?`, les parenthèses et les échappements. Les
constructeurs `union`, `concat`, `star`, `plus`, `optional`, ainsi que les nœuds `Empty`,
`Epsilon`, `Symbol`, `Union`, `Concat` et `Star`, construisent l'AST immuable. `EMPTY` et `EPSILON`
sont les constantes des langages vide et du mot vide.

```python
a, b = Symbol("a"), Symbol("b")
expr = concat(a, star(union(a, b)))
assert expr == parse("a(a|b)*")
assert EMPTY == Empty()
assert str(EPSILON) == "()"
assert Empty() == EMPTY
assert str(Epsilon()) == "()"
assert str(Union((a, b))) == "a|b"
assert str(Concat((a, b))) == "ab"
assert str(Star(a)) == "a*"
assert str(plus(a)) == "aa*"
assert str(optional(a)) == "a?"
```

Chaque occurrence de symbole reçoit une position. `firstpos`, `lastpos` et `followpos` calculent
les ensembles de positions de Glushkov ; `nullable` teste l'acceptation du mot vide. `derivative`
calcule le quotient à gauche, `simplify` normalise l'AST et `size` compte ses nœuds.

```python
assert regex.nullable() is False
assert regex.symbols() == frozenset({"a", "b"})
assert regex.size() > 0
assert regex.positions() == {1: "a", 2: "b", 3: "a", 4: "b", 5: "b"}
assert regex.firstpos() == frozenset({1, 2, 3})
assert regex.lastpos() == frozenset({5})
assert regex.followpos()[4] == frozenset({5})
assert regex.derivative("a").simplify().size() > 0
assert str(parse("(a|())*b**").simplify()) == "a*b*"
```

Les conversions rendent le choix d'algorithme explicite : dérivées de Brzozowski (`to_dfa`),
construction de Thompson (`to_nfa`) ou automate de Glushkov sans transition epsilon
(`to_glushkov_nfa`).

```python
assert regex.to_dfa().is_equivalent(dfa)
assert regex.to_nfa().determinize().is_equivalent(nfa.determinize())
glushkov = regex.to_glushkov_nfa()
assert all("" not in row for row in glushkov.transitions.values())
```

Une syntaxe invalide lève `RegexSyntaxError`, sous-classe de `ValueError`.

```python
try:
    parse("a|")
except RegexSyntaxError:
    pass
```

## Grammaires et arbres de dérivation

`Grammar.from_string` lit une règle par ligne. `Production(lhs, rhs)` représente une production,
où `rhs` est un tuple de symboles ; un tuple vide représente epsilon. Les grammaires régulières
peuvent être testées (`generates`), classées (linéaires à droite/gauche), renversées (`reverse`)
et converties en NFA (`to_nfa`). `rules_for` récupère les productions d'un non-terminal.

```python
assert grammar.is_regular() and grammar.is_right_linear()
assert grammar.generates("aaab")
assert not grammar.generates("aaba")
assert len(grammar.rules_for("S")) == 2
assert Production("S", ("a", "S")) in grammar.productions
assert grammar.to_nfa().accepts("aaab")
assert grammar.reverse().generates("baaa")
```

`derive` produit une dérivation la plus courte. `DerivationStep` expose ses étapes, règles,
forme finale et arbre de dérivation ; `ParseTree` fournit profondeur, feuilles, mot et source DOT.
Une cible non dérivable déclenche `NotDerivableError`.

```python
step = grammar.derive("aaab")
assert step.is_complete()
assert step.word() == "aaab"
assert step.sequence().startswith("S =>")
assert step.steps()[-1].is_complete()
assert step.rules()
tree = step.parse_tree()
assert tree.word() == "aaab"
assert tree.depth() > 0
assert tree.leaves()
assert tree.to_dot().startswith("digraph")
```

```python
try:
    grammar.derive("aaba")
except NotDerivableError:
    pass
```

Les automates produisent également des grammaires régulières équivalentes. `derivation_tree` est
le raccourci qui renvoie directement l'arbre d'un mot accepté.

```python
right = dfa.to_grammar()
left = dfa.to_left_grammar()
assert right.is_right_linear()
assert left.is_left_linear()
assert dfa.derivation_tree("abb").word() == "abb"
```

## Équations de langages

`EquationSystem.from_automaton` construit un système avec une inconnue par état ; `solve` renvoie
une expression régulière pour chaque inconnue. `arden(a, b)` résout l'équation `X = aX | b` sous
la condition usuelle que `a` ne contient pas epsilon.

```python
equations = EquationSystem.from_automaton(dfa)
assert equations.variables
solutions = equations.solve()
assert set(solutions) == set(equations.variables)
assert arden(Symbol("a"), Symbol("b")).nullable() is False
assert dfa.to_equations().solve()
```

## Monoïde de transitions

`TransitionMonoid` peut être calculé depuis un DFA (`transition_monoid`) ou depuis une table de
transition complète. Un élément représente une transformation d'états ; `element_of` et
`shortest_word` font le lien avec les mots. `multiply(f, g)` compose « f puis g ».

```python
monoid = dfa.transition_monoid()
identity = monoid.identity
element = monoid.element_of("abb")
assert monoid.shortest_word(element) == "abb"
assert monoid.multiply(identity, element) == element
assert monoid.idempotents()
monoid.is_group()
monoid.is_aperiodic()
monoid.is_commutative()

from_dfa = TransitionMonoid.from_dfa_table(
    ["q0", "q1"], ["a"], {"q0": {"a": "q1"}, "q1": {"a": "q1"}}
)
assert from_dfa.element_of("a") in from_dfa
```

## Exercices corrigés

`KINDS` donne les quatre types pris en charge. `generate(kind, seed)` est reproductible.
`Exercise.check` valide l'équivalence des langages ; `feedback` fournit un contre-exemple ou une
explication si la réponse n'est pas correcte. `describe` affiche les composantes d'un automate.

```python
assert KINDS == ("dfa_to_regex", "regex_to_dfa", "minimize", "determinize")
exercise = generate("minimize", seed=3)
same_exercise = generate("minimize", seed=3)
assert exercise.statement == same_exercise.statement
assert exercise.check(exercise.solution)
assert exercise.feedback(exercise.solution) is None
assert "États :" in describe(exercise.given)
```

Les générateurs bas niveau acceptent un `random.Random` pour rendre leur résultat déterministe.

```python
import random
from automata_extensions.exercises import random_dfa, random_nfa, random_regex

rng = random.Random(12)
random_dfa(rng, 3, ("a", "b"))
random_nfa(rng, 3, ("a", "b"))
random_regex(rng, ("a", "b"), depth=2)
```

## Rendu Graphviz

`render_diagram` prend une source DOT ou un objet compatible avec `string()`. Il appelle Graphviz
en sous-processus ; le binaire `dot` doit donc être installé.

```python
from automata_extensions.utils.render import render_diagram

svg_path = render_diagram(dfa.dot(), "automate.svg")
assert svg_path.suffix == ".svg"
```

## Utilitaires

Les fonctions d'ordre déterministe et d'échappement sont exposées dans leurs modules utilitaires.
`patch_cached_method` est appliqué automatiquement à l'import du paquet ; l'appel explicite reste
disponible pour les intégrations qui ont besoin de vérifier le correctif.

```python
from automata_extensions.utils.ordering import natural_key, sort_states, state_label
from automata_extensions.utils.patches import patch_cached_method

assert natural_key("q10") > natural_key("q2")
assert sort_states(["q10", "q2"]) == ["q2", "q10"]
assert state_label("q1") == "q1"
assert isinstance(patch_cached_method(), bool)
```

Les deux fonctions d'échappement sont utilisées par les générateurs DOT et LaTeX.

```python
from automata_extensions.fa.fa_mixins.visualisation import dot_quote, tex_escape

assert dot_quote('q"1') == '"q\\"1"'
assert tex_escape("q_1") == r"q\_1"
```

## Référence complète

La référence générée [`API.md`](API.md) recense 150 noms d'API de méthodes d'automates, avec les
classes concernées, une description et la complexité lorsque celle-ci est documentée. Le manuel
PDF principal présente les méthodes historiques avec exemples ; le présent supplément ajoute les
API récentes ci-dessus. L'ensemble constitue le manuel d'usage de l'extension. Les classes de
mixins et les fonctions préfixées par `_` sont des détails d'implémentation, pas une API publique
prise en charge.