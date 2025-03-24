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
