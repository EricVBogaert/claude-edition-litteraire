"""
Implémentation de l'interface LLMProvider pour l'API Claude d'Anthropic.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union, Iterator

from .provider import LLMProvider

logger = logging.getLogger(__name__)

# Modèles Claude actifs (Mars 2025)
CLAUDE_MODELS = {
    "haiku": "claude-3-haiku-20240307",
    "opus": "claude-3-opus-20240229",
    "sonnet-3.5": "claude-3-5-sonnet-20241022",
    "haiku-3.5": "claude-3-5-haiku-20241022",
    "sonnet-3.7": "claude-3-7-sonnet-20250219",
    "default": "claude-3-5-sonnet-20241022"
}

class ClaudeProvider(LLMProvider):
    """Implémentation de l'interface LLMProvider pour Claude."""
    
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        """
        Initialise le fournisseur Claude.
        
        Args:
            api_key: Clé API Claude (si None, utilise ANTHROPIC_API_KEY)
            default_model: Modèle par défaut à utiliser (si None, utilise la configuration)
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
        self.default_model = default_model or CLAUDE_MODELS["default"]
        logger.info(f"ClaudeProvider initialisé avec le modèle par défaut: {self.default_model}")
    
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
    
    def _resolve_model_name(self, model_name: Optional[str] = None) -> str:
        """
        Résout le nom du modèle à partir d'un alias ou utilise le modèle par défaut.
        
        Args:
            model_name: Nom ou alias du modèle (ex: "haiku", "opus", ou nom complet)
            
        Returns:
            Nom complet du modèle à utiliser
        """
        if not model_name:
            return self.default_model
        
        # Si c'est un alias, le convertir
        if model_name in CLAUDE_MODELS:
            return CLAUDE_MODELS[model_name]
        
        # Sinon, utiliser le nom tel quel (avec validation)
        if not any(actual_model in model_name for actual_model in ["claude-3", "claude-3.5", "claude-3.7"]):
            logger.warning(
                f"Le modèle '{model_name}' ne semble pas être un modèle Claude valide. "
                f"Utilisation du modèle par défaut: {self.default_model}"
            )
            return self.default_model
            
        return model_name
    
    def chat(self, messages: List[Dict[str, Any]], 
            max_tokens: int = 1000, 
            temperature: float = 0.7,
            stream: bool = False,
            model_name: Optional[str] = None) -> Union[str, Iterator[str]]:
        """
        Envoie une conversation à Claude et retourne la réponse.
        
        Args:
            messages: Liste de messages de la conversation
            max_tokens: Nombre maximum de tokens pour la réponse
            temperature: Température pour la génération (0.0-1.0)
            stream: Si True, retourne un itérateur sur les fragments de réponse
            model_name: Nom du modèle à utiliser (si None, utilise le modèle par défaut)
            
        Returns:
            Texte de réponse ou itérateur sur les fragments
        """
        claude_messages = self._convert_messages(messages)
        actual_model = self._resolve_model_name(model_name)
        
        try:
            if stream:
                # Mode streaming
                response_stream = self.client.messages.stream(
                    max_tokens=max_tokens,
                    messages=claude_messages,
                    model=actual_model,
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
                    model=actual_model,
                    temperature=temperature
                )
                
                # Extraire le texte de la réponse
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API Claude avec le modèle {actual_model}: {e}")
            
            if "not_found_error" in str(e) and model_name is not None:
                # Essayer avec le modèle par défaut en cas d'erreur
                logger.warning(f"Tentative avec le modèle par défaut: {self.default_model}")
                return self.chat(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream,
                    model_name=None  # Utiliser le modèle par défaut
                )
            
            # Si c'est déjà le modèle par défaut ou une autre erreur, la propager
            raise
    
    def embed(self, text: str, model_name: Optional[str] = None) -> List[float]:
        """
        Génère un embedding avec l'API Claude.
        
        Args:
            text: Texte à encoder
            model_name: Nom du modèle d'embedding (optionnel)
            
        Returns:
            Liste de valeurs d'embedding
        """
        actual_model = self._resolve_model_name(model_name)
        
        try:
            response = self.client.embeddings.create(
                model=actual_model,
                input=text
            )
            
            return response.embedding
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embedding avec le modèle {actual_model}: {e}")
            raise
    
    def supported_models(self) -> List[str]:
        """
        Retourne la liste des modèles Claude supportés.
        
        Returns:
            Liste des noms de modèles
        """
        # Retourner à la fois les alias et les noms complets
        aliases = list(CLAUDE_MODELS.keys())
        full_names = list(set(CLAUDE_MODELS.values()))  # Utiliser un set pour éviter les doublons
        
        return aliases + full_names
