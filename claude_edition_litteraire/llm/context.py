# claude_edition_litteraire/llm/context.py
"""
Module pour la gestion du contexte des conversations LLM.
Optimisation, compression et nettoyage de contexte.
"""

from typing import List, Dict, Any, Optional
import re

class ContextCompressor:
    """
    Classe pour compresser le contexte avant les appels API à un LLM.
    Réduit la taille du contexte tout en préservant les informations importantes.
    """
    
    def __init__(self):
        """Initialise le compresseur de contexte."""
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estime le nombre de tokens dans un texte.
        
        Args:
            text: Texte à évaluer
            
        Returns:
            Estimation du nombre de tokens
        """
        # Estimation simple: en moyenne 1 token ≈ 4 caractères en anglais
        # Mais nous utilisons un facteur de 0.25 pour être prudent
        return int(len(text) * 0.25)
    
    def summarize_conversation(self, messages: List[Dict[str, Any]], 
                              max_summary_tokens: int = 500) -> Dict[str, Any]:
        """
        Crée un résumé de la conversation existante.
        
        Note: Cette fonction n'effectue pas réellement l'appel à un LLM,
        elle génère simplement une instruction pour résumer la conversation.
        L'appel doit être effectué par le client.
        
        Args:
            messages: Liste des messages de la conversation
            max_summary_tokens: Nombre maximum de tokens pour le résumé
            
        Returns:
            Message système contenant un résumé
        """
        # Formatage de la conversation pour le résumé
        conversation_text = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}" 
            for msg in messages
        ])
        
        summary_prompt = f"""Voici une conversation entre un utilisateur et un assistant IA:

{conversation_text}

Résume cette conversation en conservant TOUTES les informations importantes, 
les faits, les préférences exprimées, et les décisions prises.
Sois concis mais complet, en te limitant à environ {max_summary_tokens} tokens.
"""
        
        # Retourner une instruction pour créer un résumé
        # L'appel au LLM doit être fait par le client
        return {
            "role": "system", 
            "content": summary_prompt
        }
    
    def relevance_filter(self, messages: List[Dict[str, Any]], 
                       current_query: str, threshold: float = 0.2) -> List[Dict[str, Any]]:
        """
        Filtre les messages par pertinence avec la requête actuelle.
        
        Args:
            messages: Liste des messages de la conversation
            current_query: Requête actuelle
            threshold: Seuil de pertinence
            
        Returns:
            Liste filtrée de messages
        """
        if len(messages) <= 2:  # Conserver au moins les 2 derniers messages
            return messages
        
        # Approche simple: conserver toujours les N derniers messages
        # Dans une implémentation réelle, on utiliserait des embeddings ou TF-IDF
        return messages[-5:]
    
    def sliding_window(self, messages: List[Dict[str, Any]], 
                     window_size: int = 5) -> List[Dict[str, Any]]:
        """
        Applique une fenêtre glissante pour ne conserver que 
        les derniers messages du contexte.
        
        Args:
            messages: Liste des messages de la conversation
            window_size: Taille de la fenêtre
            
        Returns:
            Liste de messages dans la fenêtre
        """
        if len(messages) <= window_size:
            return messages
        else:
            # Toujours conserver le premier message (instructions initiales)
            system_messages = [msg for msg in messages if msg.get("role") == "system"]
            
            # Prendre les (window_size - len(system_messages)) derniers messages
            remaining_size = window_size - len(system_messages)
            recent_messages = messages[-remaining_size:] if remaining_size > 0 else []
            
            return system_messages + recent_messages
    
    def compress_by_strategy(self, messages: List[Dict[str, Any]], 
                           current_query: str, 
                           target_token_limit: int = 5000, 
                           strategy: str = "hybrid") -> List[Dict[str, Any]]:
        """
        Compresse le contexte en utilisant différentes stratégies
        pour rester sous une limite de tokens.
        
        Args:
            messages: Liste des messages de la conversation
            current_query: Requête actuelle
            target_token_limit: Limite de tokens cible
            strategy: Stratégie de compression ("sliding", "relevance", "summary", "hybrid")
            
        Returns:
            Liste de messages compressée
        """
        # Estimer les tokens actuels
        current_tokens = sum(self.estimate_tokens(msg.get("content", "")) for msg in messages)
        current_tokens += self.estimate_tokens(current_query)
        
        # Si déjà sous la limite, pas besoin de compression
        if current_tokens <= target_token_limit:
            return messages
        
        # Stratégie de fenêtre glissante
        if strategy == "sliding":
            return self.sliding_window(messages)
        
        # Stratégie de filtrage par pertinence
        elif strategy == "relevance":
            return self.relevance_filter(messages, current_query)
        
        # Stratégie hybride (la plus efficace en général)
        elif strategy == "hybrid":
            # Si le contexte est petit, utiliser sliding window
            if len(messages) < 10:
                return self.sliding_window(messages)
            
            # Pour un contexte moyen, filtrer par pertinence
            elif len(messages) < 20:
                return self.relevance_filter(messages, current_query)
                
            # Pour un contexte long, combiner les approches
            else:
                # Séparer les messages système
                system_messages = [msg for msg in messages if msg.get("role") == "system"]
                non_system_messages = [msg for msg in messages if msg.get("role") != "system"]
                
                # Prendre les 8 derniers messages non-système
                recent_messages = non_system_messages[-8:] if len(non_system_messages) > 8 else non_system_messages
                
                # Ajouter un résumé des anciens messages comme message système
                if len(non_system_messages) > 8:
                    old_messages = non_system_messages[:-8]
                    summary = {
                        "role": "system",
                        "content": (
                            "Contexte précédent de la conversation (résumé): "
                            f"{len(old_messages)} messages omis pour optimiser "
                            "le contexte. Les messages récents sont préservés."
                        )
                    }
                    return system_messages + [summary] + recent_messages
                else:
                    return system_messages + recent_messages
        
        # Par défaut, retourner les 5 derniers messages
        return messages[-5:]