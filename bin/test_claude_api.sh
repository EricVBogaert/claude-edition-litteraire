#!/bin/bash
# test_claude_api.sh - Script pour tester la connexion à l'API Claude

# Vérifier si la variable d'environnement ANTHROPIC_API_KEY est définie
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Erreur: La variable d'environnement ANTHROPIC_API_KEY n'est pas définie"
    echo "Définissez-la avec: export ANTHROPIC_API_KEY='votre-clé-api'"
    exit 1
fi

# Créer un environnement virtuel temporaire
echo "Création d'un environnement virtuel temporaire..."
python3 -m venv .temp_venv
source .temp_venv/bin/activate

# Installer le SDK Anthropic
echo "Installation du SDK Anthropic..."
pip install -q anthropic

# Créer un script Python de test
cat > test_api.py << 'EOF'
import os
import sys
from anthropic import Anthropic

# Récupérer la clé API
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Erreur: Clé API non trouvée")
    sys.exit(1)

# Initialiser le client
print("Initialisation du client Anthropic...")
client = Anthropic(api_key=api_key)

# Liste des modèles actuellement actifs
ACTIVE_MODELS = [
    "claude-3-haiku-20240307",
    "claude-3-opus-20240229",
    "claude-3-5-sonnet-20240620",
    "claude-3-5-haiku-20241022",
    "claude-3-5-sonnet-20241022",
    "claude-3-7-sonnet-20250219"
]

# Utiliser le premier modèle disponible qui fonctionne
for model in ACTIVE_MODELS:
    print(f"\nTentative avec le modèle {model}...")
    try:
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[
                {"role": "user", "content": "Réponds uniquement par 'API OK'"}
            ]
        )
        print(f"✅ Connexion à l'API Claude réussie avec le modèle {model}!")
        print(f"Réponse reçue: {response.content[0].text}")
        # Si on arrive ici, un modèle a fonctionné, on peut sortir de la boucle
        break
    except Exception as e:
        print(f"❌ Erreur avec le modèle {model}: {e}")
        if model == ACTIVE_MODELS[-1]:  # Si c'est le dernier modèle testé
            print("\n❌ Aucun des modèles n'a fonctionné. Vérifiez votre clé API et votre connexion.")
            sys.exit(1)

# Afficher la liste des modèles actifs
print("\nModèles actuellement actifs selon la documentation:")
for model in ACTIVE_MODELS:
    print(f"  - {model}")

print("\nTest terminé avec succès!")
EOF

# Exécuter le script de test
echo "Exécution du test d'API..."
python test_api.py

# Nettoyer
echo -e "\nNettoyage..."
deactivate
rm -f test_api.py
rm -rf .temp_venv

echo "Test terminé."
