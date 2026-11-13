# Les algorithmes, expliqués

Ce document explique **comment** et **pourquoi** chaque famille d'algorithmes fonctionne, avec sa
complexité. La référence méthode par méthode (générée depuis les docstrings) est dans
[API.md](API.md). Notations : *Q* états, *Σ* alphabet, *E* transitions, *n = |Q|*.

## 0. Représentation

| Objet | Représentation (automata-lib 9.2.0) |
|---|---|
| DFA | `transitions[état][symbole] -> état` ; peut être *partiel* (`allow_partial=True`) |
| NFA | `transitions[état][symbole] -> frozenset d'états` ; la clé `""` est une ε-transition |
| GNFA | `transitions[p][q] -> expression régulière` (ou `None`) ; états spéciaux initial et final |

Tous les automates sont **immuables** : un algorithme construit un nouvel objet. Les algorithmes qui
ne lisent que `Q`, les transitions, l'état initial et les états finaux sont écrits une seule fois
dans `ExtendedFA` et marchent donc sur DFA, NFA et GNFA. Un drapeau de classe
`_nondeterministic` distingue « une transition = un état » de « une transition = un ensemble »
(tester `isinstance(cible, frozenset)` serait faux : après `minimize()`, les *états eux-mêmes* sont des
`frozenset`).

## 1. Graphe et accessibilité

- **BFS / DFS** (`bfs`, `dfs`) : parcours classiques depuis l'état initial, en *O(n + |E|)*. Les
  successeurs sont visités dans un ordre déterministe, donc les résultats sont reproductibles.
- **Accessibles** : états atteints depuis l'état initial. **Coaccessibles** : états depuis lesquels on
  atteint un état final, calculés par un BFS sur le **graphe renversé** depuis les finaux.
  **Utiles** = intersection ; `trim` restreint l'automate aux états utiles. Pour un langage vide,
  aucun état n'est utile : `trim` garde alors le seul état initial.
- **Composantes fortement connexes** (`strongly_connected_components`) : algorithme de **Tarjan**,
  version itérative (une chaîne de 3000 états ne dépasse pas la limite de récursion). Chaque état
  reçoit un indice de découverte et un `low-link` ; quand `low == indice`, on dépile une composante.
  Les composantes sortent en **ordre topologique inverse**. *O(n + |E|)*.
- **Cycle** (`has_cycle`) : DFS à trois couleurs (blanc / gris / noir) ; une arête vers un état *gris*
  (sur la pile) est un cycle. **Vide** : aucun accessible n'est final. **Fini** : le langage est
  infini ssi un cycle existe parmi les états **utiles** (un tel cycle se « pompe » sans quitter un
  chemin acceptant). *O(n + |E|)*.

## 2. Opérations sur les DFA

