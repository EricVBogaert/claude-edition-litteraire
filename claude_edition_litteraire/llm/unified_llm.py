# claude_edition_litteraire/llm/unified_llm.py
"""
Interface unifiée pour interagir avec différents modèles de langage (LLMs).
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union, Iterator

from .provider import LLMProvider
from .claude_provider import ClaudeProvider
from .lmstudio_provider import LMStudioProvider
from .context import ContextCompressor

logger = logging.getLogger(__name__)

class UnifiedLLM:
    """
    Interface unifiée pour interagir avec différents LLMs.
    Permet de basculer facilement entre différents fournisseurs.
    """
    
    def __init__(self, provider: str = "auto", api_key: Optional[str] = None):
        """
        Initialise le client UnifiedLLM.
        
        Args:
            provider: Le fournisseur à utiliser ('claude', 'lmstudio', 'auto')
            api_key: Clé API pour les fournisseurs cloud (Claude)
        """
        self.providers = {}
        
        # Initialiser les fournisseurs disponibles
        try:
            # Essayer d'initialiser Claude
            if provider in ["claude", "auto"]:
                self.providers["claude"] = ClaudeProvider(api_key)
        except (ImportError, ValueError) as e:
            if provider == "claude":
                logger.error(f"Impossible d'initialiser Claude: {e}")
                raise
            logger.warning(f"Claude non disponible: {e}")
        
        try:
            # Essayer d'initialiser LMStudio
            if provider in ["lmstudio", "auto"]:
                self.providers["lmstudio"] = LMStudioProvider()
        except ImportError as e:
            if provider == "lmstudio":
                logger.error(f"Impossible d'initialiser LMStudio: {e}")
                raise
            logger.warning(f"LMStudio non disponible: {e}")
        
        # Vérifier qu'au moins un fournisseur est disponible
        if not self.providers:
            raise ValueError(
                "Aucun fournisseur LLM disponible. Installez 'anthropic' pour Claude "
                "ou 'lmstudio' pour LMStudio."
            )
        
        # Sélectionner le fournisseur actif
        if provider == "auto":
            # Préférer LMStudio pour les tests locaux
            if "lmstudio" in self.providers:
                self.active_provider = "lmstudio"
            else:
                self.active_provider = next(iter(self.providers.keys()))
        else:
            if provider not in self.providers:
                raise ValueError(f"Fournisseur demandé '{provider}' non disponible")
            self.active_provider = provider
        
        # Initialiser le compresseur de contexte
        self.context_compressor = ContextCompressor()
        
        logger.info(f"UnifiedLLM initialisé avec fournisseur: {self.active_provider}")
    
    def get_provider(self) -> str:
        """
        Récupère le nom du fournisseur actuellement utilisé.
        
        Returns:
            Nom du fournisseur actif
        """
        return self.active_provider
    
    def set_provider(self, provider: str) -> None:
        """
        Change le fournisseur actif.
        
        Args:
            provider: Nom du fournisseur ('claude', 'lmstudio')
        
        Raises:
            ValueError: Si le fournisseur n'est pas disponible
        """
        if provider not in self.providers:
            raise ValueError(
                f"Fournisseur '{provider}' non disponible. "
                f"Disponibles: {list(self.providers.keys())}"
            )
        
        self.active_provider = provider
        logger.info(f"Fournisseur changé pour: {provider}")
    
    def chat(self, messages: List[Dict[str, Any]], 
            max_tokens: int = 1000, 
            temperature: float = 0.7,
            stream: bool = False,
            compress_context: bool = True,
            target_token_limit: int = 5000) -> Union[str, Iterator[str]]:
        """
        Envoie une conversation au LLM et retourne la réponse.
        
        Args:
            messages: Liste de messages de la conversation
            max_tokens: Nombre maximum de tokens pour la réponse
            temperature: Température pour la génération (0.0-1.0)
            stream: Si True, retourne un itérateur sur les fragments de réponse
            compress_context: Si True, compresse le contexte
            target_token_limit: Limite de tokens pour la compression
            
        Returns:
            Texte de réponse ou itérateur sur les fragments
        """
        # Récupérer le fournisseur actif
        provider = self.providers[self.active_provider]
        
        # Compresser le contexte si demandé
        if compress_context and len(messages) > 3:
            # On considère le dernier message comme la requête courante
            current_query = messages[-1].get("content", "") if messages[-1].get("role") == "user" else ""
            messages = self.context_compressor.compress_by_strategy(
                messages[:-1] if current_query else messages,
                current_query,
                target_token_limit
            )
            # Réajouter la requête courante si elle a été retirée
            if current_query:
                messages.append({"role": "user", "content": current_query})
        
        # Appeler le fournisseur
        return provider.chat(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream
        )
    
    def embed(self, text: str, model_name: Optional[str] = None) -> List[float]:
        """
        Génère un embedding pour le texte fourni.
        
        Args:
            text: Texte à encoder
            model_name: Nom du modèle d'embedding (optionnel)
            
        Returns:
            Liste de valeurs d'embedding
        """
        provider = self.providers[self.active_provider]
        return provider.embed(text, model_name)
    
    def supported_models(self) -> List[str]:
        """
        Retourne la liste des modèles supportés par le fournisseur actif.
        
        Returns:
            Liste des noms de modèles
        """
        provider = self.providers[self.active_provider]
        return provider.supported_models()
    
    def create_message(self, role: str, content: str) -> Dict[str, Any]:
        """
        Crée un message formaté pour une conversation.
        
        Args:
            role: Rôle du message ('user', 'assistant', 'system')
            content: Contenu du message
            
        Returns:
            Message formaté
        """
        if role not in ['user', 'assistant', 'system']:
            raise ValueError(f"Rôle '{role}' non valide. Utilisez 'user', 'assistant' ou 'system'.")
        
        return {
            "role": role,
            "content": content
        }
    
def optimize_context(self, messages: List[Dict[str, Any]], 
                   current_query: str, 
                   strategy: str = "hybrid",
                   target_token_limit: int = 5000) -> List[Dict[str, Any]]:
    """
    Optimise le contexte de conversation selon une stratégie choisie.
    
    Args:
        messages: Liste des messages de la conversation
        current_query: Requête actuelle
        strategy: Stratégie d'optimisation ('sliding', 'relevance', 'hybrid')
        target_token_limit: Limite de tokens cible
        
    Returns:
        Liste de messages optimisée
    """
    return self.context_compressor.compress_by_strategy(
        messages,
        current_query,
        target_token_limit,
        strategy
    )