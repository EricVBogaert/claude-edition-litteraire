import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_claude_provider():
    """Fixture pour simuler le ClaudeProvider."""
    provider = MagicMock()
    provider.chat.return_value = "Réponse simulée de Claude"
    provider.embed.return_value = [0.1] * 384
    provider.supported_models.return_value = ["claude-3-mock"]
    return provider

@pytest.fixture
def mock_lmstudio_provider():
    """Fixture pour simuler le LMStudioProvider."""
    provider = MagicMock()
    provider.chat.return_value = "Réponse simulée de LMStudio"
    provider.embed.return_value = [0.1] * 384
    provider.supported_models.return_value = ["mock-model"]
    return provider
