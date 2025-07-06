"""
Configuration Centralisée - Système Multi-Agents MCP
====================================================

Configuration globale pour tous les agents du système.
"""

from dataclasses import dataclass
from typing import Dict, List
import os

@dataclass
class AgentConfig:
    """Configuration de base pour tous les agents"""
    
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

@dataclass
class NLPAgentConfig(AgentConfig):
    """Configuration spécifique pour l'agent NLP"""
    
    # Extensions supportées
    supported_extensions: List[str] = None
    
    # Configuration PDF
    use_pymupdf: bool = True
    use_pypdf2: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        if self.supported_extensions is None:
            self.supported_extensions = ['.txt', '.md', '.pdf', '.json', '.csv', '.xml', '.html']

@dataclass
class VisionAgentConfig(AgentConfig):
    """Configuration spécifique pour l'agent Vision"""
    
    # Extensions supportées
    supported_extensions: List[str] = None
    
    # Configuration OCR
    ocr_languages: List[str] = None
    use_gpu: bool = False
    
    # Configuration NSFW
    nsfw_threshold: float = 0.6
    nsfw_model_path: str = "ai_models/nsfw/nsfw_model.onnx"
    
    def __post_init__(self):
        super().__post_init__()
        if self.supported_extensions is None:
            self.supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        if self.ocr_languages is None:
            self.ocr_languages = ['fr', 'en']

@dataclass
class AudioAgentConfig(AgentConfig):
    """Configuration spécifique pour l'agent Audio"""
    
    # Extensions supportées
    supported_extensions: List[str] = None
    
    # Configuration audio
    sample_rate: int = 44100
    max_duration: int = 300  # 5 minutes
    
    def __post_init__(self):
        super().__post_init__()
        if self.supported_extensions is None:
            self.supported_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']

@dataclass
class FileManagerConfig(AgentConfig):
    """Configuration spécifique pour le gestionnaire de fichiers"""
    
    # Configuration des rapports
    report_format: str = "json"  # json, html, pdf
    keep_history: bool = True
    max_history_days: int = 30
    
    # Configuration des statistiques
    enable_stats: bool = True
    stats_interval: int = 3600  # 1 heure

@dataclass
class SecurityAgentConfig(AgentConfig):
    """Configuration spécifique pour l'agent de sécurité"""
    
    # Configuration de chiffrement
    encryption_algorithm: str = "AES-256"
    key_length: int = 32
    
    # Configuration des actions
    default_action: str = "quarantine"  # quarantine, encrypt, notify
    enable_audit: bool = True
    
    # Configuration des notifications
    notify_on_warning: bool = True
    notification_methods: List[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.notification_methods is None:
            self.notification_methods = ["log", "email"]

@dataclass
class OrchestratorConfig(AgentConfig):
    """Configuration spécifique pour l'orchestrateur"""
    
    # Configuration des agents
    agent_endpoints: Dict[str, str] = None
    max_concurrent_files: int = 10
    retry_count: int = 3
    
    # Configuration des timeouts
    agent_timeout: int = 120  # 2 minutes
    batch_timeout: int = 3600  # 1 heure
    
    def __post_init__(self):
        super().__post_init__()
        if self.agent_endpoints is None:
            self.agent_endpoints = {
                'nlp': 'http://localhost:8002',
                'vision': 'http://localhost:8003',
                'audio': 'http://localhost:8004',
                'file_manager': 'http://localhost:8005',
                'security': 'http://localhost:8006'
            }

# ──────────────────────────────────────────────────────────────────────────
# Configurations par défaut pour chaque environnement
# ──────────────────────────────────────────────────────────────────────────

# Configuration par défaut
DEFAULT_CONFIG = AgentConfig()

# Configuration pour développement
DEV_CONFIG = AgentConfig(
    log_level="DEBUG",
    use_ai_analysis=True,
    offline_mode=False,
    max_file_size=10 * 1024 * 1024,  # 10MB pour les tests
    max_text_length=5000
)

# Configuration pour production
PROD_CONFIG = AgentConfig(
    log_level="INFO",
    use_ai_analysis=True,
    offline_mode=False,
    max_file_size=100 * 1024 * 1024,  # 100MB
    max_text_length=50000
)

# Configuration pour tests
TEST_CONFIG = AgentConfig(
    log_level="WARNING",
    use_ai_analysis=False,
    offline_mode=True,
    max_file_size=1024 * 1024,  # 1MB
    max_text_length=1000
)

# ──────────────────────────────────────────────────────────────────────────
# Configuration MCP
# ──────────────────────────────────────────────────────────────────────────

MCP_CONFIG = {
    'orchestrator': {'port': 8001, 'host': 'localhost'},
    'nlp': {'port': 8002, 'host': 'localhost'},
    'vision': {'port': 8003, 'host': 'localhost'},
    'audio': {'port': 8004, 'host': 'localhost'},
    'file_manager': {'port': 8005, 'host': 'localhost'},
    'security': {'port': 8006, 'host': 'localhost'}
}

# ──────────────────────────────────────────────────────────────────────────
# Fonctions utilitaires
# ──────────────────────────────────────────────────────────────────────────

def get_config_by_environment(env: str = "default") -> AgentConfig:
    """Retourne la configuration selon l'environnement"""
    configs = {
        "default": DEFAULT_CONFIG,
        "dev": DEV_CONFIG,
        "prod": PROD_CONFIG,
        "test": TEST_CONFIG
    }
    return configs.get(env, DEFAULT_CONFIG)

def get_agent_config(agent_type: str, env: str = "default"):
    """Retourne la configuration spécifique pour un agent"""
    base_config = get_config_by_environment(env)
    
    config_classes = {
        "nlp": NLPAgentConfig,
        "vision": VisionAgentConfig,
        "audio": AudioAgentConfig,
        "file_manager": FileManagerConfig,
        "security": SecurityAgentConfig,
        "orchestrator": OrchestratorConfig
    }
    
    config_class = config_classes.get(agent_type, AgentConfig)
    
    # Copier les valeurs de base
    config_dict = base_config.__dict__.copy()
    return config_class(**config_dict)

def get_mcp_endpoint(agent_type: str) -> str:
    """Retourne l'endpoint MCP pour un agent"""
    config = MCP_CONFIG.get(agent_type)
    if config:
        return f"http://{config['host']}:{config['port']}"
    return None
PROD_CONFIG = NLPAgentConfig(
    log_level="WARNING",
    use_ai_analysis=True,
    offline_mode=False,
    max_file_size=500 * 1024 * 1024,  # 500MB
    max_text_length=50000
)
