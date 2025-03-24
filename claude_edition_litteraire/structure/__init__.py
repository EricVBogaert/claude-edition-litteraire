"""
Module de validation et correction de structure pour un projet littéraire.

Ce module fournit des outils pour vérifier et corriger la structure
d'un projet d'édition littéraire, en détectant les dossiers manquants,
les fichiers requis, les liens cassés, etc.
"""

from .validator import validate_structure, validate_templates, validate_frontmatter, check_broken_links
from .fixer import fix_missing_dirs, fix_missing_files, fix_broken_links, create_missing_file
from .reporter import generate_structure_report, generate_correction_plan, group_issues_by_pattern
from .project_structure import ProjectStructure

__all__ = [
    "ProjectStructure",
    "validate_structure",
    "validate_templates",
    "validate_frontmatter",
    "check_broken_links",
    "fix_missing_dirs",
    "fix_missing_files",
    "fix_broken_links",
    "create_missing_file",
    "generate_structure_report",
    "generate_correction_plan",
    "group_issues_by_pattern"
]