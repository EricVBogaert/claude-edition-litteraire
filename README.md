# Claude Édition Littéraire

Bibliothèque Python pour l'édition littéraire assistée par Claude AI.

## À propos

Cette bibliothèque fournit des outils pour gérer un projet d'édition littéraire, avec validation de structure, correction automatique, et intégration avec l'API Claude. Elle implémente les concepts et workflows décrits dans le [Guide d'édition littéraire avec Claude](https://github.com/EricVBogaert/edition-litteraire-claude-ai).

## Fonctionnalités

- **Validation de structure** : Vérification de la hiérarchie des dossiers, fichiers, templates, etc.
- **Correction automatique** : Création de dossiers manquants, correction de liens cassés, etc.
- **Génération de rapports** : Rapports détaillés des problèmes détectés au format Markdown ou HTML
- **Intégration Claude** : Révision de contenu, assistance à l'écriture, etc.
- **Interface CLI** : Commandes simples pour gérer votre projet

<img src="media/branding/logo-centaure.png" alt="Logo Centaure" width="300" height="auto">

## Installation

```bash
pip install claude-edition-litteraire
```

## Architecture et modules

Cette bibliothèque est organisée en modules spécialisés, chacun ayant une responsabilité spécifique dans le processus d'édition littéraire assistée par IA.

### Vue d'ensemble de l'architecture

L'architecture est conçue autour d'une classe centrale `Project` qui orchestre les différents modules spécialisés :

```
claude_edition_litteraire/
├── __init__.py
├── core.py (classe Project principale)
├── llm/ (abstraction pour différents modèles de langage)
├── structure/ (validation et correction de structure)
├── content/ (gestion du contenu littéraire)
├── claude/ (intégration avec l'API Claude)
├── automation/ (tâches d'automatisation pour l'édition)
├── utils/ (utilitaires partagés)
└── cli/ (interface en ligne de commande)
```

### Modules principaux

#### Module LLM (`llm/`)

Ce module fournit une abstraction unifiée pour interagir avec différents fournisseurs de modèles de langage (LLMs).

**Composants clés :**
- `UnifiedLLM` : Interface principale qui gère le dispatching vers les fournisseurs
- `LLMProvider` : Interface abstraite pour tous les fournisseurs LLM
- `ClaudeProvider` : Implémentation spécifique pour Claude
- `LMStudioProvider` : Implémentation pour modèles locaux via LMStudio
- `ContextCompressor` : Gestion et optimisation de contexte de conversation

**Fonctionnement :**
Le module implémente un pattern Adapter/Façade permettant d'utiliser de manière unifiée différents LLMs tout en optimisant les interactions via le `ContextCompressor`.

#### Module Structure (`structure/`)

Ce module gère la validation et correction de la structure d'un projet littéraire.

**Composants clés :**
- `ProjectStructure` : Classe principale pour la gestion de structure
- `validator` : Fonctions de validation (structure, templates, frontmatter)
- `fixer` : Fonctions de correction automatique
- `reporter` : Génération de rapports sur les problèmes détectés

**Fonctionnement :**
Le module valide la structure d'un projet contre un schéma attendu, identifie les problèmes et peut les corriger automatiquement.

#### Module Content (`content/`)

Ce module gère le contenu textuel d'un projet littéraire.

**Composants clés :**
- `ContentManager` : Classe principale pour l'accès et la manipulation du contenu
- Fonctions pour extraire, valider et analyser les contenus (chapitres, personnages, etc.)

**Fonctionnement :**
Permet d'accéder aux différents éléments du projet (chapitres, personnages), d'analyser leurs métadonnées et de valider leur cohérence.

#### Module Claude (`claude/`)

Ce module gère l'intégration spécifique avec l'API Claude d'Anthropic.

**Composants clés :**
- `ClaudeManager` : Gestion principale des interactions avec Claude
- `context` : Optimisation du contexte spécifique à Claude

**Fonctionnement :**
Facilite les interactions avec Claude pour les fonctionnalités d'édition littéraire comme l'analyse de contenu, les suggestions, etc.

#### Module Automation (`automation/`)

Ce module gère les tâches d'automatisation pour l'édition littéraire.

**Composants clés :**
- `AutomationManager` : Gestion des fonctionnalités d'automatisation
- Fonctions d'export dans différents formats

**Fonctionnement :**
Automatise les tâches répétitives liées à l'édition littéraire et permet l'export dans différents formats (PDF, EPUB, etc.).

#### Module Utils (`utils/`)

Ce module fournit des utilitaires partagés par les autres modules.

**Composants clés :**
- `ConfigManager` : Gestion de la configuration du projet
- `logging` : Configuration des journaux d'application
- `dependency_injection` : Système d'injection de dépendances pour résoudre les imports circulaires

**Fonctionnement :**
Fournit des fonctionnalités transversales utilisées par l'ensemble des modules du projet.

#### Module CLI (`cli/`)

Ce module fournit une interface en ligne de commande pour la bibliothèque.

**Composants clés :**
- `main.py` : Point d'entrée CLI avec commandes principales (check, fix, init)

**Fonctionnement :**
Expose les fonctionnalités de la bibliothèque via une interface en ligne de commande intuitive.

### Interfaces et injection de dépendances

Le projet utilise un système d'interfaces abstraites et d'injection de dépendances pour:
- Découpler les modules et éviter les imports circulaires
- Faciliter les tests unitaires via le mocking
- Permettre des implémentations alternatives des composants

La classe centrale `Project` utilise le `ServiceProvider` pour accéder aux différents services sans créer de dépendances circulaires.

## Scripts utilitaires

Le projet inclut plusieurs scripts utilitaires pour faciliter le développement, les tests et la maintenance. Ces scripts sont organisés dans le dossier `bin/`.

### Scripts principaux

| Script | Description |
|--------|-------------|
| `easy_commit.sh` | Simplifie le processus d'ajout, commit et push vers le dépôt distant |
| `generate_report.sh` | Génère un rapport détaillé sur l'état du projet |
| `generate_report-context-token.sh` | Génère un rapport sur l'utilisation des tokens de contexte |
| `llm-tests-venv-script.sh` | Exécute les tests du module LLM dans un environnement virtuel isolé |
| `test_claude_api.sh` | Teste la connexion à l'API Claude |

### Scripts de gestion des imports (`bin/fix-imports/`)

Le sous-dossier `bin/fix-imports/` contient des scripts spécialisés pour la détection et la résolution des problèmes d'imports circulaires.

#### Détection des problèmes

| Script | Description |
|--------|-------------|
| `find-circular-imports.sh` | Détecte les imports circulaires dans le projet |
| `test-circular-imports.sh` | Vérifie si les imports circulaires ont été résolus |

#### Correction des problèmes

| Script | Description |
|--------|-------------|
| `fix-common-imports.sh` | Applique automatiquement les corrections pour les problèmes d'imports courants |
| `fix-imports-utils.sh` | Fournit des utilitaires pour appliquer différentes corrections |
| `update-provider-interface.sh` | Modifie provider.py pour utiliser l'interface sans casser les imports |
| `update-fix-common-imports.sh` | Met à jour le script fix-common-imports.sh pour préserver LLMProvider |

#### Gestion de l'environnement de test

| Script | Description |
|--------|-------------|
| `apply-and-test-fixes.sh` | Applique les corrections et exécute les tests |
| `setup-pytest-di.sh` | Configure pytest avec l'injection de dépendances |

### Exemples d'utilisation

#### Workflow de développement quotidien

```bash
# Après modifications du code, exécuter les tests
python -m pytest

# Commit et push des changements
./bin/easy_commit.sh "Description des modifications"
```

#### Résolution des problèmes d'imports circulaires

```bash
# Étape 1: Identifier les imports circulaires
./bin/fix-imports/find-circular-imports.sh

# Étape 2: Appliquer les corrections automatiquement
./bin/fix-imports/fix-common-imports.sh

# Étape 3: Vérifier que les problèmes sont résolus
./bin/fix-imports/test-circular-imports.sh
```

#### Tests d'intégration avec l'API Claude

```bash
# Vérifier la connexion à l'API Claude
./bin/test_claude_api.sh

# Exécuter les tests du module LLM dans un environnement virtuel isolé
./bin/llm-tests-venv-script.sh
```

## Contribution

Les contributeurs sont invités à suivre les standards de codage documentés dans `CLAUDE.md`. Pour plus d'informations sur la structure du projet et les workflows de développement, consultez le fichier `STATUS.md`.
