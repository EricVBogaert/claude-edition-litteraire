#!/bin/bash
# easy_commit.sh - Simplifie le processus de commit Git

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Afficher l'état actuel
echo -e "${YELLOW}État actuel du dépôt:${NC}"
git status -s

# Demander quoi ajouter
echo -e "\n${YELLOW}Que souhaitez-vous ajouter au commit?${NC}"
echo "1) Seulement les fichiers modifiés (déjà suivis)"
echo "2) Tous les fichiers (modifiés et nouveaux)"
echo "3) Sélection personnalisée"
read -p "Choix [1-3]: " choice

case $choice in
    1)
        # Ajouter seulement les fichiers modifiés
        git add -u
        ;;
    2)
        # Ajouter tous les fichiers
        git add .
        ;;
    3)
        # Sélection personnalisée
        echo -e "\n${YELLOW}Fichiers disponibles:${NC}"
        git status -s
        echo ""
        read -p "Entrez les patterns à ajouter (ex: *.py claude_edition_litteraire/llm/): " patterns
        for pattern in $patterns; do
            git add $pattern
        done
        ;;
    *)
        echo "Choix non valide"
        exit 1
        ;;
esac

# Afficher ce qui va être commité
echo -e "\n${YELLOW}Modifications qui seront commitées:${NC}"
git diff --cached --stat

# Demander un message de commit
read -p "Message de commit: " commit_message

# Effectuer le commit
git commit -m "$commit_message"

# Demander si on pousse les changements
read -p "Pousser les changements sur GitHub? [y/N] " push_choice
if [[ $push_choice =~ ^[Yy] ]]; then
    git push
    echo -e "\n${GREEN}Changements poussés avec succès!${NC}"
else
    echo -e "\n${GREEN}Commit effectué localement. Utilisez 'git push' quand vous serez prêt.${NC}"
fi
