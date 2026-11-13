# Historique des versions

## 0.1.0 — novembre 2026

Première version complète, construite par phases (chacune sur sa branche, fusionnée dans `main`).

### Ajouté
- **Base** : `ExtendedFA`, `ExtendedDFA`, `ExtendedNFA`, `ExtendedGNFA` (héritage + mixins, automata-lib 9.2.0
  intact) ; correctif du bug `cached_method` ; `input_parameters` et `copy` fonctionnels.
- **Graphe** : BFS/DFS, accessibles, coaccessibles, utiles, `trim`, sous-automate induit, cycles,
  vide/fini, composantes fortement connexes (Tarjan).
- **DFA** : complétion, complément, produit paresseux, union/intersection/différence, inclusion,
  équivalence, isomorphisme, langages préfixe-clos.
- **Minimisation** : table de paires avec rounds, classes de Myhill-Nerode, minimisation, Brzozowski,
  automate des résiduels, monoïde syntaxique et test « sans étoile » (Schützenberger).
- **NFA** : ε-fermeture, suppression des ε, déterminisation, miroir, opérations rationnelles,
  quotients par un mot.
- **Expressions régulières** : AST normalisé, parseur, dérivées de Brzozowski, Glushkov, Thompson,
  `from_regex` (DFA), `to_regex`, `to_regex_arden`, variantes « optimum ».
- **Équations** : lemme d'Arden, `EquationSystem`, élimination d'états d'un GNFA.
- **Grammaires** : `Grammar`, conversions automate ↔ grammaire régulière (droite et gauche),
  dérivations, arbres de dérivation.
- **Simulation et visualisation** : `run`, `execution_trace`, DOT, TikZ, LaTeX, SVG/PNG/PDF,
  animation HTML autonome, `render_diagram`.
- **Pédagogie** : `shortest_word`, `distinguishing_word` (mot contre-exemple), générateur
  d'exercices corrigés automatiquement.
- **Qualité** : plus de 1000 tests (propriétés comparées à des définitions indépendantes, couverture du
  cahier des charges, exemples du README exécutés), documentation des algorithmes et de l'API.

### Corrigé en cours de route
- `trim()` / `minimize()` / `prefix_closed_sublanguage()` sur un langage vide.
- Détection du non-déterminisme par `isinstance(..., frozenset)` (faux quand les états sont des `frozenset`).
- `determinize` : fermeture ε de l'état initial calculée avant la suppression des ε ; ensemble vide traité.
- `reverse` : pas d'ε-préambule quand il n'y a qu'un état final (sinon Brzozowski non minimal).
- TikZ : `>=stealth'` invalide ; arêtes traversant un état ; SVG : pointes de flèche et cadrage.
