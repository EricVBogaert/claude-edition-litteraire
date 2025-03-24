import pytest
import sys
import os

# Ajouter une méthode d'importation plus sûre
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import direct sans passer par le package principal
from claude_edition_litteraire.llm.context import ContextCompressor

def test_sliding_window():
    """Teste la stratégie de fenêtre glissante."""
    compressor = ContextCompressor()
    
    # Créer une liste de messages de test
    messages = [
        {"role": "system", "content": "Tu es un assistant"},
        {"role": "user", "content": "Message 1"},
        {"role": "assistant", "content": "Réponse 1"},
        {"role": "user", "content": "Message 2"},
        {"role": "assistant", "content": "Réponse 2"},
        {"role": "user", "content": "Message 3"}
    ]
    
    # Tester avec une fenêtre de taille 3
    result = compressor.sliding_window(messages, window_size=3)
    
    # Vérifier que le message système est conservé
    assert result[0]["role"] == "system"
    # Vérifier que la taille totale est correcte (système + 2 derniers)
    assert len(result) == 3
    # Vérifier que les derniers messages sont conservés
    assert result[-1]["content"] == "Message 3"
