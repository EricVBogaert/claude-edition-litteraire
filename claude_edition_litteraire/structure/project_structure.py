"""
Classe principale pour la gestion de la structure d'un projet littéraire.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

from .validator import (
    validate_structure, validate_templates, 
    validate_frontmatter, check_broken_links,
    DEFAULT_EXPECTED_STRUCTURE, DEFAULT_EXPECTED_TEMPLATES, DEFAULT_FRONTMATTER_RULES
)
from .fixer import (
    fix_missing_dirs, fix_missing_files, fix_broken_links, 
    create_missing_file, find_similar_files, detect_common_path_issues,
    suggest_prefix_replacements
)
from .reporter import (
    generate_structure_report, generate_correction_plan,
    group_issues_by_pattern, prioritize_issues, present_correction_plan,
    generate_html_report
)
from ..utils.logging import get_logger

logger = get_logger(__name__)

class ProjectStructure:
    """
    Classe principale pour la gestion de la structure d'un projet littéraire.
    
    Cette classe fournit des méthodes pour valider et corriger la structure
    d'un projet littéraire, en détectant les problèmes et en proposant des
    solutions adaptées.
    """
    
    def __init__(self, project):
        """
        Initialise l'instance ProjectStructure.
        
        Args:
            project: Instance de la classe Project parente
        """
        self.project = project
        self.path = project.path
        self.config = project.config
        
        # Charger les définitions de structure depuis la configuration
        self._load_structure_definitions()
    
    def _load_structure_definitions(self):
        """
        Charge les définitions de structure depuis la configuration du projet.
        """
        # Obtenir les définitions de structure depuis la configuration, ou utiliser les valeurs par défaut
        self.expected_structure = self.config.get('structure', DEFAULT_EXPECTED_STRUCTURE)
        self.expected_templates = self.config.get('templates', DEFAULT_EXPECTED_TEMPLATES)
        self.frontmatter_rules = self.config.get('frontmatter', DEFAULT_FRONTMATTER_RULES)
    
    def validate(self) -> List[Dict[str, Any]]:
        """
        Valide la structure complète du projet.
        
        Returns:
            Liste des problèmes détectés
        """
        logger.info(f"Validation de la structure du projet: {self.path}")
        
        issues = []
        
        # 1. Valider la structure des dossiers et fichiers
        structure_issues = validate_structure(self.path, self.expected_structure)
        issues.extend(structure_issues)
        
        # 2. Vérifier les templates
        template_issues = validate_templates(self.path, self.expected_templates)
        issues.extend(template_issues)
        
        # 3. Vérifier les frontmatters
        frontmatter_issues = validate_frontmatter(self.path, self.frontmatter_rules)
        issues.extend(frontmatter_issues)
        
        # 4. Vérifier les liens internes
        link_issues = check_broken_links(self.path)
        issues.extend(link_issues)
        
        # Classer les problèmes par priorité
        issues = prioritize_issues(issues)
        
        logger.info(f"Validation terminée. Trouvé {len(issues)} problèmes.")
        
        return issues
    
    def fix_issues(
        self, 
        issues: Optional[List[Dict[str, Any]]] = None, 
        interactive: bool = True,
        backup: bool = True
    ) -> Dict[str, int]:
        """
        Corrige les problèmes détectés dans la structure du projet.
        
        Args:
            issues: Liste des problèmes à corriger, si None, exécute validate() d'abord
            interactive: Si True, demande confirmation avant chaque correction
            backup: Si True, crée une sauvegarde du projet avant les modifications
            
        Returns:
            Dictionnaire indiquant le nombre de corrections par catégorie
        """
        logger.info(f"Correction des problèmes de structure du projet: {self.path}")
        
        # Si aucune liste de problèmes n'est fournie, exécuter la validation
        if issues is None:
            issues = self.validate()
        
        if not issues:
            logger.info("Aucun problème à corriger.")
            return {"total": 0}
        
        # Créer une sauvegarde si demandé
        if backup:
            backup_path = self._create_backup()
            if not backup_path and interactive:
                confirm = input("Impossible de créer une sauvegarde. Continuer quand même? [y/N]: ").strip().lower()
                if confirm not in ('y', 'yes', 'oui'):
                    logger.info("Opération annulée.")
                    return {"cancelled": True}
        
        # Grouper et prioritiser les problèmes
        grouped_issues = group_issues_by_pattern(issues)
        
        # Générer un plan de correction
        correction_plan = generate_correction_plan(issues)
        
        # Si en mode interactif, présenter le plan et demander confirmation
        execution_plan = {}
        if interactive:
            execution_plan = present_correction_plan(correction_plan, interactive)
        else:
            # En mode non interactif, exécuter toutes les étapes
            execution_plan = {i+1: True for i in range(len(correction_plan))}
        
        # Appliquer les corrections selon le plan d'exécution
        fixes = self._apply_corrections(grouped_issues, correction_plan, execution_plan)
        
        # Exécuter une nouvelle validation pour voir les problèmes restants
        remaining_issues = self.validate()
        
        logger.info(f"Correction terminée. {fixes['total']} problèmes corrigés, {len(remaining_issues)} problèmes restants.")
        
        return fixes
    
    def _create_backup(self) -> Optional[Path]:
        """
        Crée une sauvegarde du projet avant modification.
        
        Returns:
            Chemin du dossier de sauvegarde, ou None en cas d'échec
        """
        try:
            backup_time = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_dir = self.path.parent / f"{self.path.name}_backup_{backup_time}"
            
            logger.info(f"Création d'une sauvegarde du projet: {backup_dir}")
            shutil.copytree(
                self.path, 
                backup_dir, 
                ignore=shutil.ignore_patterns('.git', '__pycache__', '.DS_Store')
            )
            
            return backup_dir
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
            return None
    
    def _apply_corrections(
        self,
        grouped_issues: Dict[str, Any],
        correction_plan: List[Dict[str, Any]],
        execution_plan: Dict[int, bool]
    ) -> Dict[str, int]:
        """
        Applique les corrections selon le plan d'exécution.
        
        Args:
            grouped_issues: Problèmes groupés par type
            correction_plan: Plan de correction généré
            execution_plan: Plan d'exécution avec les étapes approuvées
            
        Returns:
            Dictionnaire indiquant le nombre de corrections par catégorie
        """
        fixes = {
            "dirs_created": 0,
            "files_created": 0,
            "templates_fixed": 0,
            "links_fixed": 0,
            "frontmatter_fixed": 0,
            "total": 0
        }
        
        # Parcourir chaque étape du plan de correction
        for i, step in enumerate(correction_plan, 1):
            # Vérifier si cette étape doit être exécutée
            if not execution_plan.get(i, False):
                logger.info(f"Étape {i} ignorée: {step['title']}")
                continue
            
            logger.info(f"Exécution de l'étape {i}: {step['title']}")
            
            # Appliquer la correction selon le type d'étape
            if "Créer les dossiers et fichiers" in step['title']:
                # Étape 1: Correction des dossiers et fichiers manquants
                dirs_created = fix_missing_dirs(self.path, grouped_issues['missing_dirs'])
                fixes["dirs_created"] += dirs_created
                
                files_created = fix_missing_files(self.path, grouped_issues['missing_files'])
                fixes["files_created"] += files_created
                
                logger.info(f"  {dirs_created} répertoires créés, {files_created} fichiers créés")
            
            elif "templates manquants" in step['title']:
                # Étape 2: Correction des templates manquants
                templates_fixed = self._fix_missing_templates([item for item in step['items']])
                fixes["templates_fixed"] += templates_fixed
                logger.info(f"  {templates_fixed} templates corrigés")
            
            elif "problèmes de frontmatter" in step['title']:
                # Étape 3: Correction des problèmes de frontmatter
                # Cette correction nécessite souvent une intervention manuelle
                # À implémenter dans une version future
                logger.warning("  La correction automatique des problèmes de frontmatter n'est pas encore implémentée")
            
            elif "liens cassés" in step['title']:
                # Étape 4: Correction des liens cassés
                pattern = step['title'].split("'")[1] if "'" in step['title'] else None
                
                if pattern and pattern in grouped_issues['broken_links']:
                    links_fixed = fix_broken_links(self.path, grouped_issues['broken_links'][pattern], interactive=False)
                    fixes["links_fixed"] += links_fixed
                    logger.info(f"  {links_fixed} liens cassés corrigés")
            
            # Mettre à jour le total des corrections
            step_fixes = sum(v for k, v in fixes.items() if k != "total")
            fixes["total"] = step_fixes
        
        return fixes
    
    def _fix_missing_templates(self, issues: List[Dict[str, Any]]) -> int:
        """
        Corrige les templates manquants.
        
        Args:
            issues: Liste des problèmes de templates manquants
            
        Returns:
            Nombre de templates corrigés
        """
        templates_fixed = 0
        
        # Dictionnaire des templates de base
        base_templates = {
            'personnage-avance.md': """---
