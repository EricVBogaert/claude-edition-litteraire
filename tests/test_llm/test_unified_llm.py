import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter une méthode d'importation plus sûre
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import direct sans passer par le package principal
from claude_edition_litteraire.llm.unified_llm import UnifiedLLM

class MockProvider:
    def chat(self, messages, max_tokens=1000, temperature=0.7, stream=False):
        return "Réponse de test"
    
    def embed(self, text, model_name=None):
        return [0.1] * 384
    
    def supported_models(self):
        return ["mock-model"]

def test_create_message():
    """Teste la méthode create_message."""
    llm = UnifiedLLM.__new__(UnifiedLLM)
    llm.providers = {"mock": MockProvider()}
    llm.active_provider = "mock"
    
    message = llm.create_message("user", "Test message")
    
    assert message["role"] == "user"
    assert message["content"] == "Test message"
