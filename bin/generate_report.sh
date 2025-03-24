#!/bin/bash

OUTPUT_FILE="project_structure_report.md"

echo "# Rapport de structure du projet Claude Édition Littéraire" > $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Fonction pour analyser les modules importants
analyze_module() {
    local module_path=$1
    local module_name=$2
    
    echo "## Module $module_name" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    
    # Fichiers Python dans ce module
    echo "### Fichiers sources" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    echo "| Fichier | Taille | Dernière modification |" >> $OUTPUT_FILE
    echo "|---------|--------|----------------------|" >> $OUTPUT_FILE
    
    find "$module_path" -name "*.py" -type f | sort | while read -r file; do
        file_name=$(basename "$file")
        file_size=$(du -h "$file" | cut -f1)
        last_modified=$(stat -c %y "$file" | cut -d '.' -f1)
        
        echo "| $file_name | $file_size | $last_modified |" >> $OUTPUT_FILE
    done
    
    echo "" >> $OUTPUT_FILE
    
    # Structure de sous-répertoires si présente
    if [ -n "$(find "$module_path" -mindepth 1 -type d)" ]; then
        echo "### Sous-modules" >> $OUTPUT_FILE
        echo "" >> $OUTPUT_FILE
        
        find "$module_path" -mindepth 1 -type d | sort | while read -r subdir; do
            subdir_name=$(basename "$subdir")
            echo "- $subdir_name" >> $OUTPUT_FILE
        done
        
        echo "" >> $OUTPUT_FILE
    fi
}

# Section principale sur claude-edition-litteraire
echo "# 1. Bibliothèque claude-edition-litteraire" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "C'est le projet principal contenant la bibliothèque Python qui implémente les fonctionnalités d'édition littéraire assistée par Claude." >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Analyser les modules principaux
if [ -d "claude_edition_litteraire/llm" ]; then
    analyze_module "claude_edition_litteraire/llm" "LLM"
fi

if [ -d "claude_edition_litteraire/structure" ]; then
    analyze_module "claude_edition_litteraire/structure" "Structure"
fi

if [ -d "claude_edition_litteraire/content" ]; then
    analyze_module "claude_edition_litteraire/content" "Content"
fi

if [ -d "claude_edition_litteraire/utils" ]; then
    analyze_module "claude_edition_litteraire/utils" "Utils"
fi

# Tests
if [ -d "tests" ]; then
    echo "## Tests" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    echo "| Suite de tests | Nombre de fichiers | Statut |" >> $OUTPUT_FILE
    echo "|---------------|-------------------|--------|" >> $OUTPUT_FILE
    
    # Compter les tests par module
    if [ -d "tests/test_llm" ]; then
        test_count=$(find "tests/test_llm" -name "test_*.py" | wc -l)
        echo "| LLM | $test_count | ✅ |" >> $OUTPUT_FILE
    fi
    
    if [ -d "tests/functional" ]; then
        test_count=$(find "tests/functional" -name "test_*.py" | wc -l)
        echo "| Fonctionnels | $test_count | ✅ |" >> $OUTPUT_FILE
    fi
    
    echo "" >> $OUTPUT_FILE
fi

# Scripts d'automatisation
echo "## Scripts d'automatisation" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "| Script | Description |" >> $OUTPUT_FILE
echo "|--------|-------------|" >> $OUTPUT_FILE

if [ -f "run_llm_tests.sh" ]; then
    echo "| run_llm_tests.sh | Exécution des tests du module LLM |" >> $OUTPUT_FILE
fi

if [ -f "fix_circular_imports.sh" ]; then
    echo "| fix_circular_imports.sh | Correction des imports circulaires |" >> $OUTPUT_FILE
fi

if [ -f "test_claude_models.py" ]; then
    echo "| test_claude_models.py | Test des différents modèles Claude |" >> $OUTPUT_FILE
fi

if [ -d "bin" ]; then
    find "bin" -type f -name "*.sh" | sort | while read -r script; do
        script_name=$(basename "$script")
        echo "| $script_name | $(head -n 3 "$script" | grep -i "description" || echo "Script d'automatisation") |" >> $OUTPUT_FILE
    done
fi

echo "" >> $OUTPUT_FILE

# Section sur edition-litteraire-claude-ai
echo "# 2. Documentation et structure edition-litteraire-claude-ai" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "Ce dépôt contient la documentation et les templates pour créer des projets littéraires." >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Analyser la structure du guide
if [ -d "../edition-litteraire-claude-ai/docs" ]; then
    echo "## Guides et documentation" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    echo "| Document | Taille |" >> $OUTPUT_FILE
    echo "|----------|--------|" >> $OUTPUT_FILE
    
    find "../edition-litteraire-claude-ai/docs" -name "*.md" -type f | sort | while read -r file; do
        file_name=$(basename "$file")
        file_size=$(du -h "$file" | cut -f1)
        
        echo "| $file_name | $file_size |" >> $OUTPUT_FILE
    done
    
    echo "" >> $OUTPUT_FILE
fi

# Section sur datura-projet-normalite
echo "# 3. Exemple d'application: datura-projet-normalite" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "Ce dépôt est un exemple d'application du framework d'édition littéraire pour un projet concret." >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Statistiques des chapitres
if [ -d "../datura-projet-normalite/chapitres" ]; then
    echo "## Statistiques du projet" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    
    chapter_count=$(find "../datura-projet-normalite/chapitres" -name "*.md" -type f | wc -l)
    total_size=$(du -sh "../datura-projet-normalite/chapitres" | cut -f1)
    
    echo "- Nombre de chapitres: $chapter_count" >> $OUTPUT_FILE
    echo "- Taille totale: $total_size" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
fi

echo "Rapport généré avec succès: $OUTPUT_FILE"
