#!/bin/bash
# setup-pytest-di.sh
# Script pour configurer pytest avec l'injection de dépendances

echo "🔧 Configuration de pytest avec l'injection de dépendances..."

# Créer le fichier conftest.py pour les tests
mkdir -p tests

cat > tests/conftest.py << 'EOF'
"""
Configuration pytest pour les tests avec l'injection de dépendances.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock

# Ajouter le chemin du projet pour l'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import du fournisseur de services
from claude_edition_litteraire.utils.dependency_injection import get_service_provider

@pytest.fixture(scope="session", autouse=True)
def setup_service_provider():
    """
    Configure un environnement global de test pour l'injection de dépendances.
    Ce fixture est automatiquement utilisé pour tous les tests.
    """
    # Récupérer le fournisseur de services
    provider = get_service_provider()
    
    # Vider toutes les enregistrements précédents
    provider._services = {}
    provider._factories = {}
    
    yield provider
    
    # Nettoyer après les tests
    provider._services = {}
    provider._factories = {}

@pytest.fixture
def mock_llm():
    """Fixture pour simuler le LLMProvider."""
    provider = MagicMock()
    provider.chat.return_value = "Réponse simulée de LLM"
    provider.embed.return_value = [0.1] * 384
    provider.supported_models.return_value = ["mock-model"]
    
    # Enregistrer dans le fournisseur de services
    get_service_provider().register("llm", provider)
    
    return provider

@pytest.fixture
def mock_structure():
    """Fixture pour simuler le ProjectStructure."""
    structure = MagicMock()
    structure.validate.return_value = []
    structure.fix_issues.return_value = {"total": 0}
    structure.generate_report.return_value = "Rapport simulé"
    
    # Enregistrer dans le fournisseur de services
    get_service_provider().register("structure", structure)
    
    return structure

@pytest.fixture
def mock_content():
    """Fixture pour simuler le ContentManager."""
    content = MagicMock()
    content.validate.return_value = []
    content.fix_issues.return_value = {"total": 0}
    content.get_chapter.return_value = {"title": "Chapitre simulé", "content": "Contenu simulé"}
    content.get_character.return_value = {"name": "Personnage simulé", "description": "Description simulée"}
    
    # Enregistrer dans le fournisseur de services
    get_service_provider().register("content", content)
    
    return content

@pytest.fixture
def mock_claude():
    """Fixture pour simuler le ClaudeManager."""
    claude = MagicMock()
    claude.analyze_content.return_value = "Analyse simulée de Claude"
    
    # Enregistrer dans le fournisseur de services
    get_service_provider().register("claude", claude)
    
    return claude

@pytest.fixture
def mock_automation():
    """Fixture pour simuler le AutomationManager."""
    automation = MagicMock()
    automation.export.return_value = "chemin/simulé/export.pdf"
    
    # Enregistrer dans le fournisseur de services
    get_service_provider().register("automation", automation)
    
    return automation

@pytest.fixture
def project_with_mocks(mock_llm, mock_structure, mock_content, mock_claude, mock_automation, tmp_path):
    """
    Crée une instance de Project avec tous les services mockés.
    Utilise un répertoire temporaire comme chemin de projet.
    """
    from claude_edition_litteraire.core import Project
    
    # Créer un fichier de configuration minimal dans le répertoire temporaire
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    config_file = config_dir / "claude_config.yml"
    config_file.write_text("""
project:
  name: Test Project
  author: Test Author
claude:
  api_key: test_key
  model: claude-3-mock
    """)
    
    # Créer le projet
    project = Project(tmp_path, config_path=str(config_file))
    
    return project
EOF

# Créer un exemple de test utilisant l'injection de dépendances
mkdir -p tests/test_project

cat > tests/test_project/test_project_di.py << 'EOF'
"""
Tests pour la classe Project utilisant l'injection de dépendances.
"""

import pytest
from pathlib import Path

def test_project_initialization(project_with_mocks):
    """Teste l'initialisation de Project avec des services mockés."""
    # Le projet est déjà initialisé avec tous les mocks
    project = project_with_mocks
    
    # Vérifier que tous les services sont accessibles
    assert project.llm is not None
    assert project.structure is not None
    assert project.content is not None
    assert project.claude is not None
    assert project.automation is not None
    
    # Vérifier que le chemin existe
    assert isinstance(project.path, Path)
    assert project.path.exists()

