# claude_edition_litteraire/llm/unified_llm.py
from .provider import LLMProvider
from .claude_provider import ClaudeProvider
from .lmstudio_provider import LMStudioProvider

class UnifiedLLM:
    """Interface unifiée pour différents LLMs."""
    
    def __init__(self, provider="auto", api_key=None, api_url=None):
        """
        Initialise le client LLM avec le fournisseur spécifié.
        
        Args:
            provider: Type de fournisseur ('claude', 'lmstudio', 'auto')
            api_key: Clé API pour les services cloud (Claude)
            api_url: URL de l'API pour les services locaux (LMStudio)
        """
        self.providers = {}
        
        # Essayer d'initialiser les fournisseurs disponibles
        try:
            self.providers["claude"] = ClaudeProvider(api_key)
        except (ImportError, ValueError):
            pass
            
        try:
            self.providers["lmstudio"] = LMStudioProvider(api_url)
        except ImportError:
            pass
            
        # Déterminer le fournisseur actif
        if provider == "auto":
            # Préférer LMStudio pour économiser les coûts pendant les tests
            if "lmstudio" in self.providers:
                self.active_provider = "lmstudio"
            elif "claude" in self.providers:
                self.active_provider = "claude"
            else:
                raise ValueError("Aucun fournisseur disponible")
        else:
            if provider not in self.providers:
                raise ValueError(f"Fournisseur '{provider}' non disponible")
            self.active_provider = provider
    
    def chat(self, messages, max_tokens=1000):
        """
        Envoie une conversation au LLM actif et retourne la réponse.
        
        Args:
            messages: Liste de messages (format: [{"role": "...", "content": "..."}])
            max_tokens: Nombre maximum de tokens pour la réponse
            
        Returns:
            Réponse du LLM
        """
        provider = self.providers[self.active_provider]
        return provider.chat(messages, max_tokens)
    
    def set_provider(self, provider):
        """Change le fournisseur actif."""
        if provider not in self.providers:
            raise ValueError(f"Fournisseur '{provider}' non disponible")
        self.active_provider = provider
    
    def get_provider(self):
        """Retourne le nom du fournisseur actif."""
        return self.active_provider