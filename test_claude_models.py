#!/usr/bin/env python3
"""
Script pour tester les différents modèles Claude configurés.
"""

import os
import sys
import logging
from typing import List, Dict, Any

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au path pour importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from claude_edition_litteraire.llm.claude_provider import ClaudeProvider, CLAUDE_MODELS
except ImportError:
    logger.error("Module claude_provider.py non trouvé. Exécutez ce script depuis la racine du projet.")
    sys.exit(1)

def test_claude_models():
    """Teste tous les modèles Claude configurés."""
    
    # Vérifier que la clé API est définie
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("Variable d'environnement ANTHROPIC_API_KEY non définie. Définissez-la avant d'exécuter ce script.")
        sys.exit(1)
    
    # Initialiser le provider
    provider = ClaudeProvider(api_key)
    
    # Messages de test simples
    messages = [
        {"role": "user", "content": "Réponds uniquement par 'Modèle OK' sans aucun autre texte."}
    ]
    
    # Tester chaque modèle
    logger.info(f"Modèles disponibles: {provider.supported_models()}")
    logger.info("Test de chaque modèle...")
    
    results = {}
    
    # Tester chaque modèle complet (pas les alias)
    for name, model in CLAUDE_MODELS.items():
        if name == "default":
            continue  # Sauter l'alias "default" car il pointe vers un autre modèle
            
        logger.info(f"Test du modèle {name} ({model})...")
        try:
            response = provider.chat(messages, max_tokens=10, model_name=name)
            logger.info(f"✅ Modèle {name}: {response}")
            results[name] = {"status": "success", "response": response}
        except Exception as e:
            logger.error(f"❌ Modèle {name}: {str(e)}")
            results[name] = {"status": "error", "error": str(e)}
    
    # Afficher le récapitulatif
    print("\n====== RÉCAPITULATIF DES TESTS ======")
    successful = sum(1 for r in results.values() if r["status"] == "success")
    print(f"Modèles testés: {len(results)}")
    print(f"Modèles fonctionnels: {successful}")
    print(f"Modèles en erreur: {len(results) - successful}")
    
    print("\nDétails:")
    for name, result in results.items():
        status = "✅" if result["status"] == "success" else "❌"
        print(f"{status} {name} ({CLAUDE_MODELS[name]})")
    
    # Suggérer un modèle par défaut
    if successful > 0:
        suggested_default = next((name for name, r in results.items() if r["status"] == "success"), None)
        if suggested_default:
            print(f"\nModèle par défaut suggéré: {suggested_default} ({CLAUDE_MODELS[suggested_default]})")
            print(f"Pour définir ce modèle par défaut dans la configuration:")
            print(f'1. Modifiez "models.default" dans la configuration')
            print(f'2. Ou définissez une variable d\'environnement: export CLAUDE_DEFAULT_MODEL="{CLAUDE_MODELS[suggested_default]}"')

if __name__ == "__main__":
    test_claude_models()
