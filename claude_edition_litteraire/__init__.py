"""
claude_edition_litteraire - Bibliothèque pour l'édition littéraire assistée par IA

Ce package offre des outils pour gérer un projet d'édition littéraire, 
avec validation de structure, correction automatique, et intégration avec l'API Claude.
"""

__version__ = "0.1.0"

from .core import Project
from . import structure
from . import content
from . import automation
from . import claude
from . import utils

__all__ = [
    "Project",
    "structure",
    "content",
    "automation", 
    "claude",
    "utils"
]