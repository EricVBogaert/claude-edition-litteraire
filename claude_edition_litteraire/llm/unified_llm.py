"""
Classe principale pour l'interaction unifiée avec différents LLMs.
"""

import os
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Interface abstraite pour les fournisseurs de LLM."""
    
    @abstractmethod
    async def generate(self, prompt: str, context: Optional[str] = None, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Génère une réponse à partir d'un prompt et contexte optionnel.
        
        Args:
            prompt: Instruction ou question pour le LLM
            context: Contexte supplémentaire (optionnel)
            max_tokens: Nombre maximum de tokens pour la réponse
            
        Returns:
            Dictionnaire contenant la réponse et les métadonnées (tokens, etc.)
        """
        pass

class AnthropicDirectProvider(LLMProvider):
    """Implémentation utilisant directement l'API Anthropic."""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("Le module 'anthropic' est requis pour utiliser l'API Anthropic directement. Installez-le avec 'pip install anthropic'.")
    
    async def generate(self, prompt: str, context: Optional[str] = None, max_tokens: int = 1000) -> Dict[str, Any]:
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            return {
                "text": response.content[0].text,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
            }
        except Exception as e:
            # Pour compatibilité avec la version synchrone de l'API
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": full_prompt}]
                )
                
                return {
                    "text": response.content[0].text,
                    "usage": {
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                    }
                }
            except Exception as e2:
                raise RuntimeError(f"Erreur lors de l'appel à l'API Anthropic: {e2}")

class LangChainProvider(LLMProvider):
    """Implémentation utilisant LangChain."""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        try:
            from langchain.chat_models import ChatAnthropic
            
            os.environ["ANTHROPIC_API_KEY"] = api_key
            self.chat_model = ChatAnthropic(
                model=model
            )
            self.model = model
        except ImportError:
            raise ImportError("Le module 'langchain' est requis pour utiliser LangChain. Installez-le avec 'pip install langchain'.")
    
    async def generate(self, prompt: str, context: Optional[str] = None, max_tokens: int = 1000) -> Dict[str, Any]:
        try:
            from langchain.schema import HumanMessage
            
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            messages = [HumanMessage(content=full_prompt)]
            
            try:
                response = await self.chat_model.agenerate([messages], max_tokens=max_tokens)
                result_text = response.generations[0][0].text
                
                # Essayer de récupérer les informations de tokens
                token_info = {}
                if hasattr(response, 'llm_output') and response.llm_output:
                    llm_output = response.llm_output
                    if 'token_usage' in llm_output:
                        token_info = llm_output['token_usage']
                
                # Si pas d'informations de tokens, estimer
                if not token_info:
                    token_estimate = {
                        "prompt_tokens": len(full_prompt.split()) * 1.3,
                        "completion_tokens": len(result_text.split()) * 1.3
                    }
                    token_estimate["total_tokens"] = token_estimate["prompt_tokens"] + token_estimate["completion_tokens"]
                    token_info = token_estimate
                
                return {
                    "text": result_text,
                    "usage": token_info
                }
            except Exception as e:
                # Fallback vers l'interface synchrone
                response = self.chat_model.generate([messages], max_tokens=max_tokens)
                result_text = response.generations[0][0].text
                
                # Estimation de tokens
                token_estimate = {
                    "prompt_tokens": len(full_prompt.split()) * 1.3,
                    "completion_tokens": len(result_text.split()) * 1.3
                }
                token_estimate["total_tokens"] = token_estimate["prompt_tokens"] + token_estimate["completion_tokens"]
                
                return {
                    "text": result_text,
                    "usage": token_estimate
                }
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'utilisation de LangChain: {e}")

class LlamaIndexProvider(LLMProvider):
    """Implémentation utilisant LlamaIndex."""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        try:
            from llama_index.llms import Anthropic
            
            os.environ["ANTHROPIC_API_KEY"] = api_key
            self.llm = Anthropic(model=model)
            self.model = model
        except ImportError:
            raise ImportError("Le module 'llama-index' est requis pour utiliser LlamaIndex. Installez-le avec 'pip install llama-index'.")
    
    async def generate(self, prompt: str, context: Optional[str] = None, max_tokens: int = 1000) -> Dict[str, Any]:
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        try:
            response = await self.llm.acomplete(
                prompt=full_prompt,
                max_tokens=max_tokens
            )
            
            # LlamaIndex peut ne pas toujours retourner les informations de tokens
            # Estimation similaire
            token_estimate = {
                "prompt_tokens": len(full_prompt.split()) * 1.3,
                "completion_tokens": len(response.text.split()) * 1.3
            }
            token_estimate["total_tokens"] = token_estimate["prompt_tokens"] + token_estimate["completion_tokens"]
            
            return {
                "text": response.text,
                "usage": token_estimate
            }
        except Exception as e:
            # Fallback vers l'interface synchrone
            try:
                response = self.llm.complete(
                    prompt=full_prompt,
                    max_tokens=max_tokens
                )
                
                # Estimation de tokens
                token_estimate = {
                    "prompt_tokens": len(full_prompt.split()) * 1.3,
                    "completion_tokens": len(response.text.split()) * 1.3
                }
                token_estimate["total_tokens"] = token_estimate["prompt_tokens"] + token_estimate["completion_tokens"]
                
                return {
                    "text": response.text,
                    "usage": token_estimate
                }
            except Exception as e2:
                raise RuntimeError(f"Erreur lors de l'utilisation de LlamaIndex: {e2}")

