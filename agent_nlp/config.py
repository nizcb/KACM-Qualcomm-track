"""
Configuration simplifiée pour l'Agent NLP MCP
"""

from dataclasses import dataclass
import os

@dataclass
class NLPAgentConfig:
    """Configuration pour l'agent NLP MCP"""
    
    # Configuration des logs
    log_level: str = "INFO"
    log_dir: str = "logs"
    
    # Configuration de l'IA
    ollama_base_url: str = "http://localhost:11434"
    llama_model: str = "llama3.2:latest"
    use_ai_analysis: bool = True
    offline_mode: bool = False
    
    # Limites de traitement
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    max_text_length: int = 10000
    
    # Répertoires de travail
    temp_dir: str = "temp"
    output_dir: str = "output"
    results_dir: str = "results"
    
    def __post_init__(self):
        # Création des répertoires nécessaires
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)

# Configuration par défaut
DEFAULT_CONFIG = NLPAgentConfig()

# Configuration pour développement
DEV_CONFIG = NLPAgentConfig(
    log_level="DEBUG",
    use_ai_analysis=True,
    offline_mode=False,
    max_file_size=10 * 1024 * 1024,  # 10MB pour les tests
    max_text_length=5000
)

# Configuration pour production
PROD_CONFIG = NLPAgentConfig(
    log_level="WARNING",
    use_ai_analysis=True,
    offline_mode=False,
    max_file_size=500 * 1024 * 1024,  # 500MB
    max_text_length=50000
)
