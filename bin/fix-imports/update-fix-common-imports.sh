#!/bin/bash
# update-fix-common-imports.sh
# Script pour corriger fix-common-imports.sh afin de préserver LLMProvider

echo "🔧 Mise à jour du script fix-common-imports.sh..."

# Vérifier que le script existe
SCRIPT_FILE="bin/fix-imports/fix-common-imports.sh"
if [ ! -f "$SCRIPT_FILE" ]; then
    echo "❌ Erreur: Le script $SCRIPT_FILE n'existe pas."
    exit 1
fi

# Créer une sauvegarde du fichier original
cp "$SCRIPT_FILE" "${SCRIPT_FILE}.bak_$(date +%Y%m%d%H%M%S)"
echo "✅ Sauvegarde créée: ${SCRIPT_FILE}.bak_$(date +%Y%m%d%H%M%S)"

# Générer un patch temporaire
cat > /tmp/fix-common-imports.patch << 'EOF'
--- fix-common-imports.sh.old	2025-03-24 12:00:00
+++ fix-common-imports.sh.new	2025-03-24 12:00:00
@@ -155,10 +155,12 @@
 if [[ -f "claude_edition_litteraire/llm/provider.py" ]]; then
     echo "🔄 Modification de provider.py pour utiliser l'interface..."
     cp "claude_edition_litteraire/llm/provider.py" "claude_edition_litteraire/llm/provider.py.bak"
-    
-    sed -i '1,/^from abc import ABC, abstractmethod$/d' "claude_edition_litteraire/llm/provider.py"
-    sed -i '1i"""Interface abstraite pour les fournisseurs de LLM."""\n\nfrom ..interfaces.llm_interface import LLMProviderInterface' "claude_edition_litteraire/llm/provider.py"
-    sed -i 's/class LLMProvider(ABC):/class LLMProvider(LLMProviderInterface):/' "claude_edition_litteraire/llm/provider.py"
+
+    # Ajouter l'import de l'interface au début du fichier
+    sed -i '1i"""Interface abstraite pour les fournisseurs de LLM."""' "claude_edition_litteraire/llm/provider.py"
+    sed -i '2i\nfrom ..interfaces.llm_interface import LLMProviderInterface' "claude_edition_litteraire/llm/provider.py"
+    # Modifier l'héritage pour inclure l'interface
+    sed -i 's/class LLMProvider(ABC):/class LLMProvider(LLMProviderInterface, ABC):/' "claude_edition_litteraire/llm/provider.py"
 fi
 
 # 6. Créer init.py pour le module interfaces
EOF

# Appliquer le patch
patch -p0 "$SCRIPT_FILE" < /tmp/fix-common-imports.patch && {
    echo "✅ Le script fix-common-imports.sh a été mis à jour avec succès."
    rm /tmp/fix-common-imports.patch
} || {
    echo "❌ Erreur lors de l'application du patch."
    echo "⚠️ Essayons une autre approche avec sed..."
    
    # Restaurer la sauvegarde
    LATEST_BACKUP=$(ls -t "${SCRIPT_FILE}.bak_"* | head -1)
    cp "$LATEST_BACKUP" "$SCRIPT_FILE"
    
    # Extraire la section concernée
    SECTION_START=$(grep -n "# 5. Modifier le fichier provider.py pour utiliser l'interface" "$SCRIPT_FILE" | cut -d: -f1)
    SECTION_END=$(grep -n "# 6. Créer init.py pour le module interfaces" "$SCRIPT_FILE" | cut -d: -f1)
    SECTION_END=$((SECTION_END - 1))
    
    # Préparer le nouveau contenu
    read -r -d '' NEW_SECTION << 'EOF'
# 5. Modifier le fichier provider.py pour utiliser l'interface
if [[ -f "claude_edition_litteraire/llm/provider.py" ]]; then
    echo "🔄 Modification de provider.py pour utiliser l'interface..."
    cp "claude_edition_litteraire/llm/provider.py" "claude_edition_litteraire/llm/provider.py.bak"
    
    # Ajouter l'import de l'interface au début du fichier
    sed -i '1i"""Interface abstraite pour les fournisseurs de LLM."""' "claude_edition_litteraire/llm/provider.py"
    sed -i '2i\nfrom ..interfaces.llm_interface import LLMProviderInterface' "claude_edition_litteraire/llm/provider.py"
    # Modifier l'héritage pour inclure l'interface
    sed -i 's/class LLMProvider(ABC):/class LLMProvider(LLMProviderInterface, ABC):/' "claude_edition_litteraire/llm/provider.py"
fi
EOF
    
    # Remplacer la section
    sed -i "${SECTION_START},${SECTION_END}c\\${NEW_SECTION}" "$SCRIPT_FILE"
    
    echo "✅ Le script fix-common-imports.sh a été mis à jour avec l'approche sed."
}

echo "📝 Pour annuler cette modification: cp ${SCRIPT_FILE}.bak_* $SCRIPT_FILE"