class UnifiedLLM:
    """Interface unifiée pour interagir avec différents LLMs."""
    
    def __init__(self, provider: str = "langchain", api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """
        Initialise le client LLM avec le fournisseur spécifié.
        
        Args:
            provider: Type de fournisseur ('direct', 'langchain', 'llamaindex')
            api_key: Clé API Claude (par défaut: depuis les variables d'environnement)
            model: Identifiant du modèle à utiliser
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.provider_type = provider
        
        if not self.api_key:
            raise ValueError("Clé API manquante. Définissez-la en paramètre ou dans la variable d'environnement ANTHROPIC_API_KEY.")
        
        # Sélectionner le fournisseur approprié
        if provider == "direct":
            self.provider = AnthropicDirectProvider(api_key=self.api_key, model=self.model)
        elif provider == "langchain":
            self.provider = LangChainProvider(api_key=self.api_key, model=self.model)
        elif provider == "llamaindex":
            self.provider = LlamaIndexProvider(api_key=self.api_key, model=self.model)
        else:
            raise ValueError(f"Fournisseur non pris en charge: {provider}")
        
        # Compteur d'utilisation des tokens
        self.token_usage = {"prompt": 0, "completion": 0, "total": 0}
    
    async def generate_response(self, 
                               prompt: str, 
                               context: Optional[str] = None,
                               max_tokens: int = 1000) -> str:
        """
        Génère une réponse texte pour un prompt donné.
        
        Args:
            prompt: Question ou instruction pour le LLM
            context: Contexte supplémentaire (optionnel)
            max_tokens: Nombre maximum de tokens pour la réponse
            
        Returns:
            Réponse générée
        """
        try:
            # Appeler le fournisseur sélectionné
            result = await self.provider.generate(prompt, context, max_tokens)
            
            # Mettre à jour le compteur d'utilisation
            if "usage" in result:
                usage = result["usage"]
                self.token_usage["prompt"] += usage.get("prompt_tokens", 0)
                self.token_usage["completion"] += usage.get("completion_tokens", 0)
                self.token_usage["total"] += usage.get("total_tokens", 0)
            
            return result["text"]
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de la génération: {e}")
            return f"Erreur: {str(e)}"
    
    def compress_context(self, text: str, max_tokens: int = 3000) -> str:
        """
        Compresse le contexte pour respecter les limites de tokens.
        
        Args:
            text: Texte à compresser
            max_tokens: Limite de tokens souhaitée
            
        Returns:
            Texte compressé
        """
        # Estimation grossière du nombre de tokens (à améliorer)
        estimated_tokens = len(text.split()) * 1.3
        
        if estimated_tokens <= max_tokens:
            return text
        
        # Stratégie 1: Extraction de résumé avec titre et sections
        import re
        
        # Extraire le titre
        title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
        title = title_match.group(0) if title_match else ""
        
        # Extraire les sections principales
        sections = re.findall(r'^##\s+.+$.*?(?=^##|\Z)', text, re.MULTILINE | re.DOTALL)
        
        if title and sections:
            # Calculer l'espace disponible par section
            available_tokens = max_tokens - (len(title.split()) * 1.3)
            tokens_per_section = available_tokens / len(sections)
            
            compressed_sections = []
            for section in sections:
                # Extraire le titre de la section
                section_title_match = re.match(r'^(##\s+.+)$', section, re.MULTILINE)
                section_title = section_title_match.group(1) if section_title_match else ""
                
                # Extraire le contenu de la section
                section_content = section[len(section_title):].strip()
                
                # Compresser le contenu de la section
                section_words = section_content.split()
                available_content_tokens = tokens_per_section - (len(section_title.split()) * 1.3)
                max_words = int(available_content_tokens / 1.3)
                
                if len(section_words) > max_words:
                    # Réduction proportionnelle
                    compressed_content = " ".join(section_words[:max_words // 2] + ["..."] + section_words[-max_words // 2:])
                else:
                    compressed_content = section_content
                
                compressed_sections.append(f"{section_title}\n\n{compressed_content}")
            
            # Reconstruire le texte compressé
            return f"{title}\n\n" + "\n\n".join(compressed_sections)
        
        # Stratégie 2: Si pas de structure claire, utiliser une approche basique
        words = text.split()
        reduction_factor = max_tokens / estimated_tokens
        max_words = int(len(words) * reduction_factor)
        
        # Préserver le début et la fin (souvent plus importants)
        beginning_size = max_words * 2 // 3  # 2/3 au début
        ending_size = max_words - beginning_size  # 1/3 à la fin
        
        return " ".join(words[:beginning_size] + ["[...]"] + words[-ending_size:])
    
    def get_token_usage(self) -> Dict[str, int]:
        """
        Renvoie l'utilisation actuelle des tokens.
        
        Returns:
            Dictionnaire contenant l'utilisation des tokens
        """
        return self.token_usage
    
    def reset_token_usage(self):
        """
        Réinitialise le compteur d'utilisation des tokens.
        """
        self.token_usage = {"prompt": 0, "completion": 0, "total": 0}

    def estimate_tokens(self, text: str) -> int:
        """
        Estime le nombre de tokens dans un texte.
        
        Args:
            text: Texte à évaluer
            
        Returns:
            Nombre estimé de tokens
        """
        # Estimation simple basée sur le nombre de mots
        # En moyenne, 1 token = 0.75 mots en anglais
        return int(len(text.split()) * 1.3)  # Facteur un peu plus élevé pour être prudent