"""
Classe principale pour la gestion du contenu d'un projet littéraire.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ..utils.logging import get_logger

logger = get_logger(__name__)

class ContentManager:
    """
    Gère le contenu textuel d'un projet littéraire.
    
    Cette classe fournit des méthodes pour accéder, analyser et manipuler
    le contenu des chapitres, personnages et autres éléments narratifs.
    """
    
    def __init__(self, project):
        """
        Initialise l'instance ContentManager.
        
        Args:
            project: Instance de la classe Project parente
        """
        self.project = project
        self.path = project.path
        self.config = project.config
        logger.debug(f"ContentManager initialisé pour: {self.path}")
    
    def validate(self) -> List[Dict[str, Any]]:
        """
        Valide le contenu du projet (cohérence, qualité, etc.)
        
        Returns:
            Liste des problèmes détectés
        """
        logger.info(f"Validation du contenu pour: {self.path}")
        issues = []
        
        # Vérifier les chapitres
        chapters_dir = self.path / "chapitres"
        if chapters_dir.exists():
            issues.extend(self._validate_chapters(chapters_dir))
        
        # Vérifier les personnages
        characters_dir = self.path / "personnages"
        if characters_dir.exists():
            issues.extend(self._validate_characters(characters_dir))
        
        # Autres validations possibles:
        # - Cohérence des références entre documents
        # - Qualité linguistique (avec outils externes)
        # - Vérification narrative (chronologie, POV, etc.)
        
        return issues
    
    def _validate_chapters(self, chapters_dir: Path) -> List[Dict[str, Any]]:
        """
        Valide les fichiers de chapitres.
        
        Args:
            chapters_dir: Chemin du répertoire de chapitres
            
        Returns:
            Liste des problèmes détectés
        """
        issues = []
        
        # Parcourir tous les fichiers de chapitre
        for chapter_file in chapters_dir.glob("**/*.md"):
            try:
                # Lire le contenu du chapitre
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraire les métadonnées (frontmatter)
                frontmatter, content_text = self._extract_frontmatter(chapter_file)
                
                # Vérifier les métadonnées requises
                if frontmatter:
                    if 'titre' not in frontmatter:
                        issues.append({
                            'level': 'warning',
                            'type': 'missing_chapter_title',
                            'path': str(chapter_file.relative_to(self.path)),
                            'message': "Le titre du chapitre est manquant dans les métadonnées"
                        })
                    
                    if 'statut' not in frontmatter:
                        issues.append({
                            'level': 'info',
                            'type': 'missing_chapter_status',
                            'path': str(chapter_file.relative_to(self.path)),
                            'message': "Le statut du chapitre n'est pas défini"
                        })
                else:
                    issues.append({
                        'level': 'warning',
                        'type': 'missing_frontmatter',
                        'path': str(chapter_file.relative_to(self.path)),
                        'message': "Métadonnées frontmatter manquantes pour ce chapitre"
                    })
                
                # Vérifier la structure du chapitre
                if not re.search(r'^# ', content, re.MULTILINE):
                    issues.append({
                        'level': 'warning',
                        'type': 'missing_chapter_heading',
                        'path': str(chapter_file.relative_to(self.path)),
                        'message': "Le chapitre ne commence pas par un titre de niveau 1 (# Titre)"
                    })
                
                # Analyse de base du contenu
                word_count = len(content_text.split())
                if word_count < 100:
                    issues.append({
                        'level': 'info',
                        'type': 'short_chapter',
                        'path': str(chapter_file.relative_to(self.path)),
                        'message': f"Chapitre court ({word_count} mots)"
                    })
            
            except Exception as e:
                issues.append({
                    'level': 'error',
                    'type': 'chapter_parsing_error',
                    'path': str(chapter_file.relative_to(self.path)),
                    'message': f"Erreur lors de l'analyse du chapitre: {e}"
                })
        
        return issues
    
    def _validate_characters(self, characters_dir: Path) -> List[Dict[str, Any]]:
        """
        Valide les fiches de personnages.
        
        Args:
            characters_dir: Chemin du répertoire de personnages
            
        Returns:
            Liste des problèmes détectés
        """
        issues = []
        
        # Parcourir tous les répertoires de personnages
        character_files = []
        for subdir in ["", "entites", "manifestations", "mortels", "secondaires"]:
            dir_path = characters_dir / subdir if subdir else characters_dir
            if dir_path.exists():
                character_files.extend(dir_path.glob("*.md"))
        
        for char_file in character_files:
            try:
                # Lire le contenu de la fiche
                with open(char_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraire les métadonnées
                frontmatter, _ = self._extract_frontmatter(char_file)
                
                # Vérifier les métadonnées requises
                if frontmatter:
                    if 'nom' not in frontmatter:
                        issues.append({
                            'level': 'warning',
                            'type': 'missing_character_name',
                            'path': str(char_file.relative_to(self.path)),
                            'message': "Le nom du personnage est manquant dans les métadonnées"
                        })
                    
                    if 'tags' not in frontmatter or 'personnage' not in (frontmatter.get('tags') or []):
                        issues.append({
                            'level': 'info',
                            'type': 'missing_character_tag',
                            'path': str(char_file.relative_to(self.path)),
                            'message': "Le tag 'personnage' est manquant"
                        })
                else:
                    issues.append({
                        'level': 'warning',
                        'type': 'missing_frontmatter',
                        'path': str(char_file.relative_to(self.path)),
                        'message': "Métadonnées frontmatter manquantes pour ce personnage"
                    })
                
                # Vérifier les sections requises
                if not re.search(r'^# ', content, re.MULTILINE):
                    issues.append({
                        'level': 'warning',
                        'type': 'missing_character_heading',
                        'path': str(char_file.relative_to(self.path)),
                        'message': "La fiche de personnage ne commence pas par un titre de niveau 1 (# Nom)"
                    })
                
                # Vérifier les sections recommandées
                recommended_sections = ["Caractéristiques", "Contexte", "Arc narratif"]
                for section in recommended_sections:
                    if not re.search(f"^## {section}", content, re.MULTILINE):
                        issues.append({
                            'level': 'info',
                            'type': 'missing_character_section',
                            'path': str(char_file.relative_to(self.path)),
                            'message': f"Section recommandée manquante: {section}"
                        })
            
            except Exception as e:
                issues.append({
                    'level': 'error',
                    'type': 'character_parsing_error',
                    'path': str(char_file.relative_to(self.path)),
                    'message': f"Erreur lors de l'analyse de la fiche personnage: {e}"
                })
        
        return issues
    
    def fix_issues(self, issues: List[Dict[str, Any]], interactive: bool = True) -> Dict[str, int]:
        """
        Tente de corriger les problèmes de contenu détectés.
        
        Args:
            issues: Liste des problèmes à corriger
            interactive: Si True, demande confirmation avant chaque correction
            
        Returns:
            Dictionnaire indiquant le nombre de problèmes corrigés par catégorie
        """
        logger.info(f"Correction des problèmes de contenu pour: {self.path}")
        
        # Pour suivre les corrections appliquées
        fixes = {
            "frontmatter_added": 0,
            "metadata_fixed": 0,
            "structure_fixed": 0,
            "total": 0
        }
        
        # Traiter uniquement les problèmes liés au contenu
        content_issues = [issue for issue in issues if issue['type'] in (
            'missing_frontmatter', 'missing_chapter_title', 'missing_chapter_status',
            'missing_character_name', 'missing_character_tag'
        )]
        
        # Regrouper les problèmes par fichier
        issues_by_file = {}
        for issue in content_issues:
            path = issue['path']
            if path not in issues_by_file:
                issues_by_file[path] = []
            issues_by_file[path].append(issue)
        
        # Traiter chaque fichier
        for path, file_issues in issues_by_file.items():
            if interactive:
                print(f"\nFichier: {path}")
                print(f"Problèmes: {len(file_issues)}")
                for issue in file_issues:
                    print(f"- {issue['message']}")
                
                fix_file = input("Corriger ce fichier? [Y/n]: ").strip().lower()
                if fix_file and fix_file not in ('y', 'yes', 'oui'):
                    continue
            
            file_path = self.path / path
            try:
                # Lire le contenu actuel
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraire les métadonnées existantes
                frontmatter, body = self._extract_frontmatter(file_path)
                updated = False
                
                # Si frontmatter manquant, en créer un
                if any(issue['type'] == 'missing_frontmatter' for issue in file_issues):
                    if not frontmatter:
                        frontmatter = {}
                        updated = True
                        fixes["frontmatter_added"] += 1
                
                # Corriger les métadonnées
                for issue in file_issues:
                    if issue['type'] == 'missing_chapter_title':
                        # Chercher un titre dans le corps du texte
                        title_match = re.search(r'^# (.+)$', body, re.MULTILINE)
                        if title_match:
                            frontmatter['titre'] = title_match.group(1)
                            updated = True
                            fixes["metadata_fixed"] += 1
                    
                    elif issue['type'] == 'missing_chapter_status':
                        frontmatter['statut'] = 'brouillon'
                        updated = True
                        fixes["metadata_fixed"] += 1
                    
                    elif issue['type'] == 'missing_character_name':
                        # Chercher un nom dans le titre
                        name_match = re.search(r'^# (.+)$', body, re.MULTILINE)
                        if name_match:
                            frontmatter['nom'] = name_match.group(1)
                            updated = True
                            fixes["metadata_fixed"] += 1
                    
                    elif issue['type'] == 'missing_character_tag':
                        if 'tags' not in frontmatter:
                            frontmatter['tags'] = []
                        if isinstance(frontmatter['tags'], str):
                            frontmatter['tags'] = [tag.strip() for tag in frontmatter['tags'].split(',')]
                        if 'personnage' not in frontmatter['tags']:
                            frontmatter['tags'].append('personnage')
                            updated = True
                            fixes["metadata_fixed"] += 1
                
                # Si des modifications ont été effectuées, sauvegarder le fichier
                if updated:
                    new_content = "---\n"
                    new_content += yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
                    new_content += "---\n\n"
                    new_content += body
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    logger.info(f"Fichier corrigé: {path}")
                    fixes["total"] += 1
            
            except Exception as e:
                logger.error(f"Erreur lors de la correction du fichier {path}: {e}")
        
        return fixes
    
    def _extract_frontmatter(self, file_path: Union[str, Path]) -> tuple:
        """
        Extrait le frontmatter YAML et le contenu d'un fichier markdown.
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            Tuple (frontmatter_dict, content_str) ou (None, content_str) si pas de frontmatter
        """
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
        except yaml.YAMLError as e:
            logger.warning(f"Erreur de parsing YAML dans {file_path}: {e}")
            return None, content
    
    def get_chapter(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le contenu et les métadonnées d'un chapitre spécifique.
        
        Args:
            chapter_id: Identifiant du chapitre (nom de fichier ou slug)
            
        Returns:
            Dictionnaire contenant le contenu et les métadonnées du chapitre,
            ou None si le chapitre n'est pas trouvé
        """
        # Chercher dans les formats possibles de noms de fichiers
        possible_paths = [
            self.path / "chapitres" / f"{chapter_id}.md",
            self.path / "chapitres" / f"chapitre-{chapter_id}.md"
        ]
        
        # Ajout de recherche avec motifs numériques (chapitre-01, chapitre-XX-nom, etc.)
        if chapter_id.isdigit():
            possible_paths.append(self.path / "chapitres" / f"chapitre-{int(chapter_id):02d}.md")
        
        # Chercher des correspondances partielles
        chapter_path = None
        for path in possible_paths:
            if path.exists():
                chapter_path = path
                break
        
        if not chapter_path:
            # Recherche approfondie par glob
            pattern = f"*{chapter_id}*.md"
            matches = list(self.path.glob(f"chapitres/{pattern}"))
            matches.extend(list(self.path.glob(f"chapitres/**/{pattern}")))
            
            if matches:
                chapter_path = matches[0]
            else:
                logger.warning(f"Chapitre non trouvé: {chapter_id}")
                return None
        
        try:
            # Extraire les métadonnées et le contenu
            frontmatter, content = self._extract_frontmatter(chapter_path)
            
            # Analyser le contenu
            title = None
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
            
            # Calculer des statistiques
            word_count = len(content.split())
            
            return {
                "id": chapter_id,
                "path": str(chapter_path.relative_to(self.path)),
                "title": title or (frontmatter.get('titre') if frontmatter else None) or f"Chapitre {chapter_id}",
                "status": frontmatter.get('statut') if frontmatter else None,
                "metadata": frontmatter or {},
                "content": content,
                "statistics": {
                    "word_count": word_count,
                    "estimated_reading_time": word_count // 200  # Approximation en minutes
                }
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du chapitre {chapter_id}: {e}")
            return None
    
    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations sur un personnage spécifique.
        
        Args:
            character_id: Identifiant du personnage (nom de fichier ou slug)
            
        Returns:
            Dictionnaire contenant les informations du personnage,
            ou None si le personnage n'est pas trouvé
        """
        # Chercher dans les différents dossiers possibles de personnages
        character_dirs = [
            self.path / "personnages",
            self.path / "personnages" / "entites",
            self.path / "personnages" / "manifestations",
            self.path / "personnages" / "mortels",
            self.path / "personnages" / "secondaires"
        ]
        
        # Chercher le fichier dans tous les dossiers possibles
        character_path = None
        for dir_path in character_dirs:
            if not dir_path.exists():
                continue
            
            # Vérifier le nom exact
            file_path = dir_path / f"{character_id}.md"
            if file_path.exists():
                character_path = file_path
                break
            
            # Chercher avec une correspondance partielle
            matches = list(dir_path.glob(f"*{character_id}*.md"))
            if matches:
                character_path = matches[0]
                break
        
        if not character_path:
            logger.warning(f"Personnage non trouvé: {character_id}")
            return None
        
        try:
            # Extraire les métadonnées et le contenu
            frontmatter, content = self._extract_frontmatter(character_path)
            
            # Extraire le nom du personnage
            name = None
            name_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if name_match:
                name = name_match.group(1)
            
            # Extraire les sections principales
            sections = {}
            current_section = None
            current_content = []
            
            for line in content.split('\n'):
                section_match = re.match(r'^## (.+)$', line)
                if section_match:
                    # Sauvegarder la section précédente
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Démarrer une nouvelle section
                    current_section = section_match.group(1)
                    current_content = []
                elif current_section:
                    current_content.append(line)
            
            # Ajouter la dernière section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            
            return {
                "id": character_id,
                "path": str(character_path.relative_to(self.path)),
                "name": name or (frontmatter.get('nom') if frontmatter else None) or character_id,
                "metadata": frontmatter or {},
                "content": content,
                "sections": sections
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du personnage {character_id}: {e}")
            return None
    
    def search_content(self, query: str, content_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Recherche du contenu dans le projet en fonction d'une requête.
        
        Args:
            query: Termes de recherche
            content_types: Types de contenu à rechercher ("chapitres", "personnages", etc.)
            
        Returns:
            Liste des résultats correspondants
        """
        if not content_types:
            content_types = ["chapitres", "personnages", "structure"]
        
        results = []
        query_pattern = re.compile(re.escape(query), re.IGNORECASE)
        
        for content_type in content_types:
            if content_type == "chapitres":
                chapters_dir = self.path / "chapitres"
                if chapters_dir.exists():
                    for file_path in chapters_dir.glob("**/*.md"):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            if query_pattern.search(content):
                                frontmatter, _ = self._extract_frontmatter(file_path)
                                title = frontmatter.get('titre') if frontmatter else None
                                
                                if not title:
                                    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                                    if title_match:
                                        title = title_match.group(1)
                                
                                results.append({
                                    "type": "chapitre",
                                    "id": file_path.stem,
                                    "path": str(file_path.relative_to(self.path)),
                                    "title": title or file_path.stem,
                                    "preview": self._get_match_context(content, query_pattern)
                                })
                        except Exception as e:
                            logger.error(f"Erreur lors de la recherche dans {file_path}: {e}")
            
            elif content_type == "personnages":
                for dir_name in ["personnages", "personnages/entites", "personnages/manifestations", 
                                "personnages/mortels", "personnages/secondaires"]:
                    dir_path = self.path / dir_name
                    if not dir_path.exists():
                        continue
                    
                    for file_path in dir_path.glob("*.md"):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            if query_pattern.search(content):
                                frontmatter, _ = self._extract_frontmatter(file_path)
                                name = frontmatter.get('nom') if frontmatter else None
                                
                                if not name:
                                    name_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                                    if name_match:
                                        name = name_match.group(1)
                                
                                results.append({
                                    "type": "personnage",
                                    "id": file_path.stem,
                                    "path": str(file_path.relative_to(self.path)),
                                    "name": name or file_path.stem,
                                    "preview": self._get_match_context(content, query_pattern)
                                })
                        except Exception as e:
                            logger.error(f"Erreur lors de la recherche dans {file_path}: {e}")
            
            elif content_type == "structure":
                structure_dir = self.path / "structure"
                if structure_dir.exists():
                    for file_path in structure_dir.glob("**/*.md"):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            if query_pattern.search(content):
                                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                                title = title_match.group(1) if title_match else file_path.stem
                                
                                results.append({
                                    "type": "structure",
                                    "id": file_path.stem,
                                    "path": str(file_path.relative_to(self.path)),
                                    "title": title,
                                    "preview": self._get_match_context(content, query_pattern)
                                })
                        except Exception as e:
                            logger.error(f"Erreur lors de la recherche dans {file_path}: {e}")
        
        return results
    
    def _get_match_context(self, content: str, pattern: re.Pattern, context_size: int = 50) -> str:
        """
        Extrait le contexte autour de la première correspondance d'un motif.
        
        Args:
            content: Contenu à analyser
            pattern: Motif de recherche compilé
            context_size: Nombre de caractères à inclure avant et après
            
        Returns:
            Extrait de texte avec la correspondance et son contexte
        """
        match = pattern.search(content)
        if not match:
            return ""
        
        start_pos = max(0, match.start() - context_size)
        end_pos = min(len(content), match.end() + context_size)
        
        # Ajuster pour ne pas couper les mots
        if start_pos > 0:
            while start_pos > 0 and content[start_pos] != ' ':
                start_pos -= 1
        
        if end_pos < len(content):
            while end_pos < len(content) and content[end_pos] != ' ':
                end_pos += 1
        
        # Extraire le contexte
        context = content[start_pos:end_pos].strip()
        
        # Ajouter des ellipses si nécessaire
        if start_pos > 0:
            context = "..." + context
        if end_pos < len(content):
            context = context + "..."
        
        return context
