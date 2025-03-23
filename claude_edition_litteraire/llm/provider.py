# claude_edition_litteraire/llm/provider.py
"""
Interface abstraite pour les fournisseurs de LLM.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Iterator

class LLMProvider(ABC):
    """Interface abstraite pour les fournisseurs de LLM."""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]], 
             max_tokens: int = 1000, 
             temperature: float = 0.7,
             stream: bool = False) -> Union[str, Iterator[str]]:
        """
        Envoie une conversation au LLM et retourne la réponse.
        
        Args:
            messages: Liste de messages de la conversation
            max_tokens: Nombre maximum de tokens pour la réponse
            temperature: Température pour la génération (0.0-1.0)
            stream: Si True, retourne un itérateur sur les fragments de réponse
            
        Returns:
            Texte de réponse ou itérateur sur les fragments
        """
        pass
    
    @abstractmethod
    def embed(self, text: str, model_name: Optional[str] = None) -> List[float]:
        """
        Génère un embedding pour le texte fourni.
        
        Args:
            text: Texte à encoder
            model_name: Nom du modèle d'embedding (optionnel)
            
        Returns:
            Liste de valeurs d'embedding
        """
        pass
    
    @abstractmethod
    def supported_models(self) -> List[str]:
        """
        Retourne la liste des modèles supportés par ce fournisseur.
        
        Returns:
            Liste des noms de modèles
        """
        pass