# claude_edition_litteraire/llm/claude_provider.py
from .provider import LLMProvider

class ClaudeProvider(LLMProvider):
    """Implémentation de LLMProvider pour Claude API."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        # Initialiser le client Claude
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Le package 'anthropic' est requis pour utiliser ClaudeProvider")
    
    def chat(self, messages, max_tokens=1000):
        """Envoie une conversation à Claude et retourne la réponse."""
        # Conversion des messages au format Claude
        claude_messages = self._convert_messages(messages)
        
        # Appel à l'API Claude
        response = self.client.messages.create(
            model="claude-3-7-sonnet-20250219",  # Configurable
            max_tokens=max_tokens,
            messages=claude_messages
        )
        
        return response.content[0].text
    
    def _convert_messages(self, messages):
        """Convertit les messages au format Claude."""
        # Format unifié vers format Claude
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
    
    # Autres méthodes...