# Environnement de Développement

Cette section décrit l'environnement de développement recommandé pour ce projet, avec les configurations et outils nécessaires pour maintenir la cohérence entre les différents contributeurs et environnements de travail.

## Configuration Requise

### Outils principaux
- **Git** - Gestion de versions et collaboration
- **VS Code** - Éditeur principal avec extensions spécifiques
- **Node.js** - Version LTS recommandée (≥ 18.x)
- **WSL** (Windows Subsystem for Linux) - Pour les utilisateurs Windows

### Extensions VS Code essentielles

Nous utilisons différents profils VS Code selon les types de tâches :

#### Profil "Développement Principal"
- `eamodio.gitlens` - Intégration Git avancée
- `mhutchie.git-graph` - Visualisation graphique de l'historique Git
- `esbenp.prettier-vscode` - Formatage de code
- `dbaeumer.vscode-eslint` - Linting JavaScript/TypeScript
- `usernamehw.errorlens` - Affichage amélioré des erreurs

#### Profil "Rédaction"
- `yzhang.markdown-all-in-one` - Support Markdown avancé
- `shd101wyy.markdown-preview-enhanced` - Prévisualisation Markdown
- `mushan.vscode-paste-image` - Insertion d'images dans Markdown
- `streetsidesoftware.code-spell-checker` - Vérification orthographique

#### Profil "CSS/Design"
- `bradlc.vscode-tailwindcss` - Support Tailwind CSS
- `mrmlnc.vscode-csscomb` - Organisation du CSS
- `naumovs.color-highlight` - Visualisation des couleurs

## Installation de l'environnement

Pour garantir une configuration cohérente, nous fournissons des scripts d'automatisation dans le dossier `tools/` :

### Script d'analyse d'environnement

Le script `environment-profiler.sh` génère un rapport complet de votre environnement actuel :

```bash
# Télécharger le script
curl -o environment-profiler.sh https://raw.githubusercontent.com/votre-org/votre-repo/main/tools/environment-profiler.sh

# Rendre exécutable et lancer
chmod +x environment-profiler.sh
./environment-profiler.sh
```

Ce rapport est utile pour :
- Partager votre configuration avec l'équipe
- Diagnostiquer les problèmes d'environnement
- Documenter votre setup pour référence future

### Script de configuration automatique

Le script `environment-setup.sh` configure automatiquement un nouvel environnement :

```bash
# Télécharger le script
curl -o environment-setup.sh https://raw.githubusercontent.com/votre-org/votre-repo/main/tools/environment-setup.sh

# Rendre exécutable et lancer
chmod +x environment-setup.sh
./environment-setup.sh
```

Ce script :
- Configure les alias shell utiles
- Installe et configure les profils VS Code recommandés
- Met en place un client CLI pour Claude
- Définit les variables d'environnement nécessaires

## Utilisation de Claude API en ligne de commande

Pour les utilisateurs de WSL, nous recommandons l'utilisation de notre script `claude-api` pour intégrer Claude dans les workflows CLI :

```bash
# Exemple d'utilisation simple
claude-api "Explique ce que fait cette fonction JavaScript: function add(a, b) { return a + b; }"

# Utilisation avec input/output
cat README.md | claude-api "Résume ce document" > resume.md

# Analyse de code
claude-api < code.js "Identifie les problèmes potentiels dans ce code"
```

Pour configurer `claude-api`, suivez les étapes dans `environment-setup.sh`.

## Profils VS Code recommandés

Pour changer de profil VS Code :
1. Cliquez sur le nom de profil dans la barre d'état (coin inférieur gauche)
2. Sélectionnez le profil approprié
3. Ou utilisez les alias configurés :
   - `py-profile` - Pour le développement Python
   - `react-profile` - Pour le développement React
   - `writing-profile` - Pour la rédaction
   - `css-profile` - Pour le design CSS

## Conventions Git

### Branches

- `main` - Code de production stable
- `dev` - Développement principal
- `feature/nom-de-la-fonctionnalité` - Nouvelles fonctionnalités
- `fix/description-du-bug` - Corrections de bugs

### Messages de commit

Format: `type(scope): description concise`

Types courants :
- `feat` - Nouvelle fonctionnalité
- `fix` - Correction de bug
- `docs` - Documentation
- `style` - Formatage, pas de changement de code
- `refactor` - Restructuration du code

Exemple : `feat(auth): ajouter validation du token JWT`

## Ressources supplémentaires

- [Documentation officielle de VS Code](https://code.visualstudio.com/docs)
- [Guide Git](https://git-scm.com/book/fr/v2)
- [Documentation WSL](https://docs.microsoft.com/fr-fr/windows/wsl/)

## Aide et dépannage

Si vous rencontrez des problèmes avec votre environnement :

1. Exécutez le script `environment-profiler.sh` et partagez le rapport
2. Vérifiez que vos versions correspondent aux recommandations
3. Consultez les journaux de l'application dans `logs/`
4. Demandez de l'aide sur notre canal Slack #env-support
