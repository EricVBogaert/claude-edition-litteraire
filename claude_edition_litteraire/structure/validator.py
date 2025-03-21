"""
Module pour la validation de structure d'un projet littéraire.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ..utils.logging import get_logger

logger = get_logger(__name__)

# Structure attendue du projet basée sur le guide complet
DEFAULT_EXPECTED_STRUCTURE = {
    'index.md': {'type': 'file', 'required': True},
    'README.md': {'type': 'file', 'required': True},
    'chapitres': {'type': 'dir', 'required': True},
    'structure': {
        'type': 'dir', 
        'required': True,
        'children': {
            'plan-general.md': {'type': 'file', 'required': True},
            'arcs-narratifs.md': {'type': 'file', 'required': False},
            'chronologie.md': {'type': 'file', 'required': False},
            'personnages.md': {'type': 'file', 'required': True},
            'univers.md': {'type': 'file', 'required': True}
        }
    },
    'personnages': {
        'type': 'dir', 
        'required': True,
        'children': {
            'index.md': {'type': 'file', 'required': True},
            'entites': {'type': 'dir', 'required': False},
            'manifestations': {'type': 'dir', 'required': False},
            'mortels': {'type': 'dir', 'required': False},
            'secondaires': {'type': 'dir', 'required': False}
        }
    },
    'lieux': {
        'type': 'dir', 
        'required': False,
        'children': {
            'reels': {'type': 'dir', 'required': False},
            'fictifs': {'type': 'dir', 'required': False}
        }
    },
    'concepts': {'type': 'dir', 'required': False},
    'references': {
        'type': 'dir', 
        'required': True,
        'children': {
            'index.md': {'type': 'file', 'required': True}
        }
    },
    'styles': {
        'type': 'dir', 
        'required': False,
        'children': {
            'index.md': {'type': 'file', 'required': False},
            'registres': {'type': 'dir', 'required': False}
        }
    },
    'ressources': {'type': 'dir', 'required': True},
    'claude-sessions': {'type': 'dir', 'required': True},
    'templates': {'type': 'dir', 'required': True},
    'export': {'type': 'dir', 'required': True},
    'automation': {
        'type': 'dir', 
        'required': True,
        'children': {
            'scripts': {
                'type': 'dir',
                'required': True,
                'children': {
                    'python': {'type': 'dir', 'required': True},
                    'bash': {'type': 'dir', 'required': False},
                    'js': {'type': 'dir', 'required': False}
                }
            },
            'config': {'type': 'dir', 'required': True},
            'templates': {'type': 'dir', 'required': True},
            'hooks': {'type': 'dir', 'required': False},
            'docs': {'type': 'dir', 'required': True}
        }
    },
    'review': {
        'type': 'dir', 
        'required': True,
        'children': {
            'pending': {'type': 'dir', 'required': True},
            'in_progress': {'type': 'dir', 'required': True},
            'completed': {'type': 'dir', 'required': True},
            'claude_suggestions': {'type': 'dir', 'required': True},
            'templates': {'type': 'dir', 'required': False}
        }
    },
    'media': {'type': 'dir', 'required': True}
}

# Templates attendus
DEFAULT_EXPECTED_TEMPLATES = {
    'personnage-avance.md': {'required': True},
    'chapitre.md': {'required': True},
    'scene.md': {'required': False},
    'reference.md': {'required': True},
    'todo.md': {'required': True},
    'gantt.md': {'required': False},
    'intervenant.md': {'required': True}
}

# Règles pour les frontmatter YAML par type de document
DEFAULT_FRONTMATTER_RULES = {
    'personnages/.*': {
        'required_fields': ['nom', 'tags'],
        'recommended_fields': ['citation', 'expertise'],
        'valid_tags': ['personnage', 'entite', 'mortel', 'manifestation', 'secondaire']
    },
    'review/.*todo.*\.md': {
        'required_fields': ['id', 'titre', 'statut', 'priorite', 'date_creation'],
        'recommended_fields': ['date_debut', 'date_fin', 'tags'],
        'valid_tags': ['tâche']
    }
}

def validate_structure(
    project_path: Union[str, Path], 
    expected_structure: Optional[Dict] = None, 
    path: str = "", 
    issues: Optional[List] = None
) -> List[Dict[str, Any]]:
    """
    Valide récursivement la structure du projet selon la définition attendue.
    
    Args:
        project_path: Chemin de base du projet
        expected_structure: Structure attendue pour ce niveau, utilise la structure par défaut si None
        path: Chemin relatif actuel (pour le logging)
        issues: Liste pour accumuler les problèmes détectés
        
    Returns:
        Liste des problèmes détectés
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    if expected_structure is None:
        expected_structure = DEFAULT_EXPECTED_STRUCTURE
    
    if issues is None:
        issues = []
    
    for name, details in expected_structure.items():
        current_path = os.path.join(path, name)
        full_path = project_path / current_path
        
        # Vérifier l'existence de l'élément
        if not full_path.exists():
            if details.get('required', False):
                issues.append({
                    'level': 'error',
                    'type': 'missing_required',
                    'path': current_path,
                    'message': f"Élément requis manquant: {current_path}"
                })
            else:
                issues.append({
                    'level': 'warning',
                    'type': 'missing_optional',
                    'path': current_path,
                    'message': f"Élément recommandé manquant: {current_path}"
                })
            continue
        
        # Vérifier le type (fichier/dossier)
        expected_type = details['type']
        is_dir = full_path.is_dir()
        actual_type = 'dir' if is_dir else 'file'
        
        if expected_type != actual_type:
            issues.append({
                'level': 'error',
                'type': 'type_mismatch',
                'path': current_path,
                'message': f"Type incorrect pour {current_path}: attendu {expected_type}, trouvé {actual_type}"
            })
            continue
        
        # Si c'est un dossier avec une structure interne définie, vérifier récursivement
        if is_dir and 'children' in details:
            validate_structure(project_path, details['children'], current_path, issues)
    
    return issues

