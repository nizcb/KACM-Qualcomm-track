#!/usr/bin/env python3
"""
Security Agent MVP - Version Consolidée
Toutes les fonctionnalités dans un seul fichier pour faciliter l'intégration avec l'orchestrateur.

Architecture: Vision/NLP → File Manager → Security Agent (chiffrement + vault)
"""

import asyncio
import json
import logging
import os
import secrets
import sqlite3
import hashlib
import tempfile
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Imports externes
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import pyAesCrypt
import keyring

# ================================
# CONFIGURATION
# ================================

class Config:
    """Configuration centralisée pour Security Agent MVP."""
    
    def __init__(self):
        """Initialise la configuration."""
        # Directories
        self.vault_path = Path(os.getenv("SECURITY_AGENT_VAULT_PATH", Path(__file__).parent / "vault"))
        self.encrypted_path = Path(os.getenv("SECURITY_AGENT_ENCRYPTED_PATH", Path(__file__).parent / "encrypted"))
        self.decrypted_path = Path(os.getenv("SECURITY_AGENT_DECRYPTED_PATH", Path(__file__).parent / "decrypted"))
        
        # Database
        self.db_path = self.vault_path / "vault.db"
        
        # Security
        self.keyring_service = "neurosort_security_agent"
        self.keyring_username = "master_key"
        self.master_password_env = os.getenv("NEUROSORT_MASTER_PWD", "")
        
        # Server
        self.host = os.getenv("SECURITY_AGENT_HOST", "127.0.0.1")
        self.port = int(os.getenv("SECURITY_AGENT_PORT", "8001"))
        
        # MCP
        self.redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Créer les répertoires nécessaires."""
        for directory in [self.vault_path, self.encrypted_path, self.decrypted_path]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_master_key(self) -> str:
        """
        Récupère la clé maître depuis keyring ou crée une nouvelle.
        
        Returns:
            str: La clé maître
        """
        # Try keyring first
        master_key = keyring.get_password(self.keyring_service, self.keyring_username)
        
        if master_key:
            return master_key
        
        # Try environment variable (dev only)
        if self.master_password_env:
            # Store in keyring for future use
            keyring.set_password(self.keyring_service, self.keyring_username, self.master_password_env)
            return self.master_password_env
        
        # Generate new key
        new_key = secrets.token_urlsafe(32)
        keyring.set_password(self.keyring_service, self.keyring_username, new_key)
        return new_key
    
    def set_master_key(self, key: str):
        """
        Définit une nouvelle clé maître.
        
        Args:
            key: La nouvelle clé maître
        """
        keyring.set_password(self.keyring_service, self.keyring_username, key)


# ================================
# MODÈLES DE DONNÉES
# ================================

# === MCP Messages ===

class MCPTaskPayload(BaseModel):
    """Payload pour task.security du File Manager"""
    files: List[str] = Field(..., description="Liste des fichiers à chiffrer")
    owner: str = Field(..., description="Propriétaire des fichiers")
    policy: str = Field(default="AES256", description="Politique de chiffrement")

class MCPTaskRequest(BaseModel):
    """Message MCP entrant"""
    thread_id: str
    sender: str
    type: str = Field(default="task.security")
    payload: MCPTaskPayload

class MCPVaultEntry(BaseModel):
    """Entrée dans le vault pour MCP"""
    orig: str = Field(..., description="Chemin original du fichier")
    vault_path: str = Field(..., description="Chemin dans le vault")
    hash: str = Field(..., description="Hash SHA-256 du fichier chiffré")
    uuid: str = Field(..., description="UUID unique du fichier")
    timestamp: str = Field(..., description="Timestamp ISO 8601")

class MCPTaskResponse(BaseModel):
    """Message MCP sortant"""
    thread_id: str
    sender: str = Field(default="security_agent")
    type: str = Field(default="result.security")
    payload: dict

# === API HTTP ===

class EncryptRequest(BaseModel):
    """Requête de chiffrement ad-hoc"""
    file_path: str = Field(..., description="Chemin du fichier à chiffrer")
    owner: Optional[str] = Field(default="unknown")
    policy: str = Field(default="AES256")

class DecryptRequest(BaseModel):
    """Requête de déchiffrement"""
    vault_uuid: str = Field(..., description="UUID du fichier dans le vault")
    output_path: Optional[str] = Field(default=None, description="Chemin de sortie optionnel")

class VaultEntry(BaseModel):
    """Entrée dans le vault"""
    vault_uuid: str
    original_path: str
    vault_path: str
    file_hash: str
    owner: str
    policy: str
    created_at: str

class VaultStatusResponse(BaseModel):
    """Statut du vault"""
    total_files: int
    total_size_bytes: int
    vault_path: str
    entries: List[VaultEntry]


# ================================
# MODULE CRYPTOGRAPHIQUE
# ================================

class SecurityCrypto:
    """Gestionnaire de chiffrement pour Security Agent MVP"""
    
    def __init__(self, config: Config):
        self.config = config
        self.buffer_size = 64 * 1024  # 64KB buffer
        self.salt_size = 16  # 16 bytes salt
        self.uuid_length = 3  # 3 bytes = 6 hex chars
        
    def encrypt_file(self, file_path: str, vault_uuid: str, owner: str = "unknown") -> tuple[str, str]:
        """
        Chiffre un fichier selon la spécification MVP
        
        Args:
            file_path: Chemin du fichier à chiffrer
            vault_uuid: UUID unique pour le fichier
            owner: Propriétaire du fichier
            
        Returns:
            tuple: (Chemin du fichier chiffré, salt utilisé)
        """
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        # 1. Générer chemin vault avec extension .aes
        vault_path = self.config.encrypted_path / f"{vault_uuid}.aes"
        
        # 2. Générer salt unique
        salt = secrets.token_bytes(self.salt_size)
        
        # 3. Récupérer password maître
        master_password = self.config.get_master_key()
        
        # 4. Combiner password + salt pour le chiffrement
        combined_password = master_password + salt.hex()
        
        # 5. Chiffrer le fichier
        pyAesCrypt.encryptFile(
            str(source_path),
            str(vault_path),
            combined_password,
            self.buffer_size
        )
        
        return str(vault_path), salt.hex()
    
    def decrypt_file(self, vault_path: str, output_path: str, salt_hex: str) -> str:
        """
        Déchiffre un fichier du vault
        
        Args:
            vault_path: Chemin du fichier chiffré
            output_path: Chemin de sortie pour le fichier déchiffré
            salt_hex: Salt utilisé pour le chiffrement (format hex)
            
        Returns:
            str: Chemin du fichier déchiffré
        """
        vault_file = Path(vault_path)
        if not vault_file.exists():
            raise FileNotFoundError(f"Fichier vault non trouvé: {vault_path}")
        
        # Récupérer le password maître
        master_password = self.config.get_master_key()
        
        # Reconstruire le password combiné avec le salt
        combined_password = master_password + salt_hex
        
        # Créer le répertoire de sortie si nécessaire
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Déchiffrer le fichier
        pyAesCrypt.decryptFile(
            str(vault_file),
            str(output_file),
            combined_password,
            self.buffer_size
        )
        
        return str(output_file)
    
    def calculate_file_hash(self, file_path: str) -> str:
        """
        Calcule le hash SHA-256 d'un fichier
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            str: Hash SHA-256 au format hexadécimal
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


# ================================
# GESTIONNAIRE DE VAULT
# ================================

class VaultManager:
    """Gestionnaire du vault et de la base SQLite"""
    
    def __init__(self, config: Config):
        self.config = config
        self.db_path = self.config.db_path
        self.init_vault()
    
    def init_vault(self):
        """Initialise le vault et la base de données"""
        # Créer les répertoires
        self.config.vault_path.mkdir(parents=True, exist_ok=True)
        self.config.encrypted_path.mkdir(parents=True, exist_ok=True)
        self.config.decrypted_path.mkdir(parents=True, exist_ok=True)
        
        # Initialiser la base de données
        self._init_database()
    
    def _init_database(self):
        """Initialise la base de données SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vault_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vault_uuid TEXT UNIQUE NOT NULL,
                    original_path TEXT NOT NULL,
                    vault_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    policy TEXT NOT NULL DEFAULT 'AES256',
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def register_file(self, original_path: str, vault_path: str, file_hash: str, 
                     vault_uuid: str, owner: str, salt_hex: str, policy: str = "AES256") -> VaultEntry:
        """
        Enregistre un fichier dans le vault
        
        Args:
            original_path: Chemin original du fichier
            vault_path: Chemin du fichier chiffré
            file_hash: Hash SHA-256 du fichier
            vault_uuid: UUID unique du fichier
            owner: Propriétaire du fichier
            salt_hex: Salt utilisé pour le chiffrement
            policy: Politique de chiffrement
            
        Returns:
            VaultEntry: Entrée du vault
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO vault_entries 
                (vault_uuid, original_path, vault_path, file_hash, owner, policy, salt)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (vault_uuid, original_path, vault_path, file_hash, owner, policy, salt_hex))
            conn.commit()
        
        return VaultEntry(
            vault_uuid=vault_uuid,
            original_path=original_path,
            vault_path=vault_path,
            file_hash=file_hash,
            owner=owner,
            policy=policy,
            created_at=datetime.utcnow().isoformat() + "Z"
        )
    
    def get_entry_by_uuid(self, vault_uuid: str) -> Optional[VaultEntry]:
        """
        Récupère une entrée par UUID
        
        Args:
            vault_uuid: UUID du fichier
            
        Returns:
            VaultEntry ou None si non trouvé
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT vault_uuid, original_path, vault_path, file_hash, owner, policy, created_at, salt
                FROM vault_entries WHERE vault_uuid = ?
            ''', (vault_uuid,))
            
            row = cursor.fetchone()
            if row:
                return VaultEntry(
                    vault_uuid=row[0],
                    original_path=row[1],
                    vault_path=row[2],
                    file_hash=row[3],
                    owner=row[4],
                    policy=row[5],
                    created_at=row[6]
                ), row[7]  # Retourner aussi le salt
        return None, None
    
    def get_all_entries(self) -> List[VaultEntry]:
        """
        Récupère toutes les entrées du vault
        
        Returns:
            List[VaultEntry]: Liste de toutes les entrées
        """
        entries = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT vault_uuid, original_path, vault_path, file_hash, owner, policy, created_at
                FROM vault_entries ORDER BY created_at DESC
            ''')
            
            for row in cursor.fetchall():
                entries.append(VaultEntry(
                    vault_uuid=row[0],
                    original_path=row[1],
                    vault_path=row[2],
                    file_hash=row[3],
                    owner=row[4],
                    policy=row[5],
                    created_at=row[6]
                ))
        return entries
    
    def get_vault_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du vault
        
        Returns:
            Dict: Statistiques du vault
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM vault_entries')
            total_files = cursor.fetchone()[0]
        
        # Calculer la taille totale
        total_size = 0
        for entry in self.get_all_entries():
            vault_file = Path(entry.vault_path)
            if vault_file.exists():
                total_size += vault_file.stat().st_size
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "vault_path": str(self.config.vault_path)
        }


# ================================
# SECURITY AGENT PRINCIPAL
# ================================

class SecurityAgent:
    """Agent de sécurité principal - Version consolidée"""
    
    def __init__(self):
        """Initialise l'agent de sécurité"""
        self.config = Config()
        self.crypto = SecurityCrypto(self.config)
        self.vault_manager = VaultManager(self.config)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # MCP message queue (en production, utiliser Redis/RabbitMQ)
        self.mcp_message_queue: Dict[str, Dict] = {}
        self.mcp_results_queue: Dict[str, Dict] = {}
    
    async def process_mcp_task(self, task: MCPTaskRequest) -> MCPTaskResponse:
        """
        Traite une tâche MCP de chiffrement
        
        Args:
            task: Tâche MCP à traiter
            
        Returns:
            MCPTaskResponse: Réponse avec les résultats
        """
        self.logger.info(f"🔄 Processing MCP task {task.thread_id} from {task.sender}")
        
        vault_entries = []
        
        for file_path in task.payload.files:
            try:
                # Générer UUID unique
                file_uuid = str(uuid.uuid4())[:8]
                
                # Chiffrer le fichier
                vault_path, salt_hex = self.crypto.encrypt_file(
                    file_path=file_path,
                    vault_uuid=file_uuid,
                    owner=task.payload.owner
                )
                
                # Calculer hash
                file_hash = self.crypto.calculate_file_hash(vault_path)
                
                # Enregistrer dans le vault
                vault_entry = self.vault_manager.register_file(
                    original_path=file_path,
                    vault_path=vault_path,
                    file_hash=file_hash,
                    vault_uuid=file_uuid,
                    owner=task.payload.owner,
                    salt_hex=salt_hex,
                    policy=task.payload.policy
                )
                
                # Créer entrée MCP
                mcp_entry = MCPVaultEntry(
                    orig=file_path,
                    vault_path=vault_path,
                    hash=f"SHA256:{file_hash}",
                    uuid=file_uuid,
                    timestamp=vault_entry.created_at
                )
                
                vault_entries.append(mcp_entry.dict())
                
                self.logger.info(f"✅ Encrypted: {file_path} -> {file_uuid}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to encrypt {file_path}: {e}")
                # Continuer avec les autres fichiers
        
        # Créer réponse MCP
        response = MCPTaskResponse(
            thread_id=task.thread_id,
            sender="security_agent",
            type="result.security",
            payload={"vault": vault_entries}
        )
        
        self.logger.info(f"✅ MCP task {task.thread_id} completed: {len(vault_entries)} files encrypted")
        
        return response
    
    async def encrypt_file_api(self, request: EncryptRequest) -> VaultEntry:
        """
        Chiffre un fichier via l'API HTTP
        
        Args:
            request: Requête de chiffrement
            
        Returns:
            VaultEntry: Entrée du vault
        """
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail=f"Path is not a file: {request.file_path}")
        
        # Générer UUID unique
        file_uuid = str(uuid.uuid4())[:8]
        
        try:
            # Chiffrer le fichier
            vault_path, salt_hex = self.crypto.encrypt_file(
                file_path=str(file_path),
                vault_uuid=file_uuid,
                owner=request.owner or "unknown"
            )
            
            # Calculer hash
            file_hash = self.crypto.calculate_file_hash(vault_path)
            
            # Enregistrer dans le vault
            vault_entry = self.vault_manager.register_file(
                original_path=str(file_path),
                vault_path=vault_path,
                file_hash=file_hash,
                vault_uuid=file_uuid,
                owner=request.owner or "unknown",
                salt_hex=salt_hex,
                policy=request.policy
            )
            
            self.logger.info(f"✅ File encrypted via API: {file_path} -> {file_uuid}")
            
            return vault_entry
            
        except Exception as e:
            self.logger.error(f"❌ Encryption failed: {e}")
            raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")
    
    async def decrypt_file_api(self, request: DecryptRequest) -> Dict[str, str]:
        """
        Déchiffre un fichier via l'API HTTP
        
        Args:
            request: Requête de déchiffrement
            
        Returns:
            Dict: Informations sur le fichier déchiffré
        """
        # Récupérer l'entrée du vault
        vault_entry, salt_hex = self.vault_manager.get_entry_by_uuid(request.vault_uuid)
        if not vault_entry:
            raise HTTPException(status_code=404, detail=f"Vault entry not found: {request.vault_uuid}")
        
        # Déterminer le chemin de sortie
        if request.output_path:
            output_path = request.output_path
        else:
            # Utiliser le répertoire decrypted avec le nom original
            original_name = Path(vault_entry.original_path).name
            output_path = str(self.config.decrypted_path / f"{original_name}_{request.vault_uuid}")
        
        try:
            # Déchiffrer le fichier
            decrypted_path = self.crypto.decrypt_file(
                vault_path=vault_entry.vault_path,
                output_path=output_path,
                salt_hex=salt_hex
            )
            
            self.logger.info(f"✅ File decrypted via API: {request.vault_uuid} -> {decrypted_path}")
            
            return {
                "vault_uuid": request.vault_uuid,
                "original_path": vault_entry.original_path,
                "decrypted_path": decrypted_path,
                "owner": vault_entry.owner
            }
            
        except Exception as e:
            self.logger.error(f"❌ Decryption failed: {e}")
            raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")
    
    async def get_vault_status(self) -> VaultStatusResponse:
        """
        Récupère le statut du vault
        
        Returns:
            VaultStatusResponse: Statut complet du vault
        """
        entries = self.vault_manager.get_all_entries()
        stats = self.vault_manager.get_vault_stats()
        
        return VaultStatusResponse(
            total_files=stats["total_files"],
            total_size_bytes=stats["total_size_bytes"],
            vault_path=stats["vault_path"],
            entries=entries
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie la santé de l'agent
        
        Returns:
            Dict: Statut de santé
        """
        try:
            # Vérifier l'accès à la base de données
            stats = self.vault_manager.get_vault_stats()
            
            # Vérifier l'accès aux répertoires
            vault_accessible = self.config.vault_path.exists()
            encrypted_accessible = self.config.encrypted_path.exists()
            decrypted_accessible = self.config.decrypted_path.exists()
            
            # Vérifier l'accès à la clé maître
            master_key_accessible = bool(self.config.get_master_key())
            
            health_status = {
                "status": "healthy" if all([
                    vault_accessible, encrypted_accessible, 
                    decrypted_accessible, master_key_accessible
                ]) else "unhealthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "vault_path": str(self.config.vault_path),
                "total_files": stats["total_files"],
                "components": {
                    "vault_directory": vault_accessible,
                    "encrypted_directory": encrypted_accessible,
                    "decrypted_directory": decrypted_accessible,
                    "master_key": master_key_accessible,
                    "database": True  # Si on arrive ici, la DB fonctionne
                }
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": str(e)
            }


# ================================
# APPLICATION FASTAPI
# ================================

# Initialiser l'agent global
security_agent = SecurityAgent()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    security_agent.logger.info("🔐 Security Agent MVP starting...")
    
    # Initialize vault
    try:
        security_agent.vault_manager.init_vault()
        security_agent.logger.info(f"✅ Vault initialized at: {security_agent.config.vault_path}")
    except Exception as e:
        security_agent.logger.error(f"❌ Failed to initialize vault: {e}")
        raise
    
    # Start MCP consumer
    asyncio.create_task(mcp_consumer_loop())
    security_agent.logger.info("🚀 MCP consumer started")
    
    yield
    
    # Shutdown
    security_agent.logger.info("🔄 Security Agent shutting down...")


app = FastAPI(
    title="Security Agent MVP - Consolidated",
    description="Agent de sécurité pour chiffrement cryptographique et gestion de vault",
    version="1.0.0",
    lifespan=lifespan
)


# ================================
# ENDPOINTS HTTP
# ================================

@app.post("/encrypt", response_model=VaultEntry)
async def encrypt_file_endpoint(request: EncryptRequest):
    """
    Chiffre un fichier et le stocke dans le vault.
    
    Args:
        request: Requête de chiffrement
        
    Returns:
        VaultEntry: Informations sur le fichier chiffré
    """
    return await security_agent.encrypt_file_api(request)


@app.post("/decrypt")
async def decrypt_file_endpoint(request: DecryptRequest):
    """
    Déchiffre un fichier depuis le vault.
    
    Args:
        request: Requête de déchiffrement
        
    Returns:
        Dict: Informations sur le fichier déchiffré
    """
    return await security_agent.decrypt_file_api(request)


@app.get("/vault_status", response_model=VaultStatusResponse)
async def vault_status_endpoint():
    """
    Récupère le statut complet du vault.
    
    Returns:
        VaultStatusResponse: Statut du vault avec toutes les entrées
    """
    return await security_agent.get_vault_status()


@app.get("/health")
async def health_endpoint():
    """
    Vérifie la santé de l'agent.
    
    Returns:
        Dict: Statut de santé de l'agent
    """
    return await security_agent.health_check()


# ================================
# CONSOMMATEUR MCP
# ================================

async def mcp_consumer_loop():
    """
    Boucle de consommation des messages MCP.
    En production, ceci serait remplacé par Redis/RabbitMQ.
    """
    while True:
        try:
            # Simuler la réception de messages MCP
            if security_agent.mcp_message_queue:
                for thread_id, message in list(security_agent.mcp_message_queue.items()):
                    try:
                        # Traiter le message
                        task = MCPTaskRequest(**message)
                        response = await security_agent.process_mcp_task(task)
                        
                        # Stocker la réponse
                        security_agent.mcp_results_queue[thread_id] = response.dict()
                        
                        # Supprimer le message traité
                        del security_agent.mcp_message_queue[thread_id]
                        
                        security_agent.logger.info(f"✅ MCP message processed: {thread_id}")
                        
                    except Exception as e:
                        security_agent.logger.error(f"❌ MCP message processing failed: {e}")
                        # Supprimer le message défectueux
                        del security_agent.mcp_message_queue[thread_id]
            
            # Attendre avant la prochaine itération
            await asyncio.sleep(1)
            
        except Exception as e:
            security_agent.logger.error(f"❌ MCP consumer loop error: {e}")
            await asyncio.sleep(5)  # Attendre plus longtemps en cas d'erreur


# ================================
# ENDPOINT MCP (pour tests)
# ================================

@app.post("/mcp/task")
async def mcp_task_endpoint(task: MCPTaskRequest):
    """
    Endpoint pour recevoir des tâches MCP (pour tests et intégration).
    
    Args:
        task: Tâche MCP à traiter
        
    Returns:
        MCPTaskResponse: Réponse de la tâche
    """
    return await security_agent.process_mcp_task(task)


@app.get("/mcp/results/{thread_id}")
async def mcp_results_endpoint(thread_id: str):
    """
    Récupère les résultats d'une tâche MCP.
    
    Args:
        thread_id: ID du thread de la tâche
        
    Returns:
        Dict: Résultats de la tâche ou erreur 404
    """
    if thread_id in security_agent.mcp_results_queue:
        return security_agent.mcp_results_queue[thread_id]
    else:
        raise HTTPException(status_code=404, detail=f"No results found for thread: {thread_id}")


# ================================
# FONCTION PRINCIPALE
# ================================

def main():
    """
    Fonction principale pour démarrer l'agent de sécurité.
    """
    print("🔐 Security Agent MVP - Version Consolidée")
    print("=" * 50)
    
    # Vérifier la configuration
    config = Config()
    print(f"📂 Vault Path: {config.vault_path}")
    print(f"🔒 Encrypted Path: {config.encrypted_path}")
    print(f"🔓 Decrypted Path: {config.decrypted_path}")
    print(f"🌐 Server: {config.host}:{config.port}")
    
    # Démarrer le serveur
    uvicorn.run(
        "security_agent_consolidated:app",
        host=config.host,
        port=config.port,
        log_level="info",
        reload=False
    )


if __name__ == "__main__":
    main()
