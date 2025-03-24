# claude_edition_litteraire/utils/cli.py

def confirm_action(message, default=True):
    """Affiche un prompt standard [Y/n] ou [y/N]."""
    prompt = " [Y/n] " if default else " [y/N] "
    response = input(message + prompt).strip().lower()
    if not response:
        return default
    return response.startswith('y')