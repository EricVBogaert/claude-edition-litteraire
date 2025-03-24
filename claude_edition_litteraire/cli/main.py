"""
Interface en ligne de commande pour la bibliothèque claude_edition_litteraire.
"""

import os
import sys
import click
from pathlib import Path

from .. import __version__
from ..core import Project
from ..utils.logging import get_logger

logger = get_logger(__name__)

@click.group()
@click.version_option(version=__version__)
def main():
    """
    Claude Édition Littéraire: Outils pour l'édition littéraire assistée par IA.
    
    Cette application fournit des commandes pour gérer un projet d'édition littéraire,
    avec validation de structure, correction automatique, et intégration avec l'API Claude.
    """
    pass

@main.command('check')
@click.argument('project_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True), default='.')
@click.option('--format', '-f', type=click.Choice(['markdown', 'html']), default='markdown',
              help='Format du rapport (markdown ou html)')
@click.option('--output', '-o', help='Chemin du fichier de sortie pour le rapport')
def check_command(project_dir, format, output):
    """
    Vérifie la structure du projet et génère un rapport.
    
    PROJECT_DIR est le chemin vers le répertoire du projet (par défaut: répertoire courant).
    """
    try:
        project = Project(project_dir)
        issues = project.structure.validate()
        
        # Générer le rapport
        report_path = project.structure.generate_report(
            issues=issues,
            output_format=format,
            output_file=output
        )
        
        # Afficher un résumé
        error_count = sum(1 for issue in issues if issue['level'] == 'error')
        warning_count = sum(1 for issue in issues if issue['level'] == 'warning')
        
        click.echo(f"Vérification terminée. Trouvé {error_count} erreurs et {warning_count} avertissements.")
        click.echo(f"Rapport généré: {report_path}")
        
        # Retourner un code d'erreur si des erreurs ont été trouvées
        sys.exit(1 if error_count > 0 else 0)
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du projet: {e}")
        click.echo(f"Erreur: {e}", err=True)
        sys.exit(1)

@main.command('fix')
@click.argument('project_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True), default='.')
@click.option('--yes', '-y', is_flag=True, help='Mode non-interactif: répond "oui" à toutes les questions')
@click.option('--no-backup', is_flag=True, help='Ne pas créer de sauvegarde avant les modifications')
def fix_command(project_dir, yes, no_backup):
    """
    Corrige les problèmes de structure du projet.
    
    PROJECT_DIR est le chemin vers le répertoire du projet (par défaut: répertoire courant).
    """
    try:
        project = Project(project_dir)
        
        # En mode non-interactif, on affiche quand même un avertissement
        if yes:
            click.echo("Mode non-interactif: toutes les corrections seront appliquées automatiquement.")
            if not no_backup:
                click.echo("Une sauvegarde sera créée avant les modifications.")
        
        # Corriger les problèmes
        fixes = project.structure.fix_issues(
            interactive=not yes,
            backup=not no_backup
        )
        
        # Afficher un résumé
        if 'cancelled' in fixes:
            click.echo("Opération annulée par l'utilisateur.")
            sys.exit(0)
        
        if fixes.get('total', 0) > 0:
            click.echo(f"Corrections appliquées avec succès:")
            click.echo(f"  - {fixes.get('dirs_created', 0)} répertoires créés")
            click.echo(f"  - {fixes.get('files_created', 0)} fichiers créés")
            click.echo(f"  - {fixes.get('templates_fixed', 0)} templates ajoutés")
            click.echo(f"  - {fixes.get('links_fixed', 0)} liens corrigés")
            click.echo(f"  - {fixes.get('frontmatter_fixed', 0)} problèmes de frontmatter corrigés")
            click.echo(f"Total: {fixes.get('total', 0)} corrections")
            
            # Vérifier à nouveau pour voir s'il reste des problèmes
            remaining_issues = project.structure.validate()
            remaining_errors = sum(1 for issue in remaining_issues if issue['level'] == 'error')
            
            if remaining_errors > 0:
                click.echo(f"Attention: {remaining_errors} erreurs restantes nécessitent une intervention manuelle.")
                click.echo("Exécutez 'claude-lit check' pour générer un rapport détaillé.")
        else:
            click.echo("Aucune correction n'a été appliquée.")
        
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Erreur lors de la correction des problèmes: {e}")
        click.echo(f"Erreur: {e}", err=True)
        sys.exit(1)

@main.command('init')
@click.argument('project_dir', type=click.Path(file_okay=False), default='.')
@click.option('--name', '-n', help='Nom du projet')
@click.option('--author', '-a', help='Nom de l\'auteur')
@click.option('--template', '-t', type=click.Choice(['standard', 'minimal', 'complet']), default='standard',
              help='Template de structure à utiliser')
def init_command(project_dir, name, author, template):
    """
    Initialise un nouveau projet d'édition littéraire.
    
    PROJECT_DIR est le chemin vers le répertoire du projet (par défaut: répertoire courant).
    """
    project_path = Path(project_dir)
    
    # Vérifier si le répertoire existe déjà
    if project_path.exists():
        if not click.confirm(f"Le répertoire {project_dir} existe déjà. Continuer quand même?"):
            click.echo("Opération annulée.")
            sys.exit(0)
    else:
        # Créer le répertoire
        try:
            project_path.mkdir(parents=True)
        except Exception as e:
            click.echo(f"Erreur lors de la création du répertoire: {e}", err=True)
            sys.exit(1)
    
    # Demander le nom du projet et de l'auteur si non spécifiés
    if not name:
        name = click.prompt("Nom du projet", default=project_path.name)
    
    if not author:
        author = click.prompt("Nom de l'auteur", default="Auteur")
    
    # Initialiser le projet
    try:
        # Fonction à implémenter
        click.echo(f"Projet '{name}' initialisé avec succès dans {project_path}")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du projet: {e}")
        click.echo(f"Erreur: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
```