"""
Module pour l'interaction unifiée avec différents modèles de langage (LLMs).

Ce module fournit une abstraction pour interagir avec différentes 
APIs de modèles de langage, comme Claude, GPT, etc.
"""

from .unified_llm import UnifiedLLM

__all__ = ["UnifiedLLM"]
