"""
Module de gestion de configuration pour la bibliothèque.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union

from .logging import get_logger

logger = get_logger(__name__)

# Configuration par défaut
DEFAULT_CONFIG = {
    "project": {
        "name": "Projet Littéraire",
        "author": "Auteur"
    },
    "structure": {
        # Utilise les valeurs par défaut de structure/validator.py
    },
    "templates": {
        # Utilise les valeurs par défaut de structure/validator.py
    },
    "frontmatter": {
        # Utilise les valeurs par défaut de structure/validator.py
    },
    "claude": {
        "api_key": "",
        "model": "claude-3-5-sonnet-20241022"
    },
    "export": {
        "default_format": "markdown",
        "pdf": {
            "engine": "xelatex",
            "template": "template.tex"
        },
        "epub": {
            "cover_image": "cover.jpg"
        }
    }
}

class ConfigManager:
    """
    Gestionnaire de configuration pour le projet littéraire.
    """
    
    def __init__(self, project_path: Union[str, Path], config_path: Optional[str] = None):
        """
        Initialise le gestionnaire de configuration.
        
        Args:
            project_path: Chemin du projet
            config_path: Chemin du fichier de configuration, si None, cherche dans le projet
        """
        if isinstance(project_path, str):
            project_path = Path(project_path)
        
        self.project_path = project_path
        self.config = DEFAULT_CONFIG.copy()
        
        # Charger la configuration
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Chercher dans les emplacements standards
            for config_name in ['.claude_config.yml', 'claude_config.yml', 'config/claude_config.yml']:
                potential_path = project_path / config_name
                if potential_path.exists():
                    self.config_path = potential_path
                    break
            else:
                # Aucun fichier de configuration trouvé, utiliser la valeur par défaut
                self.config_path = project_path / '.claude_config.yml'
        
        # Charger la configuration si elle existe
        if self.config_path.exists():
            self._load_config()
        else:
            logger.info(f"Aucun fichier de configuration trouvé à {self.config_path}, utilisation des valeurs par défaut")
    
    def _load_config(self):
        """
        Charge la configuration depuis le fichier.
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
            
            # Fusionner avec la configuration par défaut
            self._merge_configs(self.config, user_config)
            
            logger.info(f"Configuration chargée depuis {self.config_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
    
    def _merge_configs(self, base: Dict[str, Any], update: Dict[str, Any]):
        """
        Fusionne deux dictionnaires de configuration de manière récursive.
        
        Args:
            base: Dictionnaire de base à mettre à jour
            update: Dictionnaire contenant les mises à jour
        """
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                # Fusion récursive pour les sous-dictionnaires
                self._merge_configs(base[key], value)
            else:
                # Remplacement direct pour les autres valeurs
                base[key] = value
    
    def save(self):
        """
        Sauvegarde la configuration dans le fichier.
        """
        try:
            # S'assurer que le répertoire parent existe
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            logger.info(f"Configuration sauvegardée dans {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.
        
        Args:
            key: Clé de configuration (peut être un chemin avec des points)
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Valeur de configuration
        """
        # Gestion des clés hiérarchiques (par exemple "export.pdf.engine")
        if '.' in key:
            parts = key.split('.')
            value = self.config
            
            for part in parts:
                if part in value:
                    value = value[part]
                else:
                    return default
            
            return value
        else:
            return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Définit une valeur de configuration.
        
        Args:
            key: Clé de configuration (peut être un chemin avec des points)
            value: Valeur à définir
        """
        # Gestion des clés hiérarchiques
        if '.' in key:
            parts = key.split('.')
            config = self.config
            
            # Naviguer jusqu'au dernier niveau
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            
            # Définir la valeur
            config[parts[-1]] = value
        else:
            self.config[key] = value
