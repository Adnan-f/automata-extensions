# Référence de l'API

Généré par `python docs/gen_api.py` à partir des docstrings — ne pas éditer à la main.
La colonne *Disponible sur* indique les classes (DFA, NFA, GNFA) qui possèdent la méthode.

## `fa.base`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `input_parameters` | DFA, NFA, GNFA | Attributs publics permettant de reconstruire l'automate. | O(\|MRO\| + nombre d'attributs) |

## `fa.dfa_mixins.complement`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `complement` | DFA | Complémentaire du langage reconnu. | O(\|Q\| * \|Sigma\|) ; O(\|Q\|^2 * \|Sigma\|) avec ``minify=True``. |
| `is_universal` | DFA | Teste si l'automate reconnaît Sigma* tout entier. | O(\|Q\| * \|Sigma\|) |

## `fa.dfa_mixins.completeness`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `complete` | DFA | Complète le DFA : ajoute un état puits si nécessaire. | O(\|Q\| * \|Sigma\|) |
| `is_complete` | DFA | Teste si la fonction de transition est totale. | O(\|Q\| * \|Sigma\|) |

## `fa.dfa_mixins.difference`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `difference` | DFA | Différence des langages : mots de ``self`` absents de ``other``. | O(\|Q1\| * \|Q2\| * \|Sigma\|) |

## `fa.dfa_mixins.execution`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `execution_trace` | DFA | Trace complète de la lecture de ``word``. | O(\|mot\|) |

## `fa.dfa_mixins.from_regex`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `from_regex` | DFA | DFA reconnaissant le langage de ``regex``, sans passer par un NFA. | O(n * \|Sigma\|) dérivées, n = nombre de dérivées distinctes. |

## `fa.dfa_mixins.inclusion`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `is_equivalent` | DFA | Teste l'égalité de langages L(self) = L(other) par double inclusion. | O(\|Q1\| * \|Q2\| * \|Sigma\|) |
| `is_included_in` | DFA | Teste si L(self) ⊆ L(other). | O(\|Q1\| * \|Q2\| * \|Sigma\|) |

## `fa.dfa_mixins.isomorphism`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `is_isomorphic_to` | DFA | Teste l'existence d'un isomorphisme d'automates entre ``self`` et ``other``. | O(\|Q\| * \|Sigma\|) |

## `fa.dfa_mixins.minimization`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `distinguishable_states` | DFA | Ensemble des paires d'états distinguables (celles marquées dans ``pair_table``). | Celle de ``pair_table``. |
| `equivalence_classes` | DFA | Classes d'équivalence de Myhill-Nerode. | O(\|Q\|^2 * \|Sigma\|) |
| `is_minimal` | DFA | Teste si l'automate est déjà minimal. | O(\|Q\|^2 * \|Sigma\|) |
| `minimize` | DFA | DFA minimal équivalent (fusion des états équivalents). | O(\|Q\|^2 * \|Sigma\|) |
| `pair_table` | DFA | Table de distinguabilité complète, avec le numéro de round de marquage. | O(\|Q\|^2 * \|Sigma\|) par round, au plus \|Q\|^2 rounds. |
| `pair_table_str` | DFA | Table de distinguabilité en ASCII (triangle inférieur). | O(\|Q\|^2) après le calcul de ``pair_table``. |
| `print_pair_table` | DFA | Affiche ``pair_table_str`` (avec les numéros de round par défaut). | — |

## `fa.dfa_mixins.prefix`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `is_prefix_closed` | DFA | Teste si le langage est clos par préfixe. | O(\|Q\| + \|E\|) |
| `prefix_closed_sublanguage` | DFA | Plus grand sous-langage préfixe-clos inclus dans L(self). | O(\|Q\| + \|E\|) |

## `fa.dfa_mixins.product`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `intersection` | DFA | Intersection des langages : L(self) ∩ L(other). | O(\|Q1\| * \|Q2\| * \|Sigma\|) |
| `product` | DFA | Produit synchronisé général de deux DFA sur le même alphabet. | O(\|Q1\| * \|Q2\| * \|Sigma\|) |

## `fa.dfa_mixins.residual`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `residual_automaton` | DFA | Automate dont les états sont les résiduels du langage. | O(\|Q\|^2 * \|Sigma\|) |
| `residuals` | DFA | Représentants des classes de Myhill-Nerode. | O(\|Q\|^2 * \|Sigma\|) |

