#!/bin/bash
# fix-imports-utils.sh
# Utilitaires pour résoudre les problèmes d'imports circulaires

# Fonction pour convertir un import au niveau module en import tardif dans une méthode
make_lazy_import() {
    local file=$1
    local module_to_import=$2
    local class_to_import=$3
    
    echo "🔄 Conversion des imports en imports tardifs dans $file..."
    
    # Sauvegarde du fichier
    cp "$file" "${file}.bak"
    
    # Supprimer l'import au niveau du module
    sed -i "/from $module_to_import import $class_to_import/d" "$file"
    
    # Chercher les méthodes qui utilisent la classe importée
    if grep -q "$class_to_import" "$file"; then
        # Ajouter l'import tardif dans chaque méthode où la classe est utilisée
        methods=$(grep -n "def " "$file" | cut -d: -f1)
        
        for line in $methods; do
            # Vérifier si la méthode utilise la classe
            method_end=$(tail -n +$line "$file" | grep -n "^    def \|^class \|^$" | head -n 1 | cut -d: -f1)
            if [ -z "$method_end" ]; then
                method_end=$(wc -l < "$file")
            else
                method_end=$((line + method_end - 1))
            fi
            
            method_content=$(sed -n "${line},${method_end}p" "$file")
            if echo "$method_content" | grep -q "$class_to_import"; then
                # Déterminer l'indentation
                indent=$(grep "def " <<< "$method_content" | sed 's/\([ ]*\).*/\1/')
                
                # Insérer l'import local au début de la méthode, après la ligne de def et docstring
                after_doc=$(echo "$method_content" | grep -n '"""' | head -n 2 | tail -n 1 | cut -d: -f1)
                if [ -n "$after_doc" ] && [ "$after_doc" -gt 1 ]; then
                    insert_line=$((line + after_doc))
                else
                    # Pas de docstring, trouver la première ligne après la définition
                    first_line=$(echo "$method_content" | grep -n "def " | cut -d: -f1)
                    insert_line=$((line + first_line))
                fi
                
                sed -i "${insert_line}a\\${indent}    # Import tardif pour éviter les imports circulaires\\${indent}    from $module_to_import import $class_to_import" "$file"
                echo "  ➕ Import tardif ajouté dans une méthode à la ligne $insert_line"
            fi
        done
    fi
}

# Fonction pour créer une interface abstraite
create_abstract_interface() {
    local module_name=$1
    local class_name=$2
    local methods=$3
    local output_file=$4
    
    echo "🏗️ Création de l'interface abstraite pour $class_name dans $output_file..."
    
    # Créer le contenu de l'interface
    cat > "$output_file" << EOF
"""
Interface abstraite pour $class_name.
Ce fichier a été généré automatiquement pour résoudre des problèmes d'imports circulaires.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

class ${class_name}Interface(ABC):
    """Interface abstraite pour $class_name."""
    
EOF
    
    # Ajouter les méthodes abstraites
    IFS=','
    for method in $methods; do
        IFS='|' read -r name params return_type <<< "$method"
        cat >> "$output_file" << EOF
    @abstractmethod
    def $name($params) -> $return_type:
        """
        Méthode abstraite pour $name.
        
        Args:
            ${params/self, /}
            
        Returns:
            $return_type
        """
        pass
        
EOF
    done
    
    echo "✅ Interface créée avec succès!"
}

# Fonction pour restructurer un fichier en utilisant une interface
use_interface() {
    local file=$1
    local class_name=$2
    local interface_module=$3
    
    echo "🔄 Adaptation de $file pour utiliser l'interface $interface_module..."
    
    # Sauvegarde du fichier
    cp "$file" "${file}.bak"
    
    # Ajouter l'import de l'interface
    sed -i "1i from $interface_module import ${class_name}Interface" "$file"
    
    # Modifier la définition de classe pour hériter de l'interface
    sed -i "s/class $class_name:/class $class_name(${class_name}Interface):/g" "$file"
    
    echo "✅ Adaptation terminée!"
}

# Fonction pour créer un module d'injection de dépendances
create_dependency_injection() {
    local output_file=$1
    
    echo "🏗️ Création du module d'injection de dépendances dans $output_file..."
    
    cat > "$output_file" << EOF
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

    echo "✅ Module d'injection de dépendances créé avec succès!"
}

# Fonction pour adapter Project pour utiliser l'injection de dépendances
adapt_project_for_di() {
    local file=$1
    
    echo "🔄 Adaptation de Project pour utiliser l'injection de dépendances..."
    
    # Sauvegarde du fichier
    cp "$file" "${file}.bak"
    
    # Ajouter l'import du ServiceProvider
    sed -i '/^from/i from .utils.dependency_injection import get_service_provider' "$file"
    
    # Modifier le constructeur pour utiliser l'injection
    # Cette partie est compliquée et nécessite un traitement plus spécifique
    # On va juste ajouter un commentaire pour guider les modifications manuelles
    sed -i '/def __init__/a\\        # TODO: Utiliser l\'injection de dépendances pour initialiser les composants\\        # provider = get_service_provider()' "$file"
    
    echo "✅ Adaptation initiée - certaines modifications devront être complétées manuellement."
}

# Afficher l'aide si aucun argument n'est fourni
if [ $# -eq 0 ]; then
    echo "Utilitaires pour résoudre les problèmes d'imports circulaires"
    echo ""
    echo "Usage:"
    echo "  $0 lazy_import <file> <module_to_import> <class_to_import>"
    echo "  $0 create_interface <module_name> <class_name> <methods> <output_file>"
    echo "  $0 use_interface <file> <class_name> <interface_module>"
    echo "  $0 create_di <output_file>"
    echo "  $0 adapt_project <file>"
    echo ""
    echo "Exemples:"
    echo "  $0 lazy_import ./claude_edition_litteraire/core.py claude.manager ClaudeManager"
    echo "  $0 create_interface claude_edition_litteraire.llm LLMProvider \"chat|self,messages,max_tokens=1000,temperature=0.7,stream=False|str\" ./claude_edition_litteraire/llm/interfaces.py"
    echo "  $0 use_interface ./claude_edition_litteraire/llm/unified_llm.py UnifiedLLM claude_edition_litteraire.llm.interfaces"
    echo "  $0 create_di ./claude_edition_litteraire/utils/dependency_injection.py"
    echo "  $0 adapt_project ./claude_edition_litteraire/core.py"
    exit 1
fi

# Traiter les arguments
command=$1
shift

case $command in
    lazy_import)
        make_lazy_import "$1" "$2" "$3"
        ;;
    create_interface)
        create_abstract_interface "$1" "$2" "$3" "$4"
        ;;
    use_interface)
        use_interface "$1" "$2" "$3"
        ;;
    create_di)
        create_dependency_injection "$1"
        ;;
    adapt_project)
        adapt_project_for_di "$1"
        ;;
    *)
        echo "Commande inconnue: $command"
        exit 1
        ;;
esac
