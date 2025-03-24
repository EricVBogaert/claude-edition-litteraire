#!/bin/bash
# fix-common-imports.sh
# Script pour corriger les imports circulaires les plus courants

echo "🔧 Correction des imports circulaires courants..."

# Créer un dossier pour les interfaces
mkdir -p claude_edition_litteraire/interfaces

# 1. Créer l'interface pour LLMProvider
echo "🏗️ Création de l'interface pour LLMProvider..."
cat > claude_edition_litteraire/interfaces/llm_interface.py << 'EOF'
"""
Interface pour les fournisseurs de LLM (Large Language Models).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Iterator

class LLMProviderInterface(ABC):
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
EOF

# 2. Créer l'interface pour ProjectStructure
echo "🏗️ Création de l'interface pour ProjectStructure..."
cat > claude_edition_litteraire/interfaces/structure_interface.py << 'EOF'
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
EOF

# 3. Créer l'interface pour ContentManager
echo "🏗️ Création de l'interface pour ContentManager..."
cat > claude_edition_litteraire/interfaces/content_interface.py << 'EOF'
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
EOF

# 4. Créer le module d'injection de dépendances
echo "🏗️ Création du module d'injection de dépendances..."
cat > claude_edition_litteraire/utils/dependency_injection.py << 'EOF'
"""
Module d'injection de dépendances pour résoudre les imports circulaires.
"""

from typing import Dict, Any, Optional, Type, TypeVar, Generic

T = TypeVar('T')

class ServiceProvider:
    """
    Fournisseur de services centralisé pour l'injection de dépendances.
    
    Cette classe permet de résoudre les problèmes d'imports circulaires
    en servant de point central pour l'accès aux services.
    """
    
    def __init__(self):
        """Initialise le fournisseur de services."""
        self._services = {}
        self._factories = {}
    
    def register(self, service_type: str, instance: Any) -> None:
        """
        Enregistre une instance de service.
        
        Args:
            service_type: Type de service (nom de classe ou identifiant)
            instance: Instance du service
        """
        self._services[service_type] = instance
    
    def register_factory(self, service_type: str, factory) -> None:
        """
        Enregistre une factory pour créer un service à la demande.
        
        Args:
            service_type: Type de service (nom de classe ou identifiant)
            factory: Fonction factory qui crée l'instance
        """
        self._factories[service_type] = factory
    
    def get(self, service_type: str) -> Any:
        """
        Récupère une instance de service.
        
        Args:
            service_type: Type de service à récupérer
            
        Returns:
            Instance du service demandé
            
        Raises:
            KeyError: Si le service n'est pas enregistré
        """
        # Si déjà instancié, le retourner directement
        if service_type in self._services:
            return self._services[service_type]
        
        # Sinon, utiliser la factory si disponible
        if service_type in self._factories:
            instance = self._factories[service_type](self)
            self._services[service_type] = instance
            return instance
        
        raise KeyError(f"Service non enregistré: {service_type}")
    
    def has(self, service_type: str) -> bool:
        """
        Vérifie si un service est disponible.
        
        Args:
            service_type: Type de service à vérifier
            
        Returns:
            True si le service est disponible, False sinon
        """
        return service_type in self._services or service_type in self._factories

# Instance globale du fournisseur de services
_provider = ServiceProvider()

def get_service_provider() -> ServiceProvider:
    """
    Récupère l'instance globale du fournisseur de services.
    
    Returns:
        Instance du ServiceProvider
    """
    return _provider
EOF

# 5. Modifier le fichier provider.py pour utiliser l'interface
if [[ -f "claude_edition_litteraire/llm/provider.py" ]]; then
    echo "🔄 Modification de provider.py pour utiliser l'interface..."
    cp "claude_edition_litteraire/llm/provider.py" "claude_edition_litteraire/llm/provider.py.bak"
    
    sed -i '1,/^from abc import ABC, abstractmethod$/d' "claude_edition_litteraire/llm/provider.py"
    sed -i '1i"""Interface abstraite pour les fournisseurs de LLM."""\n\nfrom ..interfaces.llm_interface import LLMProviderInterface' "claude_edition_litteraire/llm/provider.py"
    sed -i 's/class LLMProvider(ABC):/class LLMProvider(LLMProviderInterface):/' "claude_edition_litteraire/llm/provider.py"
fi

# 6. Créer init.py pour le module interfaces
echo "🏗️ Création de __init__.py pour le module interfaces..."
cat > claude_edition_litteraire/interfaces/__init__.py << 'EOF'
"""
Interfaces abstraites pour résoudre les dépendances circulaires.
"""

from .llm_interface import LLMProviderInterface
from .structure_interface import ProjectStructureInterface
from .content_interface import ContentManagerInterface

__all__ = [
    "LLMProviderInterface",
    "ProjectStructureInterface",
    "ContentManagerInterface"
]
EOF

# 7. Adapter core.py pour utiliser l'injection de dépendances
if [[ -f "claude_edition_litteraire/core.py" ]]; then
    echo "🔄 Adaptation de core.py pour utiliser l'injection de dépendances..."
    
    # Créer un fichier temporaire avec les modifications
    cat > /tmp/core_modified.py << 'EOF'
"""
Module principal définissant la classe Project qui représente un projet d'édition littéraire.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Type

