"""
Module pour générer des rapports sur la structure du projet et les problèmes détectés.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ..utils.logging import get_logger

logger = get_logger(__name__)

def group_issues_by_file(issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Groupe les problèmes par fichier.
    
    Args:
        issues: Liste des problèmes détectés
        
    Returns:
        Dictionnaire des problèmes groupés par fichier
    """
    grouped = {}
    for issue in issues:
        path = issue.get('path', 'unknown')
        if path not in grouped:
            grouped[path] = []
        grouped[path].append(issue)
    
    return grouped

def group_issues_by_pattern(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Regroupe les problèmes par motifs similaires pour un traitement par lots.
    
    Args:
        issues: Liste des problèmes détectés
        
    Returns:
        Dictionnaire des groupes de problèmes
    """
    groups = {
        'missing_dirs': [],
        'missing_files': [],
        'broken_links': {},
        'frontmatter_issues': {},
        'other_issues': []
    }
    
    # Regrouper les liens cassés par motif de chemin
    for issue in issues:
        if issue['type'] == 'missing_required' and '.md' not in issue['path']:
            groups['missing_dirs'].append(issue)
        elif issue['type'] == 'missing_required' and '.md' in issue['path']:
            groups['missing_files'].append(issue)
        elif issue['type'] == 'broken_link':
            # Extraire le lien cassé
            link = issue['message'].split("'")[1]
            
            # Déterminer le motif (par ex: docs/, personnages/, etc.)
            pattern = 'autres'
            parts = link.split('/')
            if len(parts) > 1:
                pattern = parts[0]
            
            if pattern not in groups['broken_links']:
                groups['broken_links'][pattern] = []
            groups['broken_links'][pattern].append(issue)
        elif 'frontmatter' in issue['type']:
            # Regrouper par type de fichier
            file_type = 'autres'
            path = issue['path']
            
            if 'personnages' in path:
                file_type = 'personnages'
            elif 'chapitres' in path:
                file_type = 'chapitres'
            # etc.
            
            if file_type not in groups['frontmatter_issues']:
                groups['frontmatter_issues'][file_type] = []
            groups['frontmatter_issues'][file_type].append(issue)
        else:
            groups['other_issues'].append(issue)
    
    return groups

def generate_structure_report(
    project_path: Union[str, Path], 
    issues: List[Dict[str, Any]], 
    output_file: Optional[str] = "structure-report.md"
) -> str:
    """
    Crée un rapport au format Markdown des problèmes de structure détectés.
    
    Args:
        project_path: Chemin de base du projet
        issues: Liste des problèmes détectés
        output_file: Nom du fichier de sortie (facultatif)
        
    Returns:
        Chemin du fichier de rapport créé
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    # Compter les problèmes par niveau
    error_count = sum(1 for issue in issues if issue['level'] == 'error')
    warning_count = sum(1 for issue in issues if issue['level'] == 'warning')
    
    # Créer le contenu du rapport
    report_content = f"""# Rapport de vérification de structure

Projet: {project_path}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Résumé

- **Erreurs**: {error_count}
- **Avertissements**: {warning_count}
- **Total**: {len(issues)}

## Problèmes détectés

"""
    
    # Regrouper les problèmes par type
    issues_by_type = {}
    for issue in issues:
        issue_type = issue['type']
        if issue_type not in issues_by_type:
            issues_by_type[issue_type] = []
        issues_by_type[issue_type].append(issue)
    
    # Ajouter les problèmes au rapport, regroupés par type
    for issue_type, type_issues in sorted(issues_by_type.items()):
        report_content += f"### {issue_type.replace('_', ' ').title()} ({len(type_issues)})\n\n"
        
        for issue in sorted(type_issues, key=lambda x: x.get('path', '')):
            level_icon = "🔴" if issue['level'] == 'error' else "🟠"
            path = issue.get('path', 'N/A')
            report_content += f"- {level_icon} **{path}**: {issue['message']}\n"
        
        report_content += "\n"
    
    # Générer un plan de correction
    report_content += generate_correction_plan_markdown(issues)
    
    # Ajouter les recommandations
    report_content += """
## Recommandations

1. Corriger d'abord les erreurs critiques liées à la structure de base du projet
2. Résoudre ensuite les problèmes de frontmatter dans les fichiers spécifiques
3. Vérifier et corriger les liens internes cassés
4. Exécuter à nouveau une vérification pour confirmer que tous les problèmes ont été résolus

"""
    
    # Écrire le rapport dans un fichier si un nom est spécifié
    if output_file:
        output_path = project_path / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Rapport de structure créé: {output_path}")
        return str(output_path)
    
    return report_content

def generate_correction_plan(
    issues: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Génère un plan de correction étape par étape basé sur les problèmes détectés.
    
    Args:
        issues: Liste des problèmes détectés
        
    Returns:
        Plan d'actions recommandées
    """
    # Grouper les problèmes par type
    groups = group_issues_by_pattern(issues)
    
    plan = []
    
    # Étape 1: Corriger la structure de base (dossiers et fichiers requis)
    if groups['missing_dirs'] or groups['missing_files']:
        plan.append({
            'title': "Créer les dossiers et fichiers de structure manquants",
            'description': "Ces éléments sont requis pour la structure de base du projet.",
            'count': len(groups['missing_dirs']) + len(groups['missing_files']),
            'items': groups['missing_dirs'] + groups['missing_files']
        })
    
    # Étape 2: Corriger les templates manquants
    missing_templates = [i for i in issues if i['type'] == 'missing_template']
    if missing_templates:
        plan.append({
            'title': "Ajouter les templates manquants",
            'description': "Les templates sont essentiels pour maintenir la cohérence du projet.",
            'count': len(missing_templates),
            'items': missing_templates
        })
    
    # Étape 3: Corriger les problèmes de frontmatter par type de fichier
    for file_type, frontmatter_issues in groups['frontmatter_issues'].items():
        if frontmatter_issues:
            plan.append({
                'title': f"Corriger les problèmes de frontmatter dans les fichiers {file_type}",
                'description': "Les métadonnées frontmatter sont essentielles pour les fonctionnalités d'Obsidian.",
                'count': len(frontmatter_issues),
                'items': frontmatter_issues
            })
    
    # Étape 4: Corriger les liens cassés par groupe
    for pattern, link_issues in groups['broken_links'].items():
        if link_issues:
            plan.append({
                'title': f"Corriger les liens cassés avec le motif '{pattern}/'",
                'description': f"Ces liens cassés partagent un motif commun et peuvent être traités ensemble.",
                'count': len(link_issues),
                'items': link_issues
            })
    
    # Étape 5: Autres problèmes
    if groups['other_issues']:
        plan.append({
            'title': "Corriger les autres problèmes",
            'description': "Problèmes divers qui nécessitent une attention particulière.",
            'count': len(groups['other_issues']),
            'items': groups['other_issues']
        })
    
    return plan

def generate_correction_plan_markdown(issues: List[Dict[str, Any]]) -> str:
    """
    Génère un plan de correction au format Markdown.
    
    Args:
        issues: Liste des problèmes détectés
        
    Returns:
        Contenu Markdown du plan de correction
    """
    plan = generate_correction_plan(issues)
    
    if not plan:
        return ""
    
    markdown = """
## Plan de correction

Voici les étapes recommandées pour résoudre les problèmes détectés:

"""
    
    for i, step in enumerate(plan, 1):
        markdown += f"### Étape {i}: {step['title']} ({step['count']} éléments)\n\n"
        markdown += f"{step['description']}\n\n"
        
        # Ajouter quelques exemples
        markdown += "**Exemples:**\n\n"
        for item in step['items'][:3]:  # Limiter à 3 exemples
            path = item.get('path', 'N/A')
            message = item.get('message', 'N/A')
            markdown += f"- `{path}`: {message}\n"
        
        if len(step['items']) > 3:
            markdown += f"\n... et {len(step['items']) - 3} autres éléments\n\n"
        
        markdown += "\n"
    
    return markdown

def prioritize_issues(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Classe les problèmes par ordre de priorité pour une résolution efficace.
    
    Args:
        issues: Liste des problèmes détectés
        
    Returns:
        Liste des problèmes classés par priorité
    """
    # Définir les poids de priorité pour chaque type de problème
    priority_weights = {
        'missing_required': 100,    # Éléments requis manquants (plus haute priorité)
        'missing_template': 90,     # Templates manquants
        'type_mismatch': 80,        # Type incorrect (fichier vs dossier)
        'frontmatter_parsing_error': 70,  # Erreurs de parsing YAML
        'missing_required_field': 60,     # Champs requis manquants
        'broken_link': 50,          # Liens cassés
        'invalid_tags': 40,         # Tags invalides
        'missing_recommended_field': 30,  # Champs recommandés manquants
        'missing_optional': 20,     # Éléments optionnels manquants (priorité plus basse)
        'default': 10               # Valeur par défaut pour les autres types
    }
    
    # Fonction de calcul du score de priorité
    def get_priority_score(issue):
        # Score de base selon le type d'issue
        base_score = priority_weights.get(issue['type'], priority_weights['default'])
        
        # Ajustements basés sur le niveau de sévérité
        level_multiplier = 2 if issue['level'] == 'error' else 1
        
        # Ajustements basés sur le chemin (les fichiers de structure ont une priorité plus élevée)
        path_bonus = 0
        if 'path' in issue:
            if 'structure/' in issue['path']:
                path_bonus += 20
            elif 'templates/' in issue['path']:
                path_bonus += 15
            elif 'index.md' in issue['path']:
                path_bonus += 10
        
        return base_score * level_multiplier + path_bonus
    
    # Trier les problèmes selon le score de priorité
    prioritized_issues = sorted(issues, key=get_priority_score, reverse=True)
    
    return prioritized_issues

def present_correction_plan(
    plan: List[Dict[str, Any]], 
    interactive: bool = True
) -> Dict[int, bool]:
    """
    Présente le plan de correction à l'utilisateur et permet une exécution étape par étape.
    
    Args:
        plan: Plan de correction généré
        interactive: Mode interactif pour obtenir des confirmations
        
    Returns:
        Dictionnaire indiquant quelles étapes ont été approuvées pour exécution
    """
    execution_plan = {}
    
    print("\n=== PLAN DE CORRECTION ===\n")
    
    for i, step in enumerate(plan, 1):
        print(f"{i}. {step['title']} ({step['count']} éléments)")
        print(f"   {step['description']}")
        
        # Afficher quelques exemples
        print("\n   Exemples:")
        for item in step['items'][:3]:  # Limiter à 3 exemples
            if 'path' in item:
                print(f"   - {item['path']}: {item['message']}")
            else:
                print(f"   - {item['message']}")
        
        if len(step['items']) > 3:
            print(f"   ... et {len(step['items']) - 3} autres éléments")
        
        print()
        
        if interactive:
            action = input(f"Exécuter l'étape {i}? [Y/n/v(voir plus)]: ").strip().lower()
            
            if action == 'v':
                # Afficher plus de détails
                print("\n   Détails complets:")
                for item in step['items']:
                    if 'path' in item:
                        print(f"   - {item['path']}: {item['message']}")
                    else:
                        print(f"   - {item['message']}")
                print()
                
                action = input(f"Exécuter l'étape {i}? [Y/n]: ").strip().lower()
            
            execution_plan[i] = not action or action in ('y', 'yes', 'oui')
        else:
            execution_plan[i] = True
    
    return execution_plan

def generate_html_report(
    project_path: Union[str, Path], 
    issues: List[Dict[str, Any]], 
    output_file: Optional[str] = "structure-report.html"
) -> str:
    """
    Crée un rapport au format HTML des problèmes de structure détectés,
    avec fonctionnalités interactives.
    
    Args:
        project_path: Chemin de base du projet
        issues: Liste des problèmes détectés
        output_file: Nom du fichier de sortie (facultatif)
        
    Returns:
        Chemin du fichier de rapport créé
    """
    if not isinstance(project_path, Path):
        project_path = Path(project_path)
    
    # Compter les problèmes par niveau
    error_count = sum(1 for issue in issues if issue['level'] == 'error')
    warning_count = sum(1 for issue in issues if issue['level'] == 'warning')
    
    # Regrouper les problèmes par type
    issues_by_type = {}
    for issue in issues:
        issue_type = issue['type']
        if issue_type not in issues_by_type:
            issues_by_type[issue_type] = []
        issues_by_type[issue_type].append(issue)
    
    # Générer le plan de correction
    correction_plan = generate_correction_plan(issues)
    
    # Créer le contenu HTML
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de structure - {project_path.name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            line-height: 1.6;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        .summary {{
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-counts {{
            display: flex;
            gap: 20px;
        }}
        .count-item {{
            flex: 1;
            text-align: center;
            padding: 10px;
            border-radius: 6px;
        }}
        .errors {{
            background-color: #fee;
            border: 1px solid #f99;
        }}
        .warnings {{
            background-color: #ffd;
            border: 1px solid #dda;
        }}
        .total {{
            background-color: #eef;
            border: 1px solid #aad;
        }}
        .issue-type {{
            margin-top: 30px;
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .issue-type h3 {{
            margin-top: 0;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }}
        .issue-list {{
            list-style-type: none;
            padding-left: 0;
        }}
        .issue-item {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .error-icon {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .warning-icon {{
            color: #f39c12;
            font-weight: bold;
        }}
        .path {{
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 4px;
        }}
        .plan-step {{
            background-color: #e8f4f8;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .collapsible {{
            cursor: pointer;
            padding: 10px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 16px;
            background-color: #f1f1f1;
            border-radius: 4px;
        }}
        .active, .collapsible:hover {{
            background-color: #ddd;
        }}
        .content {{
            padding: 0 18px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.2s ease-out;
            background-color: #f9f9f9;
        }}
    </style>
</head>
<body>
    <h1>Rapport de vérification de structure</h1>
    <p>Projet: {project_path}<br>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <h2>Résumé</h2>
        <div class="summary-counts">
            <div class="count-item errors">
                <h3>{error_count}</h3>
                <p>Erreurs</p>
            </div>
            <div class="count-item warnings">
                <h3>{warning_count}</h3>
                <p>Avertissements</p>
            </div>
            <div class="count-item total">
                <h3>{len(issues)}</h3>
                <p>Total</p>
            </div>
        </div>
    </div>
    
    <h2>Problèmes détectés</h2>
"""
    
    # Ajouter les problèmes au rapport, regroupés par type
    for issue_type, type_issues in sorted(issues_by_type.items()):
        html_content += f"""
    <div class="issue-type">
        <h3>{issue_type.replace('_', ' ').title()} ({len(type_issues)})</h3>
        <ul class="issue-list">
"""
        
        for issue in sorted(type_issues, key=lambda x: x.get('path', '')):
            level_icon = "🔴" if issue['level'] == 'error' else "🟠"
            icon_class = "error-icon" if issue['level'] == 'error' else "warning-icon"
            path = issue.get('path', 'N/A')
            html_content += f"""
            <li class="issue-item">
                <span class="{icon_class}">{level_icon}</span>
                <span class="path">{path}</span>: {issue['message']}
            </li>"""
        
        html_content += """
        </ul>
    </div>
"""
    
    # Ajouter le plan de correction
    html_content += """
    <h2>Plan de correction</h2>
    <p>Voici les étapes recommandées pour résoudre les problèmes détectés:</p>
"""
    
    for i, step in enumerate(correction_plan, 1):
        html_content += f"""
    <div class="plan-step">
        <button class="collapsible">Étape {i}: {step['title']} ({step['count']} éléments)</button>
        <div class="content">
            <p>{step['description']}</p>
            <h4>Exemples:</h4>
            <ul>
"""
        
        for item in step['items'][:5]:  # Limiter à 5 exemples
            path = item.get('path', 'N/A')
            message = item.get('message', 'N/A')
            html_content += f"""
                <li><code>{path}</code>: {message}</li>"""
        
        if len(step['items']) > 5:
            html_content += f"""
                <li>... et {len(step['items']) - 5} autres éléments</li>"""
        
        html_content += """
            </ul>
        </div>
    </div>
"""
    
    # Ajouter les recommandations et le script JavaScript pour les éléments collapsibles
    html_content += """
    <h2>Recommandations</h2>
    <ol>
        <li>Corriger d'abord les erreurs critiques liées à la structure de base du projet</li>
        <li>Résoudre ensuite les problèmes de frontmatter dans les fichiers spécifiques</li>
        <li>Vérifier et corriger les liens internes cassés</li>
        <li>Exécuter à nouveau une vérification pour confirmer que tous les problèmes ont été résolus</li>
    </ol>
    
    <script>
    var coll = document.getElementsByClassName("collapsible");
    var i;
    
    for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    }
    </script>
</body>
</html>
"""
    
    # Écrire le rapport dans un fichier si un nom est spécifié
    if output_file:
        output_path = project_path / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Rapport HTML de structure créé: {output_path}")
        return str(output_path)
    
    return html_content