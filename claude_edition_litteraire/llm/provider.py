# claude_edition_litteraire/llm/provider.py
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Interface abstraite pour les fournisseurs de LLM."""
    
    @abstractmethod
    def chat(self, messages, max_tokens=1000):
        """Envoie une conversation au LLM et retourne la réponse."""
        pass
    
    @abstractmethod
    def embed(self, text):
        """Génère un embedding pour le texte fourni."""
        pass
    
    @abstractmethod
    def supported_models(self):
        """Retourne la liste des modèles supportés par ce fournisseur."""
        pass