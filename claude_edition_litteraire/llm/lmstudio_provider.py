# claude_edition_litteraire/llm/lmstudio_provider.py
"""
Implémentation de l'interface LLMProvider pour LMStudio.
"""

from typing import Dict, List, Any, Optional, Union, Iterator
import logging

from .provider import LLMProvider

logger = logging.getLogger(__name__)

class LMStudioProvider(LLMProvider):
    """Implémentation de l'interface LLMProvider pour LMStudio."""
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Initialise le fournisseur LMStudio.
        
        Args:
            api_url: URL de l'API LMStudio (si différente de l'URL par défaut)
        """
        self.api_url = api_url
        
        try:
            import lmstudio
            self.lmstudio_available = True
        except ImportError:
            logger.warning("Module 'lmstudio' non disponible. Utilisation en mode simulation.")
            self.lmstudio_available = False
        
        # Dictionnaire pour stocker les modèles chargés
        self._loaded_models = {}
    
    def _get_or_load_model(self, model_name: str):
        """
        Récupère un modèle chargé ou le charge si nécessaire.
        
        Args:
            model_name: Nom du modèle à charger
            
        Returns:
            Instance du modèle LMStudio
        """
        if not self.lmstudio_available:
            raise ImportError("Module 'lmstudio' requis pour cette fonctionnalité")
        
        if model_name not in self._loaded_models:
            import lmstudio
            self._loaded_models[model_name] = lmstudio.llm(model_name)
        
        return self._loaded_models[model_name]
    
    def _convert_messages_to_chat(self, messages: List[Dict[str, Any]]):
        """
        Convertit les messages en objet Chat LMStudio.
        
        Args:
            messages: Messages dans notre format interne
            
        Returns:
            Objet Chat LMStudio
        """
        if not self.lmstudio_available:
            raise ImportError("Module 'lmstudio' requis pour cette fonctionnalité")
        
        import lmstudio
        chat = lmstudio.Chat()
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                chat.system = content
            elif role == "user":
                chat.add_user_message(content)
            elif role == "assistant":
                chat.add_assistant_message(content)
        
        return chat
    
    def chat(self, messages: List[Dict[str, Any]], 
            max_tokens: int = 1000, 
            temperature: float = 0.7,
            stream: bool = False) -> Union[str, Iterator[str]]:
        """
        Envoie une conversation à LMStudio et retourne la réponse.
        """
        if not self.lmstudio_available:
            # Mode simulation pour les tests
            return self._simulated_chat(messages, max_tokens, temperature, stream)
        
        # Déterminer le modèle à utiliser (par défaut: premier modèle disponible)
        try:
            import lmstudio
            available_models = lmstudio.system.rpc.list_downloaded_models()
            if not available_models:
                raise ValueError("Aucun modèle LMStudio disponible.")
            
            model_name = available_models[0].model_key
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modèles LMStudio: {e}")
            model_name = "qwen2.5-7b-instruct-1m"  # Modèle par défaut
        
        # Obtenir le modèle
        model = self._get_or_load_model(model_name)
        
        # Convertir les messages en chat LMStudio
        chat = self._convert_messages_to_chat(messages)
        
        # Configurer les options LMStudio
        lmstudio_config = {
            "temperature": temperature,
            "maxTokens": max_tokens,
            "topPSampling": 0.9
        }
        
        if stream:
            # Mode streaming
            prediction_stream = model.respond_stream(
                chat,
                config=lmstudio_config,
                on_message=chat.append
            )
            
            def response_generator():
                for fragment in prediction_stream:
                    yield fragment.content
            
            return response_generator()
        else:
            # Mode standard
            response = model.respond(
                chat,
                config=lmstudio_config
            )
            
            return response
    
    def _simulated_chat(self, messages: List[Dict[str, Any]], 
                       max_tokens: int = 1000, 
                       temperature: float = 0.7,
                       stream: bool = False) -> Union[str, Iterator[str]]:
        """
        Simule une réponse LMStudio pour les tests sans dépendance.
        """
        # Dernier message utilisateur
        last_user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break
        
        # Réponse simulée
        simulated_response = (
            f"[Réponse LMStudio simulée] Réponse à: {last_user_message[:50]}... "
            f"Cette réponse est simulée car le module 'lmstudio' n'est pas disponible."
        )
        
        if stream:
            # Simuler un stream de réponse
            fragments = []
            chunk_size = 10
            for i in range(0, len(simulated_response), chunk_size):
                fragments.append(simulated_response[i:i+chunk_size])
            
            def mock_generator():
                import time
                for fragment in fragments:
                    time.sleep(0.05)  # Simuler un délai
                    yield fragment
            
            return mock_generator()
        else:
            return simulated_response
    
    def embed(self, text: str, model_name: Optional[str] = None) -> List[float]:
        """
        Génère un embedding avec LMStudio.
        """
        if not self.lmstudio_available:
            # Retourner un embedding simulé
            return [0.1] * 384  # Dimension standard pour un embedding
        
        try:
            import lmstudio
            
            # Récupérer ou charger un modèle d'embedding
            if model_name:
                embedding_model = lmstudio.embedding.channel.get_or_load(model_name)
            else:
                # Prendre le premier disponible ou en charger un
                loaded_models = lmstudio.embedding.rpc.list_loaded()
                if loaded_models:
                    embedding_model = loaded_models[0]
                else:
                    embedding_model = lmstudio.embedding.channel.get_or_load("embedding-model")
            
            # Générer l'embedding
            result = lmstudio.embedding.rpc.embed_string(
                modelSpecifier={"type": "instanceReference", 
                               "instanceReference": embedding_model.instance_reference},
                inputString=text
            )
            
            return result.embedding
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embedding avec LMStudio: {e}")
            # Retourner un embedding simulé en cas d'erreur
            return [0.1] * 384
    
    def supported_models(self) -> List[str]:
        """
        Retourne la liste des modèles supportés par LMStudio.
        """
        if not self.lmstudio_available:
            return ["qwen2.5-7b-instruct-1m", "llama3-8b-instruct", "gemma-7b-instruct"]
        
        try:
            import lmstudio
            models = lmstudio.system.rpc.list_downloaded_models()
            return [model.model_key for model in models]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modèles LMStudio: {e}")
            return ["qwen2.5-7b-instruct-1m", "llama3-8b-instruct", "gemma-7b-instruct"]