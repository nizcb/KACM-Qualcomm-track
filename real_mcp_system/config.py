"""
Configuration du Système Multi-Agents MCP Réel
===============================================
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional

# Répertoire de base
BASE_DIR = Path(__file__).parent

@dataclass
class AgentConfig:
    """Configuration d'un agent MCP"""
    name: str
    script: str
    port: int
    description: str
    enabled: bool = True

# Configuration des agents
AGENTS_CONFIG = {
    'orchestrator': AgentConfig(
        name='orchestrator',
        script='agent_orchestrator_mcp.py',
        port=8001,
        description='Agent Orchestrateur - Coordination générale',
        enabled=True
    ),
    'nlp': AgentConfig(
        name='nlp', 
        script='agent_nlp_mcp.py',
        port=8002,
        description='Agent NLP - Traitement de texte avec IA',
        enabled=True
    ),
    'vision': AgentConfig(
        name='vision',
        script='agent_vision_mcp.py', 
        port=8003,
        description='Agent Vision - Traitement d\'images',
        enabled=True
    ),
    'audio': AgentConfig(
        name='audio',
        script='agent_audio_mcp.py',
        port=8004,
        description='Agent Audio - Traitement audio',
        enabled=True
    ),
    'file_manager': AgentConfig(
        name='file_manager',
        script='agent_file_manager_mcp.py',
        port=8005,
        description='Agent File Manager - Gestion des fichiers',
        enabled=True
    ),
    'security': AgentConfig(
        name='security',
        script='agent_security_mcp.py',
        port=8006,
        description='Agent Security - Sécurisation des données',
        enabled=True
    )
}

# Configuration générale
class Config:
    # Répertoires
    BASE_DIR = BASE_DIR
    AGENTS_DIR = BASE_DIR / "agents"
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    VAULT_DIR = BASE_DIR / "vault"
    
    # Configuration des agents
    AGENTS = AGENTS_CONFIG
    
    # Extensions supportées
    TEXT_EXTENSIONS = ['.txt', '.pdf', '.md', '.json', '.csv', '.xml', '.html', '.log', '.py', '.js', '.css']
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg']
    AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.mp4']
    
    # Configuration Ollama/Llama
    OLLAMA_HOST = "http://localhost:11434"
    OLLAMA_MODEL = "llama3.2:1b"
    
    # Configuration de sécurité
    VAULT_PASSWORD = "kacm_secure_2024"
    ENCRYPTION_ALGORITHM = "AES"
    ENCRYPTION_KEY_SIZE = 256
    
    # Configuration de l'interface
    INTERFACE_HOST = "localhost"
    INTERFACE_PORT = 8000
    
    # Configuration des logs
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Timeouts
    AGENT_STARTUP_TIMEOUT = 30  # secondes
    AGENT_RESPONSE_TIMEOUT = 60  # secondes
    
    # Monitoring
    HEALTH_CHECK_INTERVAL = 30  # secondes
    MAX_CONCURRENT_FILES = 10
    
    @classmethod
    def get_agent_endpoint(cls, agent_name: str) -> str:
        """Obtenir l'endpoint d'un agent"""
        if agent_name in cls.AGENTS:
            return f"http://localhost:{cls.AGENTS[agent_name].port}"
        raise ValueError(f"Agent inconnu: {agent_name}")
    
    @classmethod
    def get_enabled_agents(cls) -> List[str]:
        """Obtenir la liste des agents activés"""
        return [name for name, config in cls.AGENTS.items() if config.enabled]
    
    @classmethod
    def ensure_directories(cls):
        """Créer les répertoires nécessaires"""
        cls.AGENTS_DIR.mkdir(exist_ok=True)
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.VAULT_DIR.mkdir(exist_ok=True)

# Initialiser les répertoires
Config.ensure_directories()
