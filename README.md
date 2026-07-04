# Vérificateur Empirique de Triplets de Hoare `{P} C {Q}`

Ce projet est un **Vérificateur de Triplets de Hoare** basé sur des tests dynamiques aléatoires (évaluation empirique). Il permet de valider le comportement d'un programme impératif simple vis-à-vis d'une précondition $P$ et d'une postcondition $Q$.

Contrairement à un prouveur formel de théorèmes (qui utilise le calcul de WP ou la logique des règles de Hoare), cet outil évalue la validité logique du triplet en générant des centaines d'états de variables aléatoires et limites, en exécutant le programme et en vérifiant si la postcondition est toujours satisfaite à la fin.

---

## Table des Matières
1. [Architecture du Projet](#architecture-du-projet)
2. [Syntaxe et Grammaire Supportées](#syntaxe-et-grammaire-supportées)
3. [Fonctionnement de la Vérification](#fonctionnement-de-la-vérification)
4. [Installation et Lancement](#installation-et-lancement)
5. [Tests et Validation](#tests-et-validation)

---

## Architecture du Projet

Voici l'organisation des répertoires et fichiers du projet :

```text
verficateur du triplet de Hoare/
│
├── app.py                      # Serveur Flask (API /verify et interface web)
├── test_verifier.py            # Suite de tests du backend
│
├── verifier/                   # Package de logique métier
│   ├── __init__.py             # Marqueur de package Python
│   ├── ast.py                  # Structure des nœuds de l'AST (Expressions et Instructions)
│   ├── parser.py               # Analyseur lexical (Lexer) et syntaxique (Parser)
│   ├── evaluator.py            # Évaluateur d'expressions arithmétiques et booléennes
│   ├── interpreter.py          # Interpréteur/Exécuteur d'instructions avec sécurité anti-boucle
│   ├── generator.py            # Générateur aléatoire d'états de variables (x, y, z) et cas limites
│   ├── verifier.py             # Coordinateur global du processus de vérification
│   └── utils.py                # Utilitaires de formatage (temps, états)
│
├── templates/
│   └── index.html              # Interface utilisateur (Dashboard SaaS)
│
└── static/
    ├── css/
    │   └── style.css           # Design responsive et moderne de l'application
    └── js/
        └── app.js              # Client JavaScript pour interagir avec l'API Flask
```

### Rôle de chaque module

*   **[app.py](file:///c:/Users/DELL/Documents/ENS_Master_AI/Master%20S2/logique/version%202.0%20projet%202/app.py)** : Fichier d'entrée de l'application web. Il expose une API HTTP REST sur `/verify` et sert l'interface web.
*   **[verifier/ast.py](file:///c:/Users/DELL/Documents/ENS_Master_AI/Master%20S2/logique/version%202.0%20projet%202/verifier/ast.py)** : Définit l'arbre de syntaxe abstraite (AST). Il sépare proprement les expressions arithmétiques (`Var`, `Num`, `BinOp`), les expressions booléennes (`BoolConst`, `CompareOp`, `AndExpr`, etc.) et les instructions (`AssignStmt`, `IfStmt`, `WhileStmt`, `SkipStmt`, `SeqStmt`).
*   **[verifier/parser.py](file:///c:/Users/DELL/Documents/ENS_Master_AI/Master%20S2/logique/version%202.0%20projet%202/verifier/parser.py)** : Implémente un analyseur lexical (`Lexer`) utilisant des expressions régulières et un analyseur syntaxique descendant récursif (`Parser`) pour transformer les chaînes de texte en AST.
*   **[verifier/evaluator.py](file:///c:/Users/DELL/Documents/ENS_Master_AI/Master%20S2/logique/version%202.0%20projet%202/verifier/evaluator.py)** : Évalue les expressions logiques ou arithmétiques pour un état donné de variables (par exemple, pour savoir si `x > 5` est vrai lorsque `x = 6`).
*   **[verifier/interpreter.py](file:///c:/Users/DELL/Documents/ENS_Master_AI/Master%20S2/logique/version%202.0%20projet%202/verifier/interpreter.py)** : Exécute pas à pas le programme sur un état mémoire. Il intègre un mécanisme de sécurité (`max_steps`) pour interrompre les boucles infinies (ex. `while true do skip end`).
*   **[verifier/generator.py](file:///c:/Users/DELL/Documents/ENS_Master_AI/Master%20S2/logique/version%202.0%20projet%202/verifier/generator.py)** : Génère un ensemble diversifié de scénarios de test. Il combine des valeurs limites (comme `0`, `1`, `-1`, les minimums et maximums de la plage configurée) avec des valeurs aléatoires pour couvrir les cas particuliers.
*   **[verifier/verifier.py](file:///c:/Users/DELL/Documents/ENS_Master_AI/Master%20S2/logique/version%202.0%20projet%202/verifier/verifier.py)** : Le coordinateur qui orchestre la génération d'états, le filtrage via la précondition $P$, l'exécution du programme $C$, et la vérification finale de la postcondition $Q$.

---

## Syntaxe et Grammaire Supportées

Le langage manipulé par l'outil est restreint à trois variables entières : **`x`**, **`y`** et **`z`**.

### 1. Expressions Arithmétiques
*   **Constantes** : entiers relatifs (ex. `42`, `-7`).
*   **Variables** : uniquement `x`, `y` ou `z`.
*   **Opérateurs** : `+`, `-`, `*`, `/` (division entière), `%` (modulo).
*   *Exemples* : `x + 1`, `(y * 2) % z`.

### 2. Expressions Booléennes (Préconditions & Postconditions)
*   **Constantes** : `true`, `false`.
*   **Comparaisons** : `==`, `!=`, `<`, `<=`, `>`, `>=`.
*   **Opérateurs logiques** : `and`, `or`, `not`.
*   *Exemples* : `x >= 0`, `not (x > 5 and y < 10)`, `x == y or z != 0`.

### 3. Instructions (Le Programme)
*   **Affectation** : `variable := expression;` (attention, le point-virgule `;` est requis à la fin de chaque instruction).
*   **Conditionnelle** : `if condition then instruction1 else instruction2 end`
*   **Boucle** : `while condition do instruction end`
*   **Vide** : `skip`
*   **Séquence** : Instructions séparées ou terminées par `;` (ex. `x := 1; y := 2;`).

---

## Fonctionnement de la Vérification

Pour valider le triplet de Hoare `{P} C {Q}` :

1.  **Filtrage par la Précondition** : Seuls les états initiaux dans lesquels la précondition $P$ est évaluée à `true` sont retenus. Les autres sont comptabilisés comme "ignorés".
2.  **Exécution contrôlée** : Si le programme provoque une division par zéro ou dépasse la limite de pas d'exécution (1000 étapes par défaut), le test échoue immédiatement avec une erreur d'exécution.
3.  **Vérification de la Postcondition** : À la fin de l'exécution, on évalue la postcondition $Q$ sur l'état mémoire final. S'il vaut `false`, l'état initial associé est renvoyé à l'utilisateur comme un **contre-exemple**.

---

## Installation et Lancement

### Prérequis
*   Python 3.x installé sur votre machine.
*   Le framework Flask (pour l'interface web).

### Installation
Installez Flask via le gestionnaire de paquets de Python :
```bash
pip install Flask
```

### Lancement de l'application Web
Lancez le serveur Flask :
```bash
python app.py
```
Le serveur sera disponible à l'adresse suivante : [http://localhost:5000](http://localhost:5000).

### Utilisation de l'interface
*   Renseignez la précondition, le programme et la postcondition.
*   Ajustez les paramètres de simulation dans le panneau de contrôle (Nombre de cas de tests à générer, bornes minimale et maximale pour les variables).
*   Cliquez sur **Vérifier le Triplet**.
*   Consultez le résultat : l'application indique si le triplet est **Valide** (aucun échec sur les états satisfaisant la précondition) ou **Invalide**, en listant les contre-exemples avec leurs états initiaux et finaux détaillés.

---

## Tests et Validation

Une suite de tests unitaires est disponible pour s'assurer que la chaîne de traitement (Lexer, Parser, Évaluateur, Interpréteur, Générateur, Vérificateur) fonctionne correctement.

Pour exécuter les tests :
```bash
python test_verifier.py
```

Les tests valident notamment :
*   Le bon parsing des expressions arithmétiques et logiques complexes.
*   L'interruption sécurisée des programmes comportant des boucles infinies.
*   La détection de triplets valides (ex: `{x >= 0} x := x + 1; {x > 0}`) et invalides.