def validate_templates(
    project_path: Union[str, Path], 
    expected_templates: Optional[Dict] = None,
    issues: Optional[List] = None
) -> List[Dict[str, Any]]:
    """
    Vérifie l'existence des templates requis.
    
    Args:
        project_path: Chemin de base du projet
        expected_templates: Dictionnaire des templates attendus, utilise la liste par défaut si None
        issues: Liste pour accumuler les problèmes détectés
        
    Returns:
        Liste des problèmes détectés
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    if expected_templates is None:
        expected_templates = DEFAULT_EXPECTED_TEMPLATES
    
    if issues is None:
        issues = []
    
    templates_dir = project_path / 'templates'
    if not templates_dir.exists() or not templates_dir.is_dir():
        issues.append({
            'level': 'error',
            'type': 'missing_templates_dir',
            'path': 'templates',
            'message': "Le dossier templates est manquant"
        })
        return issues
    
    for template_name, details in expected_templates.items():
        template_path = templates_dir / template_name
        if not template_path.exists():
            level = 'error' if details.get('required', False) else 'warning'
            issues.append({
                'level': level,
                'type': 'missing_template',
                'path': f"templates/{template_name}",
                'message': f"Template {template_name} manquant"
            })
    
    return issues

def extract_frontmatter(file_path: Union[str, Path]) -> tuple:
    """
    Extrait le frontmatter YAML d'un fichier markdown.
    
    Args:
        file_path: Chemin du fichier
        
    Returns:
        tuple: (frontmatter_dict, content_str) ou (None, content_str) si pas de frontmatter
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher le frontmatter délimité par ---
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not frontmatter_match:
        return None, content
    
    frontmatter_str = frontmatter_match.group(1)
    remaining_content = content[frontmatter_match.end():]
    
    try:
        frontmatter_dict = yaml.safe_load(frontmatter_str)
        return frontmatter_dict, remaining_content
    except yaml.YAMLError:
        # En cas d'erreur de parsing, retourner l'erreur
        raise ValueError(f"YAML invalide dans le frontmatter: {frontmatter_str}")