nom: {{nom}}
citation: {{citation}}
naissance: {{date}}
tags: personnage
---

# {{nom}}

*"{{citation}}"*

## Caractéristiques
- **Âge**: 
- **Apparence**: 
- **Traits de caractère**: 

## Contexte
- **Origine**: 
- **Famille**: 
- **Occupation**: 

## Arc narratif
- **Motivation**: 
- **Conflit**: 
- **Évolution**: 

## Apparitions
<!-- Les liens vers les chapitres où le personnage apparaît -->

## Notes
""",
            'chapitre.md': """---
titre: {{titre}}
statut: brouillon
date_creation: {{date}}
tags: chapitre
---

# {{titre}}

## Synopsis
<!-- Brève description du chapitre -->

## Scènes
<!-- Liste des scènes ou sections -->

## Personnages présents
<!-- Personnages apparaissant dans ce chapitre -->

## Notes
<!-- Notes et idées pour ce chapitre -->
""",
            'reference.md': """---
id: {{id}}
type: {{type}}
titre: {{titre}}
date: {{date}}
tags: reference
---

# {{titre}}

## Entrée
- **Type**: {{type}}
- **Créateur(s)**: 
- **Date**: 
- **Source**: 

## Description concise
<!-- Description en 1-3 phrases -->

## Pertinence pour le projet
<!-- En quoi cette référence est importante -->

