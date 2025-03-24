"""
Interface pour la structure de projet.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

class ProjectStructureInterface(ABC):
    """Interface abstraite pour la gestion de structure de projet."""
    
    @abstractmethod
    def validate(self) -> List[Dict[str, Any]]:
        """
        Valide la structure complète du projet.
        
        Returns:
            Liste des problèmes détectés
        """
        pass
    
    @abstractmethod
    def fix_issues(self, 
                 issues: Optional[List[Dict[str, Any]]] = None, 
                 interactive: bool = True,
                 backup: bool = True) -> Dict[str, int]:
        """
        Corrige les problèmes détectés dans la structure du projet.
        
        Args:
            issues: Liste des problèmes à corriger
            interactive: Si True, demande confirmation avant chaque correction
            backup: Si True, crée une sauvegarde du projet avant les modifications
            
        Returns:
            Dictionnaire indiquant le nombre de corrections par catégorie
        """
        pass
    
    @abstractmethod
    def generate_report(self, 
                      issues: Optional[List[Dict[str, Any]]] = None, 
                      output_format: str = "markdown",
                      output_file: Optional[str] = None) -> str:
        """
        Génère un rapport sur les problèmes de structure détectés.
        
        Args:
            issues: Liste des problèmes à inclure dans le rapport
            output_format: Format du rapport ("markdown" ou "html")
            output_file: Nom du fichier de sortie
            
        Returns:
            Chemin du fichier de rapport généré, ou contenu du rapport
        """
        pass