## `fa.dfa_mixins.syntactic_monoid`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `is_star_free` | DFA | Teste si le langage est *sans étoile* (exprimable avec union, | Celle de ``syntactic_monoid`` + ``is_aperiodic``. |
| `syntactic_monoid` | DFA | Monoïde syntaxique du langage = monoïde de transitions du DFA minimal. | O(\|Q\|^2 * \|Sigma\| + \|M\| * \|Sigma\| * \|Q\|) |
| `transition_monoid` | DFA | Monoïde de transitions de ce DFA (complété, états accessibles seulement). | O(\|M\| * \|Sigma\| * \|Q\|), \|M\| = taille du monoïde. |

## `fa.dfa_mixins.union`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `union` | DFA | Union des langages : L(self) ∪ L(other). | O(\|Q1\| * \|Q2\| * \|Sigma\|) |

## `fa.fa_mixins.accessibility`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `accessible_states` | DFA, NFA, GNFA | États atteignables depuis l'état initial. | O(\|Q\| + \|E\|) |
| `coaccessible_states` | DFA, NFA, GNFA | États depuis lesquels un état final est atteignable. | O(\|Q\| + \|E\|) |
| `induced_subautomaton` | DFA, NFA, GNFA | Sous-automate induit par un sous-ensemble d'états. | O(\|Q\| + \|E\|) |
| `is_accessible` | DFA, NFA, GNFA | Teste si ``state`` est accessible depuis l'état initial. | O(\|Q\| + \|E\|) |
| `is_coaccessible` | DFA, NFA, GNFA | Teste si un état final est atteignable depuis ``state``. | O(\|Q\| + \|E\|) |
| `is_trim` | DFA, NFA, GNFA | Teste si tous les états de l'automate sont utiles. | O(\|Q\| + \|E\|) |
| `trim` | DFA, NFA, GNFA | Automate élagué : restriction aux états utiles. | O(\|Q\| + \|E\|) |
| `useful_states` | DFA, NFA, GNFA | États à la fois accessibles et coaccessibles. | O(\|Q\| + \|E\|) |

## `fa.fa_mixins.animation`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `animate` | DFA, NFA, GNFA | Page HTML autonome animant la lecture de ``word``. | O(\|mot\| * \|Q\| * \|E\| + \|Q\| + \|E\|) |

## `fa.fa_mixins.brzozowski`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `brzozowski_minimize` | DFA, NFA, GNFA | DFA minimal équivalent, par l'algorithme de Brzozowski. | O(2^\|Q\|) dans le pire cas (la déterminisation peut exploser), mais se comporte bien en pratique. |