## Éléments clés à retenir
- 
- 
- 

## Connexions internes
<!-- Liens vers d'autres éléments du projet reliés à cette référence -->
- 
- 

## Notes additionnelles
<!-- Réflexions personnelles, idées d'utilisation, etc. -->
""",
            'todo.md': """---
id: TODO-{{id}}
titre: {{titre}}
statut: À faire
priorite: 3
date_creation: {{date}}
date_debut: {{date}}
date_fin: 
tags: tâche
---

# {{titre}} [TODO-{{id}}]

**Statut**: À faire
**Priorité**: 3/5
**Période**: {{date}} → 

## Description

## Sous-tâches

- [ ] 
- [ ] 
- [ ] 

## Intervenants assignés

- [[]]

## Ressources nécessaires

- 
- 

## Notes
"""
        }
        
        for issue in issues:
            if issue['type'] != 'missing_template':
                continue
            
            template_name = os.path.basename(issue['path'])
            
            if template_name in base_templates:
                # Créer le template à partir du modèle de base
                template_dir = self.path / "templates"
                template_path = template_dir / template_name
                
                # Préparer les variables
                variables = {
                    "nom": "Nouveau Personnage",
                    "citation": "Citation caractéristique",
                    "titre": "Nouveau Titre",
                    "id": datetime.now().strftime("%Y%m%d%H%M%S")[:8],
                    "type": "livre",
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                
                # Créer le template
                if not template_path.exists():
                    os.makedirs(template_dir, exist_ok=True)
                    
                    # Remplacer les variables dans le template
                    content = base_templates[template_name]
                    for var, value in variables.items():
                        content = content.replace(f"{{{{{var}}}}}", value)
                    
                    # Écrire le fichier
                    with open(template_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    logger.info(f"Template créé: {template_path}")
                    templates_fixed += 1
        
        return templates_fixed
    
    def generate_report(
        self, 
        issues: Optional[List[Dict[str, Any]]] = None, 
        output_format: str = "markdown",
        output_file: Optional[str] = None
    ) -> str:
        """
        Génère un rapport sur les problèmes de structure détectés.
        
        Args:
            issues: Liste des problèmes à inclure dans le rapport, si None, exécute validate() d'abord
            output_format: Format du rapport ("markdown" ou "html")
            output_file: Nom du fichier de sortie, si None, utilise le nom par défaut
            
        Returns:
            Chemin du fichier de rapport généré, ou contenu du rapport si output_file est None
        """
        # Si aucune liste de problèmes n'est fournie, exécuter la validation
        if issues is None:
            issues = self.validate()
        
        if not output_file:
            # Définir un nom de fichier par défaut
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_file = f"structure-report-{timestamp}.{output_format}"
        
        # Générer le rapport selon le format demandé
        if output_format.lower() == "html":
            return generate_html_report(self.path, issues, output_file)
        else:
            return generate_structure_report(self.path, issues, output_file)
    
    def create_file(
        self, 
        file_path: str, 
        template_name: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Crée un nouveau fichier dans le projet à partir d'un template.
        
        Args:
            file_path: Chemin relatif du fichier à créer
            template_name: Nom du template à utiliser
            variables: Variables à remplacer dans le template
            
        Returns:
            True si le fichier a été créé, False sinon
        """
        return create_missing_file(self.path, file_path, template_name, variables=variables)
    
    def find_similar_files(self, file_path: str) -> List[Tuple[str, float]]:
        """
        Recherche des fichiers similaires à un chemin donné.
        
        Args:
            file_path: Chemin du fichier à rechercher
            
        Returns:
            Liste de fichiers similaires trouvés [(chemin, score_similitude)]
        """
        return find_similar_files(self.path, file_path)
