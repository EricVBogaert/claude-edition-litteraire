# claude_edition_litteraire/llm/__init__.py
"""
Module pour l'interaction unifiée avec différents modèles de langage (LLMs).

Ce module fournit une abstraction pour interagir avec différentes 
APIs de modèles de langage, comme Claude, LMStudio, etc.
"""

from .unified_llm import UnifiedLLM

__all__ = ["UnifiedLLM"]