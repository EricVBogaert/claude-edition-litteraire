#!/bin/bash
# Un script très simple utilisant des commandes Unix de base

# Créer une sauvegarde
cp STATUS.md STATUS.md.bak
echo "✅ Sauvegarde créée: STATUS.md.bak"

# Trouve la ligne où se trouve "## Notes et recommandations"
NOTES_LINE=$(grep -n "^## Notes et recommandations" STATUS.md | cut -d: -f1)

if [ -n "$NOTES_LINE" ]; then
    # Si nous avons trouvé la section, divisez le fichier
    head -n $((NOTES_LINE-1)) STATUS.md > part1.txt
    tail -n +$NOTES_LINE STATUS.md > part2.txt

    # Écrire la première partie, puis notre section, puis la seconde partie
    cat part1.txt > STATUS.md
    echo "## Amélioration du workflow développeur" >> STATUS.md
    echo "" >> STATUS.md
    echo "Le développement du module a été grandement facilité par l'utilisation de Git pour la gestion de versions et d'artefacts bash pour les modifications en lot." >> STATUS.md
    echo "Cette approche, dans la philosophie Unix avec utilisation de diff/sed/patch, s'est révélée très efficace." >> STATUS.md
    echo "" >> STATUS.md
    cat part2.txt >> STATUS.md

    # Nettoyer
    rm part1.txt part2.txt
else
    # Sinon, ajouter simplement à la fin
    echo "" >> STATUS.md
    echo "## Amélioration du workflow développeur" >> STATUS.md
    echo "" >> STATUS.md
    echo "Le développement du module a été grandement facilité par l'utilisation de Git pour la gestion de versions et d'artefacts bash pour les modifications en lot." >> STATUS.md
    echo "Cette approche, dans la philosophie Unix avec utilisation de diff/sed/patch, s'est révélée très efficace." >> STATUS.md
fi

echo "✅ Mise à jour terminée"
