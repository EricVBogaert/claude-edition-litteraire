#!/bin/bash

# Script pour exécuter les tests du module LLM
echo "===== Exécution des tests du module LLM ====="

# 1. S'assurer que les dépendances sont installées
echo "Vérification des dépendances de test..."
pip install -q pytest pytest-cov

# 2. Appliquer les corrections de dépendances circulaires si nécessaire
echo "Application des corrections de dépendances circulaires..."
./fix_circular_imports.sh

# 3. Exécuter les tests unitaires
echo -e "\nExécution des tests unitaires..."
pytest tests/test_llm -v

# 4. Exécuter les tests fonctionnels
echo -e "\nExécution des tests fonctionnels..."
pytest tests/functional/test_llm_integration.py -v

# 5. Générer un rapport de couverture
echo -e "\nGénération du rapport de couverture..."
pytest --cov=claude_edition_litteraire.llm tests/

echo -e "\n===== Tests terminés ====="
