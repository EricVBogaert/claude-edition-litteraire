# claude_edition_litteraire/llm/claude_provider.py

import os
from typing import Dict, List, Any, Optional, Union, Iterator

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
    # def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le fournisseur Claude.
        
        Args:
            api_key: Clé API Claude (si None, utilise ANTHROPIC_API_KEY)
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "Le module 'anthropic' est requis pour utiliser ClaudeProvider. "
                "Installez-le avec 'pip install anthropic'."
            )
        
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Clé API Claude non fournie. Spécifiez-la en paramètre ou "
                "définissez la variable d'environnement ANTHROPIC_API_KEY."
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)        
        return response.content[0].text
    
    def _convert_messages(self, messages):
        """Convertit les messages au format Claude."""
        # Format unifié vers format Claude
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
    
 
    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convertit les messages au format attendu par Claude.
        
        Args:
            messages: Messages dans notre format interne
            
        Returns:
            Messages au format attendu par l'API Claude
        """
        claude_messages = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            claude_messages.append({
                "role": role,
                "content": content
            })
        
        return claude_messages
    
    def chat(self, messages: List[Dict[str, Any]], 
            max_tokens: int = 1000, 
            temperature: float = 0.7,
            stream: bool = False) -> Union[str, Iterator[str]]:
        """
        Envoie une conversation à Claude et retourne la réponse.
        """
        claude_messages = self._convert_messages(messages)
        
        if stream:
            # Mode streaming
            response_stream = self.client.messages.stream(
                max_tokens=max_tokens,
                messages=claude_messages,
                model="claude-3-sonnet-20240229",
                temperature=temperature
            )
            
            def response_generator():
                for chunk in response_stream:
                    if chunk.type == "content_block_delta" and chunk.delta.type == "text":
                        yield chunk.delta.text
            
            return response_generator()
        else:
            # Mode standard
            response = self.client.messages.create(
                max_tokens=max_tokens,
                messages=claude_messages,
                model="claude-3-sonnet-20240229",
                temperature=temperature
            )
            
            # Extraire le texte de la réponse
            return response.content[0].text
    
    def embed(self, text: str, model_name: Optional[str] = None) -> List[float]:
        """
        Génère un embedding avec l'API Claude.
        """
        model = model_name or "claude-3-sonnet-20240229"
        
        response = self.client.embeddings.create(
            model=model,
            input=text
        )
        
        return response.embedding
    
    def supported_models(self) -> List[str]:
        """
        Retourne la liste des modèles Claude supportés.
        """
        return [
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307"
        ]
    
    # Autres méthodes...
    # claude_edition_litteraire/llm/claude_provider.py
"""
2025-03-25: Visual Code; chat claude
Implémentation de l'interface LLMProvider pour l'API Claude d'Anthropic.
"""