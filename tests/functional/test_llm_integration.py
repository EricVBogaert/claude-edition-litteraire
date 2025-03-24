"""
Tests fonctionnels pour les fonctionnalités essentielles du module LLM.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Ajouter le chemin du projet pour l'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from claude_edition_litteraire.llm.unified_llm import UnifiedLLM
from claude_edition_litteraire.llm.context import ContextCompressor

class TestUnifiedLLMCore:
    """Tests fonctionnels pour les fonctionnalités essentielles de UnifiedLLM."""

    def test_provider_switching(self):
        """Teste la capacité à basculer entre différents fournisseurs."""
        # Créer des mocks pour les deux providers
        mock_claude = MagicMock()
        mock_claude.chat.return_value = "Réponse de Claude"
        
        mock_lmstudio = MagicMock()
        mock_lmstudio.chat.return_value = "Réponse de LMStudio"
        
        # Initialiser UnifiedLLM avec les providers mockés
        llm = UnifiedLLM.__new__(UnifiedLLM)
        llm.providers = {
            "claude": mock_claude,
            "lmstudio": mock_lmstudio
        }
        llm.active_provider = "claude"
        llm.context_compressor = ContextCompressor()
        
        # Test avec le provider Claude
        messages = [{"role": "user", "content": "Bonjour"}]
        response = llm.chat(messages)
        assert response == "Réponse de Claude"
        mock_claude.chat.assert_called_once()
        
        # Basculer vers LMStudio
        llm.set_provider("lmstudio")
        assert llm.get_provider() == "lmstudio"
        
        # Test avec le provider LMStudio
        response = llm.chat(messages)
        assert response == "Réponse de LMStudio"
        mock_lmstudio.chat.assert_called_once()
    
    def test_context_compression(self):
        """Teste que la compression de contexte fonctionne correctement."""
        # Créer un mock pour le provider
        mock_provider = MagicMock()
        mock_provider.chat.return_value = "Réponse avec compression"
        
        # Initialiser UnifiedLLM avec le provider mocké
        llm = UnifiedLLM.__new__(UnifiedLLM)
        llm.providers = {"mock": mock_provider}
        llm.active_provider = "mock"
        llm.context_compressor = ContextCompressor()
        
        # Créer une longue conversation
        long_conversation = [
            {"role": "system", "content": "Tu es un assistant pour l'édition littéraire"},
        ]
        
        # Ajouter 20 échanges de messages
        for i in range(10):
            long_conversation.append({"role": "user", "content": f"Question {i}"})
            long_conversation.append({"role": "assistant", "content": f"Réponse {i}"})
        
        # Ajouter un message final
        final_message = {"role": "user", "content": "Question finale"}
        
        # Simuler un appel avec compression
        with patch.object(llm.context_compressor, 'compress_by_strategy') as mock_compress:
            # Configuration du mock pour qu'il retourne une version compressée
            compressed_messages = [
                {"role": "system", "content": "Tu es un assistant pour l'édition littéraire"},
                {"role": "system", "content": "Résumé de conversation précédente..."},
                {"role": "user", "content": "Question 9"},
                {"role": "assistant", "content": "Réponse 9"},
                {"role": "user", "content": "Question finale"}
            ]
            mock_compress.return_value = compressed_messages
            
            # Appeler chat avec compression
            response = llm.chat(long_conversation + [final_message], compress_context=True)
            
            # Vérifier que compress_by_strategy a été appelé
            mock_compress.assert_called_once()
            
            # Vérifier que le provider a été appelé avec les messages compressés
            mock_provider.chat.assert_called_once()
            # Obtenir les arguments passés à provider.chat
            call_args = mock_provider.chat.call_args[1]
            assert 'messages' in call_args
            assert call_args['messages'] == compressed_messages
    
    def test_message_creation(self):
        """Teste la création correcte de messages formatés."""
        # Initialiser UnifiedLLM directement avec les attributs nécessaires
        llm = UnifiedLLM.__new__(UnifiedLLM)
        llm.providers = {"mock": MagicMock()}
        llm.active_provider = "mock"
        
        # Créer un message utilisateur
        user_msg = llm.create_message("user", "Bonjour")
        assert user_msg["role"] == "user"
        assert user_msg["content"] == "Bonjour"
        
        # Créer un message système
        system_msg = llm.create_message("system", "Instructions spéciales")
        assert system_msg["role"] == "system"
        assert system_msg["content"] == "Instructions spéciales"
        
        # Créer un message assistant
        assistant_msg = llm.create_message("assistant", "Je peux vous aider")
        assert assistant_msg["role"] == "assistant"
        assert assistant_msg["content"] == "Je peux vous aider"
        
        # Vérifier le rejet des rôles invalides
        with pytest.raises(ValueError):
            llm.create_message("invalid_role", "Contenu")


class TestProjectIntegration:
    """Tests d'intégration avec la classe Project."""
    
    def test_project_analyze_content(self):
        """Teste l'intégration de UnifiedLLM avec la méthode analyze_content du projet."""
        # Créer un mock pour Config
        mock_config = MagicMock()
        mock_config.get.return_value = "fake-api-key"
        
        # Créer un mock pour Project
        mock_project = MagicMock()
        mock_project.config = mock_config
        
        # Créer un mock pour UnifiedLLM
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "Analyse de contenu réussie"
        
        # Attacher le mock LLM au projet
        mock_project.llm = mock_llm
        
        # Import dynamique pour éviter les problèmes de dépendances circulaires
        import importlib
        module = importlib.import_module('claude_edition_litteraire.claude.manager')
        ClaudeManager = getattr(module, 'ClaudeManager')
        
        # Créer une instance de ClaudeManager avec notre mock Project
        manager = ClaudeManager(mock_project)
        
        # Tester analyze_content
        content = "Ceci est un contenu à analyser"
        instruction = "Analyse ce contenu"
        
        result = manager.analyze_content(content, instruction)
        
        # Vérifier que le LLM a été appelé correctement
        mock_llm.chat.assert_called_once()
        call_args = mock_llm.chat.call_args[0][0]  # Premier argument positionnels (messages)
        
        # Vérifier que les messages contiennent l'instruction et le contenu
        assert len(call_args) == 2
        assert call_args[0]["role"] == "system"
        assert call_args[0]["content"] == instruction
        assert call_args[1]["role"] == "user"
        assert call_args[1]["content"] == content
        
        # Vérifier que le résultat est correct
        assert result == "Analyse de contenu réussie"


