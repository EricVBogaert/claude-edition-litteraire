Voici le contenu pour le fichier `claude_edition_litteraire/structure/fixer.py` :

```python
# claude_edition_litteraire/structure/fixer.py
"""
Module de correction automatique des problèmes de structure.
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable, Tuple

from ..utils.logging import get_logger

logger = get_logger(__name__)

def fix_missing_dirs(
    project_path: Union[str, Path], 
    issues: List[Dict[str, Any]]
) -> int:
    """
    Crée les répertoires manquants identifiés dans les problèmes.
    
    Args:
        project_path: Chemin de base du projet
        issues: Liste des problèmes détectés
        
    Returns:
        Nombre de répertoires créés
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    dirs_created = 0
    for issue in issues:
        if issue['level'] == 'error' and issue['type'] == 'missing_required' and '.md' not in issue['path']:
            try:
                # C'est un répertoire manquant
                dir_path = project_path / issue['path']
                if not dir_path.exists():
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"Répertoire créé: {dir_path}")
                    dirs_created += 1
            except Exception as e:
                logger.error(f"Erreur lors de la création du répertoire {issue['path']}: {e}")
    
    return dirs_created

def fix_missing_files(
    project_path: Union[str, Path], 
    issues: List[Dict[str, Any]],
    templates: Optional[Dict[str, str]] = None
) -> int:
    """
    Crée les fichiers manquants identifiés dans les problèmes.
    
    Args:
        project_path: Chemin de base du projet
        issues: Liste des problèmes détectés
        templates: Dictionnaire des templates à utiliser par type de fichier
        
    Returns:
        Nombre de fichiers créés
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    if templates is None:
        templates = {
            'index.md': """# {title}

## Vue d'ensemble
Ce document sert d'index pour {directory}.

## Contenu
<!-- Liste des contenus principaux de cette section -->

## Navigation rapide
<!-- Liens vers les documents principaux -->
""",
            'default.md': """# {title}

*Document créé automatiquement le {date}*

## Contenu à définir
Ce document a été créé automatiquement pour corriger la structure du projet.
Veuillez le compléter avec le contenu approprié.
"""
        }
    
    files_created = 0
    for issue in issues:
        if issue['level'] == 'error' and issue['type'] == 'missing_required' and '.md' in issue['path']:
            try:
                # C'est un fichier manquant
                file_path = project_path / issue['path']
                
                # S'assurer que le répertoire parent existe
                os.makedirs(file_path.parent, exist_ok=True)
                
                # Déterminer le template à utiliser
                template_key = os.path.basename(issue['path'])
                if template_key not in templates:
                    template_key = 'default.md'
                
                # Préparer les variables pour le template
                title = os.path.splitext(os.path.basename(issue['path']))[0].replace('-', ' ').title()
                directory = os.path.basename(os.path.dirname(issue['path']))
                date = datetime.now().strftime('%Y-%m-%d')
                
                # Créer le contenu avec les variables
                content = templates[template_key].format(
                    title=title,
                    directory=directory,
                    date=date
                )
                
                # Écrire le fichier
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Fichier créé: {file_path}")
                files_created += 1
            except Exception as e:
                logger.error(f"Erreur lors de la création du fichier {issue['path']}: {e}")
    
    return files_created

def create_missing_file(
    project_path: Union[str, Path], 
    file_path: str, 
    template_name: Optional[str] = None,
    template_content: Optional[str] = None,
    variables: Optional[Dict[str, str]] = None
) -> bool:
    """
    Crée un fichier manquant à partir d'un template.
    
    Args:
        project_path: Chemin de base du projet
        file_path: Chemin relatif du fichier à créer
        template_name: Nom du template à utiliser
        template_content: Contenu du template si pas de nom de template
        variables: Variables à remplacer dans le template
        
    Returns:
        True si le fichier a été créé, False sinon
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    # Chemin complet du fichier à créer
    full_path = project_path / file_path
    
    # S'assurer que le répertoire parent existe
    os.makedirs(full_path.parent, exist_ok=True)
    
    # Si le fichier existe déjà, ne pas l'écraser
    if full_path.exists():
        logger.warning(f"Le fichier existe déjà et ne sera pas écrasé: {full_path}")
        return False
    
    # Obtenir le contenu du template
    content = ""
    
    if template_content:
        content = template_content
    elif template_name:
        # Chercher le template dans le dossier templates
        template_path = project_path / "templates" / template_name
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            logger.warning(f"Template non trouvé: {template_path}")
            return False
    else:
        # Template par défaut
        title = os.path.splitext(os.path.basename(file_path))[0].replace('-', ' ').title()
        content = f"""# {title}

*Document créé automatiquement le {datetime.now().strftime('%Y-%m-%d')}*

## Contenu à définir
Ce document a été créé automatiquement.
Veuillez le compléter avec le contenu approprié.
"""
    
    # Remplacer les variables si fournies
    if variables:
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", value)
    
    # Écrire le fichier
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Fichier créé: {full_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la création du fichier {full_path}: {e}")
        return False

def find_similar_files(
    project_path: Union[str, Path], 
    broken_link: str
) -> List[Tuple[str, float]]:
    """
    Recherche des fichiers similaires au lien cassé dans le projet.
    
    Args:
        project_path: Chemin de base du projet
        broken_link: Lien cassé à rechercher
        
    Returns:
        Liste de fichiers similaires trouvés [(chemin, score_similitude)]
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    # Extraire le nom de fichier sans le chemin
    link_parts = broken_link.split('/')
    filename = link_parts[-1]
    
    # Si le nom de fichier contient une extension, la conserver, sinon ajouter .md
    if '.' not in filename:
        filename += '.md'
    
    # Rechercher des fichiers avec le même nom dans tout le projet
    similar_files = []
    for file_path in project_path.glob(f'**/{filename}'):
        # Ignorer les fichiers dans .git, export, etc.
        if any(part.startswith('.') for part in file_path.parts) or 'export' in file_path.parts:
            continue
        
        rel_path = file_path.relative_to(project_path)
        # Calculer un score de similarité simple
        similarity = 0.8  # Score de base pour le même nom de fichier
        
        # Bonus pour les parties de chemin correspondantes
        rel_parts = str(rel_path).split(os.sep)
        link_parts = broken_link.split('/')
        common_parts = set(rel_parts) & set(link_parts)
        if common_parts:
            similarity += 0.1 * len(common_parts)
        
        similar_files.append((str(rel_path), similarity))
    
    return sorted(similar_files, key=lambda x: x[1], reverse=True)

def detect_common_path_issues(issues: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Détecte les problèmes de chemin communs (par exemple, préfixe 'docs/' incorrect).
    
    Args:
        issues: Liste des problèmes de liens cassés
        
    Returns:
        Dictionnaire des motifs de préfixe détectés et leur fréquence
    """
    prefix_patterns = {}
    
    for issue in issues:
        if issue['type'] != 'broken_link':
            continue
        
        path = issue['message'].split("'")[1]  # Extraire le chemin du message
        
        # Détecter les préfixes communs
        parts = path.split('/')
        if len(parts) > 1:
            prefix = parts[0]
            if prefix not in prefix_patterns:
                prefix_patterns[prefix] = 0
            prefix_patterns[prefix] += 1
    
    return prefix_patterns

def suggest_prefix_replacements(
    prefix_patterns: Dict[str, int], 
    project_path: Union[str, Path]
) -> Dict[str, str]:
    """
    Suggère des remplacements pour les préfixes problématiques.
    
    Args:
        prefix_patterns: Dictionnaire des motifs de préfixe et leur fréquence
        project_path: Chemin de base du projet
        
    Returns:
        Dictionnaire des suggestions de remplacement de préfixe
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    suggestions = {}
    
    # Vérifier les dossiers de premier niveau du projet
    root_dirs = [d.name for d in project_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    for prefix, count in prefix_patterns.items():
        if count > 5:  # Seuil arbitraire pour considérer un motif comme significatif
            # Chercher un dossier similaire
            best_match = None
            best_score = 0
            
            for dir_name in root_dirs:
                # Score simple basé sur les caractères communs
                score = sum(1 for a, b in zip(prefix, dir_name) if a == b) / max(len(prefix), len(dir_name))
                if score > 0.5 and score > best_score:  # Seuil arbitraire de similarité
                    best_match = dir_name
                    best_score = score
            
            if best_match:
                suggestions[prefix] = best_match
    
    return suggestions

def fix_broken_links(
    project_path: Union[str, Path], 
    issues: List[Dict[str, Any]], 
    interactive: bool = True
) -> int:
    """
    Corrige les liens cassés simples (renommages, changements de casse, etc.)
    
    Args:
        project_path: Chemin de base du projet
        issues: Liste des problèmes détectés
        interactive: Demander confirmation pour chaque fichier modifié
        
    Returns:
        Nombre de liens corrigés
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    links_fixed = 0
    
    # Collecter tous les fichiers markdown existants pour rechercher les correspondances
    existing_files = {}
    for md_file in project_path.glob('**/*.md'):
        if any(part.startswith('.') for part in md_file.parts) or 'export' in md_file.parts:
            continue
        
        relative_path = md_file.relative_to(project_path)
        str_path = str(relative_path)
        
        # Ajouter le chemin complet
        existing_files[str_path.lower()] = str_path
        # Ajouter aussi sans extension .md
        existing_files[str_path[:-3].lower()] = str_path[:-3]
    
    # Filtrer les problèmes de liens cassés
    broken_link_issues = [issue for issue in issues if issue['type'] == 'broken_link']
    
    if not broken_link_issues:
        return 0
    
    # Détecter les problèmes de préfixe communs
    prefix_patterns = detect_common_path_issues(broken_link_issues)
    prefix_suggestions = suggest_prefix_replacements(prefix_patterns, project_path)
    
    if prefix_suggestions and interactive:
        print("\nCorrections de préfixe suggérées:")
        for prefix, suggestion in prefix_suggestions.items():
            print(f"  '{prefix}/' → '{suggestion}/' ({prefix_patterns[prefix]} occurrences)")
        
        apply_all = input("\nAppliquer toutes ces corrections de préfixe? [Y/n/s(elect)]: ").strip().lower()
        
        if apply_all == 's' or apply_all == 'select':
            # Mode sélection individuelle
            approved_prefixes = {}
            for prefix, suggestion in prefix_suggestions.items():
                approval = input(f"  Remplacer '{prefix}/' par '{suggestion}/'? [Y/n]: ").strip().lower()
                if not approval or approval in ('y', 'yes', 'oui'):
                    approved_prefixes[prefix] = suggestion
            prefix_suggestions = approved_prefixes
        elif apply_all and apply_all not in ('y', 'yes', 'oui'):
            prefix_suggestions = {}  # Annuler toutes les suggestions
    
    # Traiter chaque fichier contenant des liens cassés
    processed_files = set()
    for issue in broken_link_issues:
        file_path = project_path / issue['path']
        
        if str(file_path) in processed_files:
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraire le lien cassé du message
            broken_link = issue['message'].split("'")[1]
            
            # Chercher des fichiers similaires
            similar_files = find_similar_files(project_path, broken_link)
            
            # Appliquer les corrections
            new_content = content
            link_fixed = False
            
            # 1. Correction par préfixe si applicable
            prefix = broken_link.split('/')[0] if '/' in broken_link else ""
            if prefix in prefix_suggestions:
                replacement = prefix_suggestions[prefix]
                # Remplacer dans les liens markdown et wiki
                new_content = replace_prefix_in_links(new_content, prefix, replacement)
                link_fixed = new_content != content
            
            # 2. Correction par similarité si pas de correction par préfixe
            if not link_fixed and similar_files:
                best_match = similar_files[0][0]
                
                if interactive:
                    print(f"\nPour le lien '{broken_link}' dans {issue['path']}:")
                    print(f"  Meilleure correspondance: {best_match} (score: {similar_files[0][1]:.2f})")
                    approval = input("  Remplacer par cette correspondance? [Y/n]: ").strip().lower()
                    
                    if approval and approval not in ('y', 'yes', 'oui'):
                        continue
                
                # Remplacer le lien dans le contenu
                new_content = replace_link_in_content(new_content, broken_link, best_match)
                link_fixed = new_content != content
            
            # Sauvegarder les modifications si des liens ont été corrigés
            if link_fixed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                links_fixed += 1
                logger.info(f"Liens corrigés dans {file_path}")
            
            processed_files.add(str(file_path))
        except Exception as e:
            logger.error(f"Erreur lors de la correction des liens dans {file_path}: {e}")
    
    return links_fixed

def replace_prefix_in_links(content: str, old_prefix: str, new_prefix: str) -> str:
    """
    Remplace un préfixe dans tous les liens markdown et wiki du contenu.
    
    Args:
        content: Contenu à modifier
        old_prefix: Ancien préfixe
        new_prefix: Nouveau préfixe
        
    Returns:
        Contenu modifié
    """
    # Remplacer dans les liens markdown: [text](old_prefix/...)
    md_pattern = r'\[.*?\]\((' + re.escape(old_prefix) + r'/[^)]*)\)'
    content = re.sub(md_pattern, lambda m: m.group(0).replace(
        m.group(1), m.group(1).replace(old_prefix + '/', new_prefix + '/', 1)), content)
    
    # Remplacer dans les liens wiki: [[old_prefix/...|...]]
    wiki_pattern = r'\[\[(' + re.escape(old_prefix) + r'/[^\]|]*)((?:\|[^\]]*)?)\]\]'
    content = re.sub(wiki_pattern, lambda m: m.group(0).replace(
        m.group(1), m.group(1).replace(old_prefix + '/', new_prefix + '/', 1)), content)
    
    return content

def replace_link_in_content(content: str, old_link: str, new_link: str) -> str:
    """
    Remplace un lien spécifique dans le contenu markdown.
    
    Args:
        content: Contenu à modifier
        old_link: Ancien lien
        new_link: Nouveau lien
        
    Returns:
        Contenu modifié
    """
    # Remplacer dans les liens markdown: [text](old_link)
    md_pattern = r'\[([^\]]*)\]\(' + re.escape(old_link) + r'(?:\.md)?\)'
    content = re.sub(md_pattern, r'[\1](' + new_link + r')', content)
    
    # Remplacer dans les liens wiki: [[old_link|text]]
    wiki_pattern = r'\[\[' + re.escape(old_link) + r'(\|[^\]]+)?\]\]'
    
    def wiki_replacer(match):
        pipe_part = match.group(1) if match.group(1) else ''
        return f'[[{new_link}{pipe_part}]]'
    
    content = re.sub(wiki_pattern, wiki_replacer, content)
    
    return content
```