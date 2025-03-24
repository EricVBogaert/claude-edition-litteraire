#!/bin/bash
# update-provider-interface.sh
# Script pour modifier provider.py afin qu'il utilise l'interface sans casser les imports

echo "🔧 Modification de provider.py pour utiliser l'interface LLMProviderInterface..."

# Vérifier que le fichier provider.py existe
PROVIDER_FILE="claude_edition_litteraire/llm/provider.py"
if [ ! -f "$PROVIDER_FILE" ]; then
    echo "❌ Erreur: Le fichier $PROVIDER_FILE n'existe pas."
    exit 1
fi

# Créer une sauvegarde du fichier original
cp "$PROVIDER_FILE" "${PROVIDER_FILE}.bak_$(date +%Y%m%d%H%M%S)"
echo "✅ Sauvegarde créée: ${PROVIDER_FILE}.bak_$(date +%Y%m%d%H%M%S)"

# 1. D'abord, vérifier si l'interface est déjà importée
if grep -q "from ..interfaces.llm_interface import LLMProviderInterface" "$PROVIDER_FILE"; then
    echo "⚠️ L'interface est déjà importée, aucun changement nécessaire."
else
    # 2. Ajouter l'import de l'interface au début du fichier
    # Trouver la première ligne après le docstring pour y insérer l'import
    DOCSTRING_END=$(grep -n '"""' "$PROVIDER_FILE" | head -2 | tail -1 | cut -d: -f1)
    
    if [ -n "$DOCSTRING_END" ]; then
        # Insérer après la fin du docstring
        sed -i "${DOCSTRING_END}a from ..interfaces.llm_interface import LLMProviderInterface" "$PROVIDER_FILE"
    else
        # Si pas de docstring, insérer au début du fichier
        sed -i '1i from ..interfaces.llm_interface import LLMProviderInterface' "$PROVIDER_FILE"
    fi
    
    echo "✅ Import de l'interface ajouté."
fi

# 3. Modifier la définition de la classe pour hériter de l'interface
if grep -q "class LLMProvider(LLMProviderInterface, ABC):" "$PROVIDER_FILE"; then
    echo "⚠️ La classe hérite déjà de l'interface, aucun changement nécessaire."
elif grep -q "class LLMProvider(ABC):" "$PROVIDER_FILE"; then
    # Remplacer par l'héritage multiple
    sed -i 's/class LLMProvider(ABC):/class LLMProvider(LLMProviderInterface, ABC):/' "$PROVIDER_FILE"
    echo "✅ Héritage modifié pour inclure l'interface LLMProviderInterface."
else
    echo "❌ Erreur: Format de classe LLMProvider inattendu. Vérification manuelle nécessaire."
    # Afficher les premières lignes de définition de classe pour inspection
    grep -A 5 "class LLMProvider" "$PROVIDER_FILE"
    exit 1
fi

# 4. Vérifier que le fichier compile correctement
python3 -c "from claude_edition_litteraire.llm.provider import LLMProvider; print('✅ Vérification réussie: LLMProvider peut être importée.')" || {
    echo "❌ Erreur: La modification a introduit une erreur de compilation."
    echo "🔄 Restauration de la sauvegarde..."
    LATEST_BACKUP=$(ls -t "${PROVIDER_FILE}.bak_"* | head -1)
    cp "$LATEST_BACKUP" "$PROVIDER_FILE"
    echo "✅ Fichier original restauré."
    exit 1
}

echo "✅ provider.py a été modifié avec succès pour utiliser l'interface LLMProviderInterface."
echo "📝 Pour annuler cette modification: cp ${PROVIDER_FILE}.bak_* $PROVIDER_FILE"
