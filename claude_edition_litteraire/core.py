"""
Module principal définissant la classe Project qui représente un projet d'édition littéraire.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from .structure import ProjectStructure
from .content import ContentManager
from .automation import AutomationManager
from .claude import ClaudeManager
from .utils.config import ConfigManager
from .utils.logging import get_logger

logger = get_logger(__name__)

class Project:
    """
    Représente un projet d'édition littéraire complet.
    
    Cette classe est le point d'entrée principal pour interagir avec un projet,
    donnant accès à toutes les fonctionnalités de validation, correction,
    et génération de contenu.
    """
    
    def __init__(self, project_path: Union[str, Path], config_path: Optional[str] = None):
        """
        Initialise un nouveau projet.
        
        Args:
            project_path: Chemin vers le répertoire du projet
            config_path: Chemin vers un fichier de configuration (facultatif)
        """
        self.path = Path(project_path).resolve()
        logger.debug(f"Initialisation du projet: {self.path}")
        
        if not self.path.exists():
            raise FileNotFoundError(f"Le répertoire du projet n'existe pas: {self.path}")
        
        if not self.path.is_dir():
            raise NotADirectoryError(f"Le chemin spécifié n'est pas un répertoire: {self.path}")
        
        # Initialiser le gestionnaire de configuration
        self.config = ConfigManager(self.path, config_path)
        
        # Initialiser les différents modules
        self.structure = ProjectStructure(self)
        self.content = ContentManager(self)
        self.automation = AutomationManager(self)
        self.claude = ClaudeManager(self)
    
    def validate(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Valide l'ensemble du projet et retourne tous les problèmes détectés.
        
        Returns:
            Un dictionnaire des problèmes par catégorie
        """
        logger.info(f"Validation du projet: {self.path}")
        
        issues = {
            "structure": self.structure.validate(),
            "content": self.content.validate(),
            # Autres validations...
        }
        
        return issues
    
    def fix_issues(self, interactive: bool = True) -> Dict[str, int]:
        """
        Tente de corriger automatiquement les problèmes détectés dans le projet.
        
        Args:
            interactive: Si True, demande confirmation avant chaque correction
            
        Returns:
            Un dictionnaire indiquant le nombre de problèmes corrigés par catégorie
        """
        logger.info(f"Correction des problèmes du projet: {self.path}")
        
        # Valider d'abord pour trouver les problèmes
        issues = self.validate()
        
        # Corriger les problèmes par catégorie
        fixed = {
            "structure": self.structure.fix_issues(issues["structure"], interactive),
            "content": self.content.fix_issues(issues["content"], interactive),
            # Autres corrections...
        }
        
        return fixed
    
    def get_chapter(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le contenu et les métadonnées d'un chapitre spécifique.
        
        Args:
            chapter_id: Identifiant du chapitre (nom de fichier ou slug)
            
        Returns:
            Dictionnaire contenant le contenu et les métadonnées du chapitre,
            ou None si le chapitre n'est pas trouvé
        """
        return self.content.get_chapter(chapter_id)
    
    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations sur un personnage spécifique.
        
        Args:
            character_id: Identifiant du personnage (nom de fichier ou slug)
            
        Returns:
            Dictionnaire contenant les informations du personnage,
            ou None si le personnage n'est pas trouvé
        """
        return self.content.get_character(character_id)
    
    def export(self, format: str, output_path: Optional[str] = None) -> str:
        """
        Exporte le projet dans le format spécifié.
        
        Args:
            format: Format d'exportation ('pdf', 'epub', 'html', etc.)
            output_path: Chemin de sortie pour le fichier généré (facultatif)
            
        Returns:
            Chemin du fichier généré
        """
        return self.automation.export(format, output_path)
    
    def __repr__(self) -> str:
        return f"Project(path='{self.path}')"