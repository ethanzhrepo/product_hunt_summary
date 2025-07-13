import logging
from typing import Dict, Any
from .deepseek_analyzer import DeepSeekAnalyzer
from .openai_analyzer import OpenAIAnalyzer
from .gemini_analyzer import GeminiAnalyzer
from .ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)

class AnalyzerFactory:
    """Factory class for creating AI analyzers based on configuration"""
    
    @staticmethod
    def create_analyzer(config_manager, language: str = "zh") -> AIAnalyzer:
        """
        Create an AI analyzer based on configuration
        
        Args:
            config_manager: Configuration manager instance
            language: Output language code
            
        Returns:
            AI analyzer instance
            
        Raises:
            ValueError: If unsupported AI provider is specified
            KeyError: If required configuration is missing
        """
        try:
            # Get AI provider from config, default to deepseek
            ai_provider = config_manager.config.get('ai_provider', 'deepseek').lower()
            
            logger.info(f"Creating AI analyzer: {ai_provider}")
            
            if ai_provider == 'deepseek':
                return AnalyzerFactory._create_deepseek_analyzer(config_manager, language)
            elif ai_provider == 'openai':
                return AnalyzerFactory._create_openai_analyzer(config_manager, language)
            elif ai_provider == 'gemini':
                return AnalyzerFactory._create_gemini_analyzer(config_manager, language)
            else:
                raise ValueError(f"Unsupported AI provider: {ai_provider}")
                
        except Exception as e:
            logger.error(f"Failed to create AI analyzer: {e}")
            logger.info("Falling back to DeepSeek analyzer")
            return AnalyzerFactory._create_deepseek_analyzer(config_manager, language)
    
    @staticmethod
    def _create_deepseek_analyzer(config_manager, language: str) -> DeepSeekAnalyzer:
        """Create DeepSeek analyzer"""
        deepseek_config = config_manager.get_deepseek_config()
        return DeepSeekAnalyzer(
            api_key=deepseek_config['api_key'],
            base_url=deepseek_config['base_url'],
            model=deepseek_config['model'],
            language=language
        )
    
    @staticmethod
    def _create_openai_analyzer(config_manager, language: str) -> OpenAIAnalyzer:
        """Create OpenAI analyzer"""
        openai_config = config_manager.get_openai_config()
        return OpenAIAnalyzer(
            api_key=openai_config['api_key'],
            base_url=openai_config['base_url'],
            model=openai_config['model'],
            language=language
        )
    
    @staticmethod
    def _create_gemini_analyzer(config_manager, language: str) -> GeminiAnalyzer:
        """Create Gemini analyzer"""
        gemini_config = config_manager.get_gemini_config()
        return GeminiAnalyzer(
            api_key=gemini_config['api_key'],
            model=gemini_config['model'],
            language=language
        )
    
    @staticmethod
    def get_supported_providers() -> Dict[str, Dict[str, Any]]:
        """
        Get information about supported AI providers
        
        Returns:
            Dictionary with provider information
        """
        return {
            'deepseek': {
                'name': 'DeepSeek',
                'description': 'DeepSeek AI API',
                'website': 'https://platform.deepseek.com/',
                'pricing': 'Free: 5000 chars/month, Paid: $49/month for 10K requests',
                'required_env': ['DEEPSEEK_API_KEY']
            },
            'openai': {
                'name': 'OpenAI',
                'description': 'OpenAI GPT API',
                'website': 'https://platform.openai.com/',
                'pricing': 'Pay-per-use, varies by model',
                'required_env': ['OPENAI_API_KEY']
            },
            'gemini': {
                'name': 'Google Gemini',
                'description': 'Google Gemini AI API',
                'website': 'https://ai.google.dev/',
                'pricing': 'Free tier available, pay-per-use',
                'required_env': ['GEMINI_API_KEY']
            }
        }