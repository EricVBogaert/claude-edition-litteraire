# claude_edition_litteraire/claude/dispatcher.py

import logging
import functools
from datetime import datetime

def trace_call(func):
    """Décorateur simple pour tracer les appels de fonction."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger = logging.getLogger("claude_dispatcher")
        logger.info(f"DÉBUT: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"FIN: {func.__name__}, durée: {datetime.now() - start_time}")
            return result
        except Exception as e:
            logger.error(f"ERREUR: {func.__name__}, {str(e)}")
            raise
            
    return wrapper

class ClaudeManager:
    """Version améliorée du ClaudeManager avec traçage."""
    
    def __init__(self, project):
        self.project = project
        self.api_key = project.config.get("claude.api_key")
    
    @trace_call
    def analyze_content(self, content, instruction):
        """Analyse un contenu avec Claude."""
        # Implementation...