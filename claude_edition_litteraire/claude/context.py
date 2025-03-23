# claude_edition_litteraire/claude/context.py

class ContextCompressor:
    """Compresse le contexte pour optimiser les appels à Claude."""
    
    def __init__(self):
        self.max_context_tokens = 100000  # Exemple de limite
    
    def compress_context(self, messages):
        """Version simple de compression de contexte."""
        # Limiter le nombre de messages si trop nombreux
        if len(messages) > 10:
            # Garder le premier message (souvent système) et les derniers
            return [messages[0]] + messages[-9:]
        return messages