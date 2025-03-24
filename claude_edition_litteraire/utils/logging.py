"""
Module de journalisation pour la bibliothèque.
"""

import os
import logging
from pathlib import Path
from datetime import datetime

def get_logger(name, level=logging.INFO):
    """
    Retourne un logger configuré pour le module spécifié.
    
    Args:
        name: Nom du module
        level: Niveau de journalisation
        
    Returns:
        Instance de logger configurée
    """
    # Si le logger existe déjà, on le retourne
    if name in logging.Logger.manager.loggerDict:
        return logging.getLogger(name)
    
    # Créer un nouveau logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Formateur pour les messages
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Gestionnaire de console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Gestionnaire de fichier
    try:
        # Créer un dossier logs s'il n'existe pas
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        # Créer un fichier de log avec la date du jour
        log_file = logs_dir / f"claude_edition_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # En cas d'erreur, on utilise seulement la console
        logger.warning(f"Impossible de créer le fichier de log: {e}")
    
    return logger
