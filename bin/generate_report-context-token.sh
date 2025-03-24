#!/bin/bash

# Chemin vers les dépôts
CLAUDE_EDITION_PATH="claude-edition-litteraire"
EDITION_LITTERAIRE_PATH="edition-litteraire-claude-ai"
DATURA_PATH="datura-projet-normalite"

# Fichier de sortie
OUTPUT_FILE="fichiers_essentiels_tailles.md"

echo "# Tailles des fichiers essentiels pour le Project Knowledge" > $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Fonction pour calculer la taille en tokens approximative
# (estimation grossière: 1 token ~= 4 caractères)
calculate_tokens() {
    local file_path=$1
    if [ -f "$file_path" ]; then
        local chars=$(wc -c < "$file_path")
        local tokens=$(( chars / 4 ))
        echo "$tokens"
    else
        echo "0"
    fi
}

# Fonction pour analyser les fichiers essentiels
analyze_essential_files() {
    local repo_path=$1
    local repo_name=$2
    local files_list=$3
    
    echo "## $repo_name" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    echo "| Fichier | Taille | Tokens (estimés) |" >> $OUTPUT_FILE
    echo "|---------|--------|------------------|" >> $OUTPUT_FILE
    
    total_tokens=0
    
    while IFS= read -r file; do
        if [ -f "$repo_path/$file" ]; then
            file_size=$(du -h "$repo_path/$file" | cut -f1)
            tokens=$(calculate_tokens "$repo_path/$file")
            total_tokens=$((total_tokens + tokens))
            
            echo "| $file | $file_size | ~$tokens |" >> $OUTPUT_FILE
        fi
    done <<< "$files_list"
    
    echo "" >> $OUTPUT_FILE
    echo "Total des tokens estimés: ~$total_tokens" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    
    return $total_tokens
}

# Fichiers essentiels pour chaque dépôt
CLAUDE_EDITION_FILES=$(cat << EOF
STATUS.md
README.md
claude_edition_litteraire/__init__.py
claude_edition_litteraire/core.py
claude_edition_litteraire/llm/__init__.py
claude_edition_litteraire/llm/unified_llm.py
claude_edition_litteraire/llm/provider.py
claude_edition_litteraire/llm/claude_provider.py
claude_edition_litteraire/llm/lmstudio_provider.py
claude_edition_litteraire/llm/context.py
claude_edition_litteraire/structure/__init__.py
claude_edition_litteraire/structure/project_structure.py
claude_edition_litteraire/structure/validator.py
claude_edition_litteraire/utils/config.py
claude_edition_litteraire/utils/logging.py
tests/test_llm/test_unified_llm.py
tests/test_llm/test_context.py
tests/functional/test_llm_integration.py
bin/run_llm_tests.sh
bin/test_claude_api.sh
EOF
)

EDITION_LITTERAIRE_FILES=$(cat << EOF
docs/guide-complet.md
docs/directive-utilisation-claude.md
templates/personnage-avance.md
templates/todo.md
EOF
)

DATURA_FILES=$(cat << EOF
index.md
structure/plan-general.md
EOF
)

# Analyser les dépôts
analyze_essential_files "$CLAUDE_EDITION_PATH" "claude-edition-litteraire" "$CLAUDE_EDITION_FILES"
claude_tokens=$?

analyze_essential_files "$EDITION_LITTERAIRE_PATH" "edition-litteraire-claude-ai" "$EDITION_LITTERAIRE_FILES"
edition_tokens=$?

analyze_essential_files "$DATURA_PATH" "datura-projet-normalite" "$DATURA_FILES"
datura_tokens=$?

# Total global
total_all=$((claude_tokens + edition_tokens + datura_tokens))
echo "# Total global des tokens" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "Total global estimé: ~$total_all tokens" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "Note: La limite de contexte de Claude pour une conversation est d'environ 100 000 tokens." >> $OUTPUT_FILE

echo "Rapport généré avec succès: $OUTPUT_FILE"
