#!/bin/bash
# apply-and-test-fixes.sh
# Script pour appliquer les corrections d'imports circulaires et tester la solution

echo "🔄 Application des corrections et tests pour les imports circulaires..."

# Vérifier que nous sommes dans le répertoire du projet
if [[ ! -d "claude_edition_litteraire" ]]; then
    echo "❌ Erreur: Vous devez exécuter ce script depuis la racine du projet."
    exit 1
fi

# Sauvegarder l'état actuel du projet
echo "📦 Création d'une sauvegarde du projet..."
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="../claude_edition_litteraire_backup_$timestamp"
mkdir -p "$backup_dir"
cp -r . "$backup_dir"
echo "✅ Sauvegarde créée: $backup_dir"

# 1. Appliquer les corrections de structure avec les interfaces
echo "🔧 Application des corrections de structure..."
chmod +x ./fix-common-imports.sh
./fix-common-imports.sh

# 2. Exécuter les tests pour vérifier les imports circulaires
echo "🧪 Exécution des tests d'imports circulaires..."
chmod +x ./test-circular-imports.sh
./test-circular-imports.sh

# 3. Vérifier que les tests du projet passent toujours
echo "🧪 Exécution des tests unitaires du projet..."

# Créer un environnement virtuel
python3 -m venv .venv_project_tests
source .venv_project_tests/bin/activate

# Installer les dépendances
pip install pytest pytest-cov > /dev/null 2>&1
pip install -e . > /dev/null 2>&1

# Exécuter les tests
pytest tests/test_llm

# Sortir de l'environnement virtuel
deactivate

# Nettoyage
rm -rf .venv_project_tests

# Vérifier si des erreurs d'imports existent encore
echo "🔍 Recherche d'éventuels imports circulaires restants..."
chmod +x ./find-circular-imports.sh
./find-circular-imports.sh

echo "📝 Rapport final:"
echo "1. Vérifiez les alertes et erreurs éventuelles ci-dessus."
echo "2. Les modifications apportées aux interfaces devraient permettre de résoudre les imports circulaires."
echo "3. Si des problèmes persistent, vérifiez le rapport détaillé dans import_cycles_report.md."
echo "4. La sauvegarde du projet est disponible dans: $backup_dir"

echo "✅ Processus terminé!"