def test_project_validate(project_with_mocks, mock_structure, mock_content):
    """Teste la méthode validate() de Project."""
    project = project_with_mocks
    
    # Configurer les mocks pour ce test spécifique
    mock_structure.validate.return_value = [{"level": "warning", "message": "Test warning"}]
    mock_content.validate.return_value = [{"level": "error", "message": "Test error"}]
    
    # Appeler la méthode à tester
    result = project.validate()
    
    # Vérifier que les mocks ont été appelés
    mock_structure.validate.assert_called_once()
    mock_content.validate.assert_called_once()
    
    # Vérifier le résultat
    assert "structure" in result
    assert "content" in result
    assert result["structure"] == [{"level": "warning", "message": "Test warning"}]
    assert result["content"] == [{"level": "error", "message": "Test error"}]

def test_project_fix_issues(project_with_mocks, mock_structure, mock_content):
    """Teste la méthode fix_issues() de Project."""
    project = project_with_mocks
    
    # Configurer les mocks
    mock_structure.validate.return_value = [{"level": "warning", "message": "Test warning"}]
    mock_content.validate.return_value = [{"level": "error", "message": "Test error"}]
    
    mock_structure.fix_issues.return_value = {"fixed": 1, "total": 1}
    mock_content.fix_issues.return_value = {"fixed": 2, "total": 2}
    
    # Appeler la méthode à tester
    result = project.fix_issues(interactive=False)
    
    # Vérifier que les mocks ont été appelés
    mock_structure.validate.assert_called_once()
    mock_content.validate.assert_called_once()
    mock_structure.fix_issues.assert_called_once()
    mock_content.fix_issues.assert_called_once()
    
    # Vérifier le résultat
    assert "structure" in result
    assert "content" in result
    assert result["structure"] == {"fixed": 1, "total": 1}
    assert result["content"] == {"fixed": 2, "total": 2}

def test_project_get_chapter(project_with_mocks, mock_content):
    """Teste la méthode get_chapter() de Project."""
    project = project_with_mocks
    
    # Configurer le mock
    chapter_data = {
        "id": "test-chapter",
        "title": "Chapitre de test",
        "content": "Contenu du chapitre",
        "metadata": {"status": "draft"}
    }
    mock_content.get_chapter.return_value = chapter_data
    
    # Appeler la méthode à tester
    result = project.get_chapter("test-chapter")
    
    # Vérifier que le mock a été appelé
    mock_content.get_chapter.assert_called_once_with("test-chapter")
    
    # Vérifier le résultat
    assert result == chapter_data

def test_project_get_character(project_with_mocks, mock_content):
    """Teste la méthode get_character() de Project."""
    project = project_with_mocks
    
    # Configurer le mock
    character_data = {
        "id": "test-character",
        "name": "Personnage de test",
        "description": "Description du personnage",
        "metadata": {"type": "protagonist"}
    }
    mock_content.get_character.return_value = character_data
    
    # Appeler la méthode à tester
    result = project.get_character("test-character")
    
    # Vérifier que le mock a été appelé
    mock_content.get_character.assert_called_once_with("test-character")
    
    # Vérifier le résultat
    assert result == character_data

def test_project_export(project_with_mocks, mock_automation):
    """Teste la méthode export() de Project."""
    project = project_with_mocks
    
    # Configurer le mock
    output_path = "/chemin/vers/sortie.pdf"
    mock_automation.export.return_value = output_path
    
    # Appeler la méthode à tester
    result = project.export("pdf", "output.pdf")
    
    # Vérifier que le mock a été appelé
    mock_automation.export.assert_called_once_with("pdf", "output.pdf")
    
    # Vérifier le résultat
    assert result == output_path

def test_project_analyze_content(project_with_mocks, mock_llm):
    """Teste la méthode analyze_content() de Project."""
    project = project_with_mocks
    
    # Configurer le mock
    mock_llm.chat.return_value = "Analyse du contenu: excellent"
    
    # Appeler la méthode à tester
    content = "Texte à analyser"
    instruction = "Analyse ce texte"
    result = project.analyze_content(content, instruction)
    
    # Vérifier que le mock a été appelé
    mock_llm.chat.assert_called_once()
    args = mock_llm.chat.call_args[0][0]  # premier argument de l'appel
    
    # Vérifier que les messages sont correctement formatés
    assert len(args) == 2
    assert args[0]["role"] == "system"
    assert args[0]["content"] == instruction
    assert args[1]["role"] == "user"
    assert args[1]["content"] == content
    
    # Vérifier le résultat
    assert result == "Analyse du contenu: excellent"
EOF

# Créer un exemple de test pour le module llm avec injection de dépendances
mkdir -p tests/test_llm

cat > tests/test_llm/test_unified_llm_di.py << 'EOF'
"""
Tests pour UnifiedLLM avec l'injection de dépendances.
"""

