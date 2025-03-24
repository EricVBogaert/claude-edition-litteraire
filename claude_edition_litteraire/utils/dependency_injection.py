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