from .utils.config import ConfigManager
from .utils.logging import get_logger
from .utils.dependency_injection import get_service_provider, ServiceProvider

# Imports des interfaces pour éviter les imports circulaires
from .interfaces.llm_interface import LLMProviderInterface
from .interfaces.structure_interface import ProjectStructureInterface
from .interfaces.content_interface import ContentManagerInterface

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
        
        # Initialiser la configuration
        self.config = ConfigManager(project_path, config_path)
        
        # Accéder au fournisseur de services
        self.provider = get_service_provider()
        
        # Initialiser les services principaux avec lazy loading
        self._init_services()
    
    def _init_services(self):
        """Initialise les services principaux avec lazy loading."""
        # Enregistrer les factories pour créer les services à la demande
        
        # Factory pour UnifiedLLM
        def create_llm(provider: ServiceProvider):
            # Import tardif pour éviter les imports circulaires
            from .llm.unified_llm import UnifiedLLM
            
            api_key = self.config.get("claude.api_key")
            api_url = self.config.get("lmstudio.api_url", "http://localhost:1234/v1")
            default_provider = self.config.get("llm.default_provider", "auto")
            
            return UnifiedLLM(
                provider=default_provider,
                api_key=api_key,
                api_url=api_url
            )
        
        # Factory pour ProjectStructure
        def create_structure(provider: ServiceProvider):
            # Import tardif pour éviter les imports circulaires
            from .structure.project_structure import ProjectStructure
            return ProjectStructure(self)
        
        # Factory pour ContentManager
        def create_content(provider: ServiceProvider):
            # Import tardif pour éviter les imports circulaires
            from .content.content_manager import ContentManager
            return ContentManager(self)
        
        # Factory pour ClaudeManager
        def create_claude(provider: ServiceProvider):
            # Import tardif pour éviter les imports circulaires
            from .claude.manager import ClaudeManager
            return ClaudeManager(self)
        
        # Factory pour AutomationManager
        def create_automation(provider: ServiceProvider):
            # Import tardif pour éviter les imports circulaires
            from .automation.manager import AutomationManager
            return AutomationManager(self)
        
        # Enregistrer les factories
        self.provider.register_factory("llm", create_llm)
        self.provider.register_factory("structure", create_structure)
        self.provider.register_factory("content", create_content)
        self.provider.register_factory("claude", create_claude)
        self.provider.register_factory("automation", create_automation)
    
    @property
    def llm(self) -> LLMProviderInterface:
        """Accède au service LLM."""
        return self.provider.get("llm")
    
    @property
    def structure(self) -> ProjectStructureInterface:
        """Accède au service de structure."""
        return self.provider.get("structure")
    
    @property
    def content(self) -> ContentManagerInterface:
        """Accède au service de gestion de contenu."""
        return self.provider.get("content")
    
    @property
    def claude(self):
        """Accède au service Claude."""
        return self.provider.get("claude")
    
    @property
    def automation(self):
        """Accède au service d'automatisation."""
        return self.provider.get("automation")
    
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
    
    def analyze_content(self, content, instruction):
        """Analyse un contenu avec le LLM configuré."""
        messages = [
            {"role": "system", "content": instruction},
            {"role": "user", "content": content}
        ]
        return self.llm.chat(messages)
    
    def __repr__(self) -> str:
        return f"Project(path='{self.path}')"
EOF

    # Remplacer le fichier original
    read -p "⚠️ Cette opération va remplacer core.py. Continuer? [Y/n] " confirmation
    if [[ "$confirmation" != [nN] ]]; then
        cp "claude_edition_litteraire/core.py" "claude_edition_litteraire/core.py.bak"
        cp /tmp/core_modified.py "claude_edition_litteraire/core.py"
        echo "✅ core.py modifié avec succès."
    else
        echo "❌ Opération annulée."
        # Sauvegarder les modifications pour référence
        cp /tmp/core_modified.py "claude_edition_litteraire/core.py.new"
        echo "💾 Les modifications proposées ont été sauvegardées dans core.py.new"
    fi
    
    # Nettoyer le fichier temporaire
    rm -f /tmp/core_modified.py
fi

echo "✅ Configuration des interfaces et de l'injection de dépendances terminée!"
echo "🧪 Exécutez maintenant test-circular-imports.sh pour vérifier si les problèmes ont été résolus."