def test_document_analysis_workflow():
    """
    Teste un scénario d'utilisation typique: analyse d'un document littéraire.
    Ce test simule un flux de travail complet avec UnifiedLLM.
    """
    # Créer un mock pour le provider
    mock_provider = MagicMock()
    mock_provider.chat.return_value = (
        "Le texte présente une structure narrative cohérente. "
        "Le personnage principal est bien développé, mais les personnages "
        "secondaires manquent de profondeur. Le style est fluide et élégant."
    )
    
    # Initialiser UnifiedLLM avec le provider mocké
    llm = UnifiedLLM.__new__(UnifiedLLM)
    llm.providers = {"mock": mock_provider}
    llm.active_provider = "mock"
    llm.context_compressor = ContextCompressor()
    
    # Document littéraire d'exemple
    document = """
    Le soleil se levait à peine sur la petite ville de Saint-Maur. 
    Jean-Philippe contemplait l'horizon, perdu dans ses pensées. 
    Depuis la disparition de sa femme, le temps semblait s'être arrêté.
    Les jours passaient, identiques et mornes.
    
    "Un café, monsieur?" demanda la serveuse du bistrot où il s'était réfugié.
    
    Il acquiesça d'un signe de tête, sans même la regarder.
    """
    
    # Instructions d'analyse
    instructions = """
    Analyse ce passage littéraire en considérant:
    1. La structure narrative
    2. Le développement des personnages
    3. Le style d'écriture
    """
    
    # Analyser le document
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": document}
    ]
    
    analysis = llm.chat(messages)
    
    # Vérifier que l'analyse a été effectuée
    mock_provider.chat.assert_called_once()
    
    # Vérifier le contenu de l'analyse
    assert "structure narrative" in analysis.lower()
    assert "personnage" in analysis.lower()
    assert "style" in analysis.lower()
    
    # Simuler un retour de l'utilisateur et une analyse plus approfondie
    follow_up = "Pourrais-tu développer davantage sur le style d'écriture?"
    
    # Mettre à jour les messages
    messages.append({"role": "assistant", "content": analysis})
    messages.append({"role": "user", "content": follow_up})
    
    # Configurer une nouvelle réponse
    mock_provider.chat.return_value = (
        "Le style d'écriture est caractérisé par des phrases courtes et incisives, "
        "créant un rythme saccadé qui reflète l'état émotionnel du personnage. "
        "L'auteur utilise des images visuelles fortes (le soleil qui se lève, l'horizon) "
        "qui contrastent avec l'état intérieur du protagoniste."
    )
    
    # Obtenir l'analyse approfondie
    detailed_analysis = llm.chat(messages)
    
    # Vérifier que l'analyse a été effectuée une seconde fois
    assert mock_provider.chat.call_count == 2
    
    # Vérifier le contenu de l'analyse détaillée
    assert "style" in detailed_analysis.lower()
    assert "phrases" in detailed_analysis.lower()
    assert "rythme" in detailed_analysis.lower()