- **Complétion** : un état puits reçoit toutes les transitions manquantes. **Complément** : compléter
  *puis* échanger finals et non-finals (oublier de compléter est l'erreur classique). *O(n·|Σ|)*.
- **Produit** (`product`) : états = couples `(p, q)`, **construits paresseusement** depuis le couple
  initial, donc seuls les couples accessibles existent. L'union, l'intersection et la différence ne
  diffèrent que par la fonction `is_final(p, q)`. *O(n₁·n₂·|Σ|)*.
- **Inclusion** : `L₁ ⊆ L₂` ssi `L₁ \ L₂ = ∅`. **Équivalence** : double inclusion. Les automates
  doivent partager le même alphabet (sinon `ValueError`), sauf pour `distinguishing_word`.
- **Isomorphisme** : BFS synchronisé depuis les deux états initiaux qui construit une bijection ;
  elle est forcée à chaque pas car les automates sont déterministes. *O(n·|Σ|)*.
- **Préfixe-clos** : un langage est préfixe-clos ssi tous ses états *utiles* sont finaux ; le plus grand
  sous-langage préfixe-clos s'obtient en rendant finaux tous les états utiles.

## 3. Minimisation et structure algébrique

- **Table de paires** (`pair_table`) : une paire `{p, q}` reçoit le **round 0** si exactement un des deux
  est final ; sinon le **round r** si un symbole mène à une paire marquée au round `r-1`. Une paire
  jamais marquée désigne deux états **équivalents**. Propriété utile : *le round d'une paire est la
  longueur du plus court mot qui distingue les deux états* (vérifié par test contre
  `distinguishing_word`). *O(n²·|Σ|)* par round.
- **Classes de Myhill-Nerode** : les états non distinguables (union-find sur les paires `None`).
  **Minimiser** = fusionner chaque classe ; le résultat est unique à renommage près.
- **Brzozowski** (`brzozowski_minimize`) : `déterminiser(renverser(déterminiser(renverser(A))))` donne le
  DFA minimal. Piège rencontré : quand l'automate n'a qu'un état final, `reverse` doit le prendre
  *directement* comme initial (pas d'ε-préambule), sinon la déterminisation produit deux sous-ensembles
  équivalents et le résultat n'est plus minimal. Pire cas exponentiel.
- **Automate des résiduels** (`residual_automaton`) : états = résiduels `u⁻¹L`, nommés `q0, q1, …` dans
  l'ordre de découverte d'un BFS (`residuals()` donne le plus court mot de chaque classe).
- **Monoïde de transitions / syntaxique** : un mot `w` agit par `q ↦ δ*(q, w)` ; on engendre toutes les
  transformations par BFS depuis l'identité. Le monoïde du **DFA minimal** est le monoïde syntaxique.
  **Schützenberger** : le langage est *sans étoile* ssi ce monoïde est **apériodique** (`xᵐ = xᵐ⁺¹`
  pour un `m`). Le langage « nombre de a multiple de 3 » a pour monoïde ℤ/3ℤ, qui n'est pas apériodique.

## 4. Automates non déterministes

- **ε-fermeture** : états atteignables par ε-transitions seulement (DFS). *O(n + |E|)*.
- **Suppression des ε** : `δ'(p, a) = fermeture(⋃ δ(q, a) pour q ∈ fermeture(p))` ; `p` devient final si
  sa fermeture contient un final.
- **Déterminisation** (construction des sous-ensembles) : états = ensembles d'états, construits depuis
  la fermeture de l'état initial ; l'**ensemble vide** est un état à part entière (puits implicite).
  Pire cas *O(2ⁿ)*. Piège : la fermeture de l'état initial se calcule **avant** de supprimer les ε.
- **Opérations rationnelles** (`union`, `concatenation`, `kleene_star`) : ajout d'ε-transitions entre
  copies disjointes des automates ; le résultat est un NFA. *O(n₁ + n₂)*.
- **Quotients par un mot** : le quotient gauche `w⁻¹L` déplace l'état initial après lecture de `w` ;
  le quotient droit `Lw⁻¹` rend finaux les états depuis lesquels `w` mène à un final.

## 5. Expressions régulières

- **AST normalisé** : l'union est aplatie, sans doublon et **triée** (associativité, commutativité,
  idempotence) ; `∅` est absorbant pour la concaténation ; `ε` est neutre ; `(ε|r)* = r*`, `r** = r*`.
- **Dérivées de Brzozowski** : `a⁻¹(r)` se calcule par récurrence structurelle (`ν(r)` = « r contient ε ») :

  ```text
  a⁻¹(b) = ε si a = b, ∅ sinon         a⁻¹(r|s) = a⁻¹(r) | a⁻¹(s)
  a⁻¹(r·s) = a⁻¹(r)·s | (ν(r) ? a⁻¹(s) : ∅)      a⁻¹(r*) = a⁻¹(r)·r*
  ```

  Grâce à la normalisation, l'ensemble des dérivées est **fini** : c'est l'automate (complet) du
  langage (`Regex.to_dfa`, `DFA.from_regex`).
- **Glushkov** : on numérote les occurrences de symboles ; `firstpos`, `lastpos`, `followpos` donnent
  directement un NFA **sans ε** à `n+1` états.
- **Thompson** : construction récursive avec ε-transitions ; chaque état a au plus 2 transitions sortantes,
  un seul état final, au plus `2·|r|` états.

## 6. Automate → expression régulière

- **Élimination d'états** (GNFA) : pour supprimer `q`, chaque `p → r` devient
  `T(p,r) | T(p,q)·T(q,q)*·T(q,r)`. `to_regex()` délègue à automata-lib ; `eliminate_state(s)` expose un pas
  à la fois. *O(n³)* opérations sur des expressions (taille potentiellement exponentielle).
- **Lemme d'Arden** : `X = A·X | B` a pour plus petite solution `X = A*·B`. Un automate donne le système
  `X_q = Σ a·X_q' | (ε si q final)` ; on élimine les inconnues une à une (Arden pour l'auto-référence,
  substitution dans les autres équations), puis on remonte. `EquationSystem.solve()` donne une
  expression pour **chaque** état (le langage depuis cet état).
- **Variantes « optimum »** : le texte dépend de l'ordre d'élimination, jamais le langage. On essaie tous
  les ordres (jusqu'à 6 états, sinon un échantillon reproductible) et on garde la plus courte. Aucune
  garantie de minimalité globale.

## 7. Grammaires

- **Automate → grammaire** : un état devient un non-terminal, `p --a--> q` la règle `p → a q`, un final `f → ε`.
  La grammaire **linéaire à gauche** s'obtient en renversant celle de l'automate miroir.
- **Grammaire → NFA** : une règle `A → a₁…aₖ B` devient un chemin de `k` transitions (états intermédiaires
  créés si `k > 1`) ; `A → w` mène à un état final unique. Les grammaires linéaires à gauche passent par
  renversement.
- **Dérivation** (`derive`) : BFS sur les couples *(non-terminal, position dans le mot)* ; le premier chemin
  trouvé est une dérivation **la plus courte**. Elle donne la suite de formes sentencielles
  (`S => aS => aaS => aab`) et l'arbre de dérivation. Limité aux grammaires régulières.

## 8. Contre-exemples et exercices

- **Mot distinguant** : on construit le produit des deux DFA (déterminisés, sur l'union des alphabets) avec
  `is_final = (p final) XOR (q final)` ; le plus court mot accepté de ce produit est un témoin minimal
  (BFS à symboles ordonnés, donc minimal en longueur puis lexicographiquement). *O(n₁·n₂·|Σ|)*.
- **Exercices** : générés par graine ; la correction teste l'**équivalence des langages** (toute réponse
  correcte est acceptée) et fournit un contre-exemple, ou signale « pas minimal », « pas déterministe ».

## 9. Visualisation

- **DOT** : texte pur, états `s0, s1, …` triés naturellement, arêtes parallèles fusionnées (`a,b`).
- **Placement** : colonne = distance (BFS) depuis l'état initial, ligne = rang dans la colonne.
- **Arêtes** : pour chacune on essaie des courbures croissantes (droite d'abord, puis des deux côtés) et on
  garde la première qui reste à distance des autres états ; un aller-retour est toujours courbé.
- **TikZ / LaTeX** : bibliothèque `automata`, mêmes positions et mêmes courbures (`bend left=θ`).
- **Animation HTML** : SVG généré en Python, JavaScript minimal (états actifs et transitions empruntées
  coloriés à chaque pas), aucune dépendance externe.

## 10. Tableau récapitulatif des complexités

| Algorithme | Temps |
|---|---|
| BFS, DFS, accessibles, coaccessibles, trim, SCC, cycle | *O(n + \|E\|)* |
| Complétion, complément | *O(n·\|Σ\|)* |
| Produit, union, intersection, différence, inclusion, mot distinguant | *O(n₁·n₂·\|Σ\|)* |
| Isomorphisme de DFA | *O(n·\|Σ\|)* |
| Table de paires, classes d'équivalence, minimisation | *O(n²·\|Σ\|)* par round |
| Déterminisation, Brzozowski | *O(2ⁿ)* pire cas |
| ε-fermeture, quotients par un mot | *O(n + \|E\|)* par fermeture |
| Opérations rationnelles (NFA) | *O(n₁ + n₂)* |
| Dérivées (DFA d'une regex) | *O(d·\|Σ\|)* dérivées, *d* fini |
| Élimination d'états, Arden | *O(n³)* opérations sur expressions |
| Monoïde de transitions | *O(\|M\|·\|Σ\|·n)*, \|M\| ≤ nⁿ |