## `fa.fa_mixins.counterexample`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `distinguishing_word` | DFA, NFA, GNFA | Plus court mot sur lequel ``self`` et ``other`` diffèrent (un seul des deux | O(\|Q1\| * \|Q2\| * \|Sigma\|) pour deux DFA. |
| `shortest_word` | DFA, NFA, GNFA | Plus court mot accepté (le plus petit dans l'ordre longueur puis | O(\|Q\| * \|Sigma\|) pour un DFA ; O(2^\|Q\|) dans le pire cas pour un NFA. |

## `fa.fa_mixins.cycle`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `has_cycle` | DFA, NFA, GNFA | Teste l'existence d'un cycle accessible depuis l'état initial. | O(\|Q\| + \|E\|) |
| `has_cycle_from` | DFA, NFA, GNFA | Teste l'existence d'un cycle dans le sous-graphe accessible depuis ``state``. | O(\|Q\| + \|E\|) |
| `is_empty` | DFA, NFA, GNFA | Teste si le langage reconnu est vide. | O(\|Q\| + \|E\|) |
| `is_finite` | DFA, NFA, GNFA | Teste si le langage reconnu est fini. | O(\|Q\| + \|E\|) |

## `fa.fa_mixins.determinism`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `is_deterministic` | DFA, NFA, GNFA | Teste si la fonction de transition est déterministe. | O(\|E\|) |

## `fa.fa_mixins.equations_fa`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `to_equations` | DFA, NFA, GNFA | Système d'équations de langages de l'automate (une inconnue ``X_q`` par état, | O(\|Q\| + \|E\|) |

## `fa.fa_mixins.grammar_fa`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `derivation_tree` | DFA, NFA, GNFA | Dérivation de ``word`` dans la grammaire de l'automate (dernière étape). | O(\|E\| * \|mot\|^2) |
| `to_grammar` | DFA, NFA, GNFA | Grammaire régulière linéaire à droite équivalente. | O(\|Q\| + \|E\|) |
| `to_left_grammar` | DFA, NFA, GNFA | Grammaire régulière linéaire à gauche équivalente. | O(\|Q\| + \|E\|) |

## `fa.fa_mixins.graph`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `predecessors_graph` | DFA, NFA, GNFA | États ayant une transition directe vers ``state``, tout symbole confondu. | O(\|Q\| * \|Sigma\|) : on parcourt toutes les transitions de l'automate. |
| `successors_graph` | DFA, NFA, GNFA | États atteignables en une transition depuis ``state``, tout symbole confondu. | O(\|Sigma\|) pour un DFA, O(somme des tailles des ensembles cibles) pour un NFA. |

## `fa.fa_mixins.language_operations`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `concatenation` | DFA, NFA, GNFA | Concaténation des langages : L(self) . L(other). | O(\|Q1\| + \|Q2\|) |
| `kleene_star` | DFA, NFA, GNFA | Étoile de Kleene de L(self). | O(\|Q\|) |
| `union` | NFA, GNFA | Union des langages : L(self) ∪ L(other), par construction directe. | O(\|Q1\| + \|Q2\|) |

## `fa.fa_mixins.morphism`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `is_morphism_to` | DFA, NFA, GNFA | Teste si ``state_map`` est un morphisme d'automate valide de ``self`` vers ``other``. | O(\|Q\| * \|Sigma\|) |
| `project` | DFA, NFA, GNFA | Relabellise (ou efface, avec ``None``) les symboles d'entrée. | O(\|Q\| * \|Sigma\|) |
| `quotient_by` | DFA, NFA, GNFA | Fusionne des états selon une application donnée. | O(\|Q\| * \|Sigma\|) |

## `fa.fa_mixins.quotient_fa`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `left_quotient_word` | DFA, NFA, GNFA | Quotient à gauche par un mot : ``{u : word·u ∈ L}``. | O(\|mot\| * \|Q\| + \|Q\| + \|E\|) |
| `right_quotient_word` | DFA, NFA, GNFA | Quotient à droite par un mot : ``{u : u·word ∈ L}``. | O(\|Q\| * \|mot\| * \|Q\|) |

## `fa.fa_mixins.regex`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `to_regex` | DFA, NFA, GNFA | Expression régulière dénotant L(self). | O(\|Q\|^3) (élimination d'états, taille des expressions pouvant croître exponentiellement dans le pire cas). |

## `fa.fa_mixins.regex_arden`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `to_regex_arden` | DFA, NFA, GNFA | Expression régulière dénotant L(self), par le lemme d'Arden. | O(\|Q\|^3) dans le pire cas (taille des expressions potentiellement exponentielle). |

## `fa.fa_mixins.regex_optimum`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `to_regex_arden_optimum` | DFA, NFA, GNFA | Comme ``to_regex_optimum``, mais par résolution d'Arden (ordre d'élimination variable). | O(k * \|Q\|^3) |
| `to_regex_optimum` | DFA, NFA, GNFA | Expression régulière courte, par élimination d'états avec essai de plusieurs ordres. | O(k * \|Q\|^3) pour k ordres essayés (k = \|Q\|! si \|Q\| <= max_exhaustive). |

## `fa.fa_mixins.reverse`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `reverse` | DFA, NFA, GNFA | Automate (NFA) du langage miroir de L(self). | O(\|Q\| + \|E\|) |

## `fa.fa_mixins.scc`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `is_strongly_connected` | DFA, NFA, GNFA | Vrai si tous les états sont mutuellement atteignables (une seule composante). | O(\|Q\| + \|E\|) |
| `strongly_connected_components` | DFA, NFA, GNFA | Composantes fortement connexes de *tout* le graphe de transition (états | O(\|Q\| + \|E\|) |

## `fa.fa_mixins.traversal`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `bfs` | DFA, NFA, GNFA | Parcours en largeur depuis ``start`` (état initial par défaut). | O(\|Q\| + \|E\|) |
| `dfs` | DFA, NFA, GNFA | Parcours en profondeur depuis ``start`` (état initial par défaut). | O(\|Q\| + \|E\|) |
| `reachable_states` | DFA, NFA, GNFA | États atteignables depuis ``start`` (état initial par défaut). | O(\|Q\| + \|E\|) |

## `fa.fa_mixins.visualisation`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `dot` | DFA, NFA, GNFA | Source DOT (Graphviz) de l'automate, en texte pur. | O(\|Q\| log \|Q\| + \|E\|) |
| `graph` | DFA, NFA, GNFA | Objet ``graphviz.Digraph`` de l'automate (s'affiche tel quel dans Jupyter). | — |
| `latex` | DFA, NFA, GNFA | Document LaTeX autonome (classe ``standalone``) contenant le TikZ de l'automate. | O(\|Q\| log \|Q\| + \|E\|) |
| `pdf` | DFA, NFA, GNFA | Rendu PDF (octets). Nécessite le binaire ``dot``. | — |
| `png` | DFA, NFA, GNFA | Rendu PNG (octets). Nécessite le binaire ``dot``. | — |
| `save` | DFA, NFA, GNFA | Écrit l'automate dans un fichier ; le format est déduit de l'extension : | — |
| `svg` | DFA, NFA, GNFA | Rendu SVG (texte). Nécessite le binaire ``dot``. | — |
| `tikz` | DFA, NFA, GNFA | Code TikZ (bibliothèque ``automata``) de l'automate. | O(\|Q\| log \|Q\| + \|E\|) |

## `fa.fa_mixins.word`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `accepts` | DFA, NFA, GNFA | Alias pédagogique de ``accepts_input``. | O(\|mot\|) pour un DFA ; O(\|mot\| * \|Q\|^2) pour un NFA. |
| `run` | DFA, NFA, GNFA | Exécution de ``word`` sous forme de texte, ex. ``0 → 1 → 2 → 0 → accept``. | Celle de ``execution_trace``. |

## `fa.gnfa_mixins.elimination`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `eliminate_state` | GNFA | GNFA équivalent sans l'état ``state`` (un pas de la méthode d'élimination). | O(\|Q\|^2) opérations sur des expressions régulières. |
| `eliminate_states` | GNFA | Élimine tous les états intermédiaires ; il reste le GNFA à deux états dont la | O(\|Q\|^3) opérations sur des expressions (tailles potentiellement exponentielles). |

## `fa.nfa_mixins.determinization`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `determinize` | NFA | Construction des sous-ensembles : DFA équivalent au NFA. | O(2^\|Q\| * \|Sigma\|) dans le pire cas. |
| `to_dfa` | NFA | Alias de ``determinize``. | O(2^\|Q\| * \|Sigma\|) |

## `fa.nfa_mixins.elimination`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `eliminate_lambda` | NFA | Alias de ``remove_epsilon_transitions`` : surcharge ``NFA.eliminate_lambda`` | O(\|Q\|^2 * \|Sigma\|) |
| `remove_epsilon_transitions` | NFA | Propage les transitions au travers des fermetures epsilon. | O(\|Q\|^2 * \|Sigma\|) |

## `fa.nfa_mixins.epsilon`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `epsilon_closure` | NFA | Fermeture epsilon d'un seul état. | O(\|Q\| + \|E\|) |
| `epsilon_closure_of_set` | NFA | Fermeture epsilon d'un ensemble d'états. | O(\|Q\| + \|E\|) |

## `fa.nfa_mixins.execution`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `execution_trace` | NFA | Trace de la lecture de ``word`` : ensembles d'états actifs. | O(\|mot\| * \|Q\| * \|E\|) |

## `fa.nfa_mixins.grammar_nfa`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `from_grammar` | NFA | NFA reconnaissant le langage d'une grammaire régulière (à droite ou à gauche). | O(\|P\| * longueur maximale d'un membre droit) |
| `from_grammar_string` | NFA | NFA d'une grammaire écrite en texte, ex. ``"S -> aS \| b"`` | O(taille du texte) |

## `fa.nfa_mixins.thompson`

| Méthode | Disponible sur | Résumé | Complexité |
|---|---|---|---|
| `from_regex` | NFA | NFA de Thompson reconnaissant le langage de ``regex``. | O(n) états et transitions. |

## Autres classes

### `Grammar`

| Méthode | Résumé | Complexité |
|---|---|---|
| `derive` | Une dérivation la plus courte de ``word``, sous forme d'une chaîne de formes | O(\|P\| * \|mot\|^2) dans le pire cas. |
| `from_string` | Lit une grammaire au format classique, une ligne par non-terminal :: | O(taille du texte) |
| `generates` | Teste si ``word`` appartient au langage (grammaires régulières seulement). | — |
| `is_left_linear` | Toute règle est ``A -> B w`` ou ``A -> w``. | — |
| `is_regular` | Linéaire à droite *ou* à gauche (pas un mélange des deux). | — |
| `is_right_linear` | Toute règle est ``A -> w B`` ou ``A -> w`` (w terminal, B non-terminal). | — |
| `reverse` | Grammaire du langage miroir : chaque membre droit est renversé. | — |
| `rules_for` | Règles de ``nonterminal``, triées (la règle ε en dernier). | — |
| `to_nfa` | NFA (avec ε-transitions) reconnaissant le langage de la grammaire. | O(\|P\| * longueur maximale d'un membre droit) |

### `DerivationStep`

| Méthode | Résumé | Complexité |
|---|---|---|
| `is_complete` | Vrai si la forme ne contient plus de non-terminal. | — |
| `parse_tree` | Arbre de dérivation correspondant (dérivation la plus à gauche). | — |
| `rules` | Règles appliquées, dans l'ordre. | — |
| `sequence` | Suite des formes sentencielles, ex. ``S => aS => aaS => aab``. | — |
| `steps` | Toutes les étapes, de l'axiome jusqu'à celle-ci. | — |
| `word` | Mot dérivé (la forme doit être terminale). | — |

### `ParseTree`

| Méthode | Résumé | Complexité |
|---|---|---|
| `depth` | Hauteur de l'arbre (une feuille seule : 0). | — |
| `leaves` | Feuilles de gauche à droite (symboles, ε compris). | — |
| `to_dot` | Description Graphviz de l'arbre. | — |
| `word` | Mot lu sur les feuilles (ε ignoré). | — |

### `Regex`

| Méthode | Résumé | Complexité |
|---|---|---|
| `derivative` | Dérivée de Brzozowski par ``symbol`` : quotient à gauche a^{-1}L. | O(taille de l'expression) par appel (plus le coût de normalisation). |
| `firstpos` | Positions pouvant commencer un mot du langage (Glushkov). | — |
| `followpos` | Pour chaque position i, positions pouvant suivre immédiatement i. | — |
| `lastpos` | Positions pouvant terminer un mot du langage (Glushkov). | — |
| `nullable` | Teste si ε appartient au langage dénoté. | O(taille de l'expression) |
| `positions` | Numérotation (à partir de 1) des occurrences de symboles, de gauche à droite. | — |
| `simplify` | Forme normale : applique les constructeurs intelligents de bas en haut. | O(taille * log taille) |
| `size` | Nombre de nœuds de l'arbre. | — |
| `symbols` | Ensemble des symboles apparaissant dans l'expression. | — |
| `to_dfa` | DFA complet équivalent, par l'automate des dérivées de Brzozowski. | O(n * \|Sigma\|) dérivées, n = nombre de dérivées distinctes (fini). |
| `to_glushkov_nfa` | NFA de Glushkov (sans ε-transition) : états 0 (initial) et 1..n (positions). | O(n^2) dans le pire cas (taille de followpos). |
| `to_nfa` | NFA de Thompson équivalent (voir ``ThompsonMixin.from_regex``). | — |

### `EquationSystem`

| Méthode | Résumé | Complexité |
|---|---|---|
| `from_automaton` | Système associé à un DFA/NFA : une inconnue par état, ``X_q = Σ a·X_q' \| ε`` | O(\|Q\| + \|E\|) |
| `solve` | Résout le système : une expression régulière pour *chaque* inconnue. | O(n^3) opérations sur des expressions (la taille des expressions peut croître exponentiellement dans le pire cas). |

### `TransitionMonoid`

| Méthode | Résumé | Complexité |
|---|---|---|
| `element_of` | Transformation induite par ``word``. | — |
| `from_dfa_table` | Construit le monoïde par parcours en largeur depuis l'identité. | O(\|M\| * \|Sigma\| * \|Q\|) où \|M\| est la taille du monoïde (qui peut atteindre \|Q\|^\|Q\| dans le pire cas). |
| `idempotents` | Éléments ``e`` tels que ``e e = e``, par plus court mot croissant. | — |
| `identity` | Transformation identité (mot vide). | — |
| `is_aperiodic` | Vrai si pour tout ``x`` il existe ``m`` avec ``x^m = x^(m+1)`` | O(\|M\| * \|M\| * \|Q\|) dans le pire cas. |
| `is_commutative` | Vrai si ``fg = gf`` pour tous éléments. Il suffit de le vérifier sur | O(\|Sigma\|^2 * \|Q\|) |
| `is_group` | Vrai si tous les éléments sont des permutations (le monoïde est un groupe). | — |
| `multiply` | Composition « f puis g ». | — |
| `shortest_word` | Plus court mot induisant ``element``. | — |

### `Exercise`

| Méthode | Résumé | Complexité |
|---|---|---|
| `check` | Vrai si la réponse est correcte (voir ``feedback``). | — |
| `feedback` | Correction commentée. | — |