def validate_frontmatter(
    project_path: Union[str, Path], 
    frontmatter_rules: Optional[Dict] = None,
    issues: Optional[List] = None
) -> List[Dict[str, Any]]:
    """
    Vérifie les frontmatter YAML des fichiers markdown selon les règles définies.
    
    Args:
        project_path: Chemin de base du projet
        frontmatter_rules: Règles pour les frontmatter, utilise les règles par défaut si None
        issues: Liste pour accumuler les problèmes détectés
        
    Returns:
        Liste des problèmes détectés
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    if frontmatter_rules is None:
        frontmatter_rules = DEFAULT_FRONTMATTER_RULES
    
    if issues is None:
        issues = []
    
    # Parcourir tous les fichiers markdown du projet
    for md_file in project_path.glob('**/*.md'):
        # Ignorer les fichiers dans .git, export, etc.
        if any(part.startswith('.') for part in md_file.parts) or 'export' in md_file.parts:
            continue
        
        relative_path = md_file.relative_to(project_path)
        str_path = str(relative_path)
        
        # Vérifier si ce fichier correspond à une règle de frontmatter
        matching_rules = []
        for pattern, rules in frontmatter_rules.items():
            if re.match(pattern, str_path):
                matching_rules.append(rules)
        
        if not matching_rules:
            continue  # Aucune règle spécifique pour ce fichier
        
        # Extraire le frontmatter
        try:
            frontmatter, _ = extract_frontmatter(md_file)
            
            if frontmatter is None:
                issues.append({
                    'level': 'warning',
                    'type': 'missing_frontmatter',
                    'path': str_path,
                    'message': f"Frontmatter YAML manquant dans {str_path}"
                })
                continue
            
            # Vérifier les champs requis et recommandés selon les règles
            for rules in matching_rules:
                for field in rules.get('required_fields', []):
                    if field not in frontmatter:
                        issues.append({
                            'level': 'error',
                            'type': 'missing_required_field',
                            'path': str_path,
                            'message': f"Champ requis manquant dans {str_path}: {field}"
                        })
                
                for field in rules.get('recommended_fields', []):
                    if field not in frontmatter:
                        issues.append({
                            'level': 'warning',
                            'type': 'missing_recommended_field',
                            'path': str_path,
                            'message': f"Champ recommandé manquant dans {str_path}: {field}"
                        })
                
                # Vérifier les tags si définis
                if 'tags' in frontmatter and 'valid_tags' in rules:
                    tags = frontmatter['tags']
                    if isinstance(tags, str):
                        # Certains fichiers pourraient avoir les tags comme une chaîne
                        tags = [tag.strip() for tag in tags.split(',')]
                    
                    valid_tags = rules['valid_tags']
                    if not any(tag in valid_tags for tag in tags):
                        issues.append({
                            'level': 'warning',
                            'type': 'invalid_tags',
                            'path': str_path,
                            'message': f"Aucun tag valide trouvé dans {str_path}. Tags attendus: {', '.join(valid_tags)}"
                        })
        
        except Exception as e:
            issues.append({
                'level': 'error',
                'type': 'frontmatter_parsing_error',
                'path': str_path,
                'message': f"Erreur lors de l'analyse du frontmatter dans {str_path}: {str(e)}"
            })
    
    return issues

def check_broken_links(
    project_path: Union[str, Path], 
    issues: Optional[List] = None
) -> List[Dict[str, Any]]:
    """
    Vérifie les liens internes cassés dans les fichiers markdown.
    
    Args:
        project_path: Chemin de base du projet
        issues: Liste pour accumuler les problèmes détectés
        
    Returns:
        Liste des problèmes détectés
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    if issues is None:
        issues = []
    
    # Collecter tous les fichiers markdown existants
    existing_files = set()
    for md_file in project_path.glob('**/*.md'):
        if any(part.startswith('.') for part in md_file.parts) or 'export' in md_file.parts:
            continue
        
        relative_path = md_file.relative_to(project_path)
        existing_files.add(str(relative_path))
        # Ajouter aussi sans extension .md
        existing_files.add(str(relative_path)[:-3])
    
    # Vérifier les liens dans chaque fichier
    for md_file in project_path.glob('**/*.md'):
        if any(part.startswith('.') for part in md_file.parts) or 'export' in md_file.parts:
            continue
        
        relative_path = md_file.relative_to(project_path)
        str_path = str(relative_path)
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher les liens wiki [[lien]]
        wiki_links = re.findall(r'\[\[(.*?)(?:\|.*?)?\]\]', content)
        
        # Rechercher les liens markdown [texte](lien)
        md_links = re.findall(r'\[.*?\]\((.*?)\)', content)
        
        # Vérifier tous les liens
        all_links = wiki_links + md_links
        for link in all_links:
            # Ignorer les liens externes et les ancres
            if link.startswith(('http://', 'https://', '#')):
                continue
            
            # Normaliser le lien
            link = link.split('#')[0]  # Enlever les ancres
            
            # Si le lien est relatif au dossier courant du fichier
            if not link.startswith('/'):
                current_dir = os.path.dirname(str_path)
                link = os.path.normpath(os.path.join(current_dir, link))
            else:
                # Enlever le / initial pour les chemins absolus dans le projet
                link = link.lstrip('/')
            
            # Vérifier si le fichier cible existe
            if link and link not in existing_files and link + '.md' not in existing_files:
                issues.append({
                    'level': 'warning',
                    'type': 'broken_link',
                    'path': str_path,
                    'message': f"Lien cassé dans {str_path}: '{link}'"
                })
    
    return issues