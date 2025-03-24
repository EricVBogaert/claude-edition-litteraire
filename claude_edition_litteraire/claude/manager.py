"""
Gestionnaire principal pour l'interaction avec Claude.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ClaudeManager:
    """
    Gère les interactions avec l'API Claude.
    """
    
    def __init__(self, project):
        """
        Initialise l'instance ClaudeManager.
        
        Args:
            project: Instance de la classe Project parente
        """
        self.project = project
        self.api_key = project.config.get("claude.api_key")
        logger.debug(f"ClaudeManager initialisé")
    
    def analyze_content(self, content: str, instruction: str) -> str:
        """
        Analyse un contenu avec Claude.
        
        Args:
            content: Contenu à analyser
            instruction: Instructions pour l'analyse
            
        Returns:
            Résultat de l'analyse
        """
        # Utiliser le module llm pour interagir avec Claude
        messages = [
            {"role": "system", "content": instruction},
            {"role": "user", "content": content}
        ]
        
        try:
            return self.project.llm.chat(messages)
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de contenu: {e}")
            return f"Erreur: {str(e)}"
