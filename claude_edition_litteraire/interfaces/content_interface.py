"""
Interface pour la gestion de contenu.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

class ContentManagerInterface(ABC):
    """Interface abstraite pour la gestion de contenu littéraire."""
    
    @abstractmethod
    def validate(self) -> List[Dict[str, Any]]:
        """
        Valide le contenu du projet.
        
        Returns:
            Liste des problèmes détectés
        """
        pass
    
    @abstractmethod
    def fix_issues(self, issues: List[Dict[str, Any]], interactive: bool = True) -> Dict[str, int]:
        """
        Tente de corriger les problèmes de contenu détectés.
        
        Args:
            issues: Liste des problèmes à corriger
            interactive: Si True, demande confirmation avant chaque correction
            
        Returns:
            Dictionnaire indiquant le nombre de problèmes corrigés par catégorie
        """
        pass
    
    @abstractmethod
    def get_chapter(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le contenu et les métadonnées d'un chapitre spécifique.
        
        Args:
            chapter_id: Identifiant du chapitre (nom de fichier ou slug)
            
        Returns:
            Dictionnaire contenant le contenu et les métadonnées du chapitre,
            ou None si le chapitre n'est pas trouvé
        """
        pass
    
    @abstractmethod
    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations sur un personnage spécifique.
        
        Args:
            character_id: Identifiant du personnage (nom de fichier ou slug)
            
        Returns:
            Dictionnaire contenant les informations du personnage,
            ou None si le personnage n'est pas trouvé
        """
        pass