import pytest
from unittest.mock import MagicMock, patch

def test_unified_llm_chat_with_di():
    """
    Teste la méthode chat() de UnifiedLLM en utilisant l'injection de dépendances.
    """
    # Imports
    from claude_edition_litteraire.utils.dependency_injection import get_service_provider
    from claude_edition_litteraire.llm.unified_llm import UnifiedLLM
    
    # Créer des mocks pour les providers
    mock_claude = MagicMock()
    mock_claude.chat.return_value = "Réponse de Claude"
    mock_claude.supported_models.return_value = ["claude-3-mock"]
    
    mock_lmstudio = MagicMock()
    mock_lmstudio.chat.return_value = "Réponse de LMStudio"
    mock_lmstudio.supported_models.return_value = ["lmstudio-mock"]
    
    # Créer l'instance UnifiedLLM
    with patch("claude_edition_litteraire.llm.unified_llm.ClaudeProvider", return_value=mock_claude):
        with patch("claude_edition_litteraire.llm.unified_llm.LMStudioProvider", return_value=mock_lmstudio):
            # Instantier UnifiedLLM
            llm = UnifiedLLM(provider="claude")
            
            # Enregistrer dans le fournisseur de services
            get_service_provider().register("llm", llm)
            
            # Tester chat() avec Claude
            messages = [{"role": "user", "content": "Bonjour"}]
            response = llm.chat(messages)
            
            # Vérifier que le mock a été appelé
            mock_claude.chat.assert_called_once_with(
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                stream=False
            )
            
            # Vérifier le résultat
            assert response == "Réponse de Claude"
            
            # Basculer vers LMStudio
            llm.set_provider("lmstudio")
            
            # Réinitialiser les mocks
            mock_claude.chat.reset_mock()
            
            # Tester chat() avec LMStudio
            response = llm.chat(messages)
            
            # Vérifier que le mock a été appelé
            mock_lmstudio.chat.assert_called_once()
            
            # Vérifier le résultat
            assert response == "Réponse de LMStudio"

def test_context_compression_with_di():
    """
    Teste la compression de contexte dans UnifiedLLM.
    """
    # Imports
    from claude_edition_litteraire.utils.dependency_injection import get_service_provider
    from claude_edition_litteraire.llm.unified_llm import UnifiedLLM
    
    # Créer un mock pour le provider
    mock_provider = MagicMock()
    mock_provider.chat.return_value = "Réponse compressée"
    
    # Créer l'instance UnifiedLLM
    with patch("claude_edition_litteraire.llm.unified_llm.ClaudeProvider", return_value=mock_provider):
        # Instantier UnifiedLLM
        llm = UnifiedLLM(provider="claude")
        
        # Créer un mock pour context_compressor
        mock_compressor = MagicMock()
        compressed_messages = [{"role": "system", "content": "Résumé"}, {"role": "user", "content": "Question"}]
        mock_compressor.compress_by_strategy.return_value = compressed_messages
        
        # Assigner le mock au compresseur
        llm.context_compressor = mock_compressor
        
        # Enregistrer dans le fournisseur de services
        get_service_provider().register("llm", llm)
        
        # Créer des messages longs
        long_messages = []
        for i in range(10):
            long_messages.append({"role": "user", "content": f"Message {i}"})
            long_messages.append({"role": "assistant", "content": f"Réponse {i}"})
        
        # Tester chat() avec compression
        response = llm.chat(long_messages, compress_context=True)
        
        # Vérifier que le compresseur a été appelé
        mock_compressor.compress_by_strategy.assert_called_once()
        
        # Vérifier que le provider a été appelé avec les messages compressés
        mock_provider.chat.assert_called_once_with(
            messages=compressed_messages,
            max_tokens=1000,
            temperature=0.7,
            stream=False
        )
        
        # Vérifier le résultat
        assert response == "Réponse compressée"
EOF

# Créer un pytest.ini pour configurer les tests
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Ignorer certains avertissements
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning

# Options par défaut
addopts = --verbose

# Ajouter des marqueurs
markers =
    unit: tests unitaires qui testent une fonction ou méthode isolément
    integration: tests d'intégration qui testent l'interaction entre composants
    functional: tests fonctionnels qui testent des workflows complets
    slow: tests qui prennent plus de temps à s'exécuter
EOF

echo "✅ Configuration pytest avec injection de dépendances terminée!"
echo "Pour exécuter les tests avec l'injection de dépendances:"
echo "  pytest tests/test_project/test_project_di.py -v"
echo "  pytest tests/test_llm/test_unified_llm_di.py -v"
