"""
🔒 Agent Security MCP Réel
=========================

Agent de sécurisation automatique des fichiers sensibles avec chiffrement.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import base64
import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Ajout du répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from mcp.server.fastmcp import FastMCP
    from pydantic import BaseModel
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP non disponible pour Agent Security")
    MCP_AVAILABLE = False

from config import Config

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOGS_DIR / "agent_security.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SecurityAction(BaseModel):
    """Action de sécurité effectuée"""
    action_type: str  # 'encrypt', 'quarantine', 'backup', 'alert'
    file_path: str
    vault_path: Optional[str]
    success: bool
    message: str
    timestamp: str

class SecurityReport(BaseModel):
    """Rapport de sécurisation"""
    session_id: str
    total_files_processed: int
    files_encrypted: int
    files_quarantined: int
    actions_performed: List[SecurityAction]
    vault_location: str
    created_at: str

class RealSecurityAgent:
    """Agent Security réel pour la sécurisation des fichiers"""
    
    def __init__(self):
        self.agent_name = "security"
        self.vault_dir = Config.VAULT_DIR
        self.password = Config.VAULT_PASSWORD
        self.vault_db = self.vault_dir / "vault.db"
        
        # Assurer l'existence du répertoire vault
        self.vault_dir.mkdir(exist_ok=True)
        
        # Initialiser la base de données du vault
        self.init_vault_database()
        
        logger.info(f"🔒 Agent Security MCP Réel initialisé - Vault: {self.vault_dir}")
    
    def init_vault_database(self):
        """Initialiser la base de données du vault"""
        try:
            with sqlite3.connect(self.vault_db) as conn:
                cursor = conn.cursor()
                
                # Table des fichiers chiffrés
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS encrypted_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_path TEXT,
                        vault_path TEXT,
                        file_hash TEXT,
                        encryption_method TEXT,
                        session_id TEXT,
                        reason TEXT,
                        created_at TEXT,
                        accessed_at TEXT
                    )
                ''')
                
                # Table des tentatives d'accès
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS access_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        vault_path TEXT,
                        action TEXT,
                        success BOOLEAN,
                        ip_address TEXT,
                        user_agent TEXT,
                        timestamp TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("✅ Base de données Vault initialisée")
                
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Vault DB: {e}")
    
    def generate_encryption_key(self, password: str, salt: bytes) -> bytes:
        """Générer une clé de chiffrement à partir d'un mot de passe"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_file(self, file_path: str, reason: str = "") -> tuple[bool, str, Optional[str]]:
        """Chiffrer un fichier et le déplacer dans le vault"""
        try:
            original_path = Path(file_path)
            if not original_path.exists():
                return False, f"Fichier non trouvé: {file_path}", None
            
            # Générer un salt unique
            salt = os.urandom(16)
            key = self.generate_encryption_key(self.password, salt)
            fernet = Fernet(key)
            
            # Lire et chiffrer le contenu
            with open(original_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = fernet.encrypt(file_data)
            
            # Calculer le hash du fichier original
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Créer le nom du fichier dans le vault
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            vault_filename = f"{original_path.stem}_{timestamp}.vault"
            vault_path = self.vault_dir / vault_filename
            
            # Sauvegarder le fichier chiffré avec le salt
            with open(vault_path, 'wb') as f:
                f.write(salt)  # Salt en premier
                f.write(encrypted_data)  # Puis données chiffrées
            
            # Enregistrer en base de données
            with sqlite3.connect(self.vault_db) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO encrypted_files 
                    (original_path, vault_path, file_hash, encryption_method, session_id, reason, created_at, accessed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(original_path),
                    str(vault_path),
                    file_hash,
                    "AES-256-Fernet",
                    datetime.now().strftime("%Y%m%d_%H%M%S"),
                    reason,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                conn.commit()
            
            # Supprimer le fichier original (optionnel, ici on fait une copie)
            # original_path.unlink()  # Décommenter pour supprimer l'original
            
            logger.info(f"✅ Fichier chiffré: {original_path.name} → {vault_filename}")
            return True, f"Fichier chiffré avec succès dans le vault", str(vault_path)
            
        except Exception as e:
            logger.error(f"❌ Erreur chiffrement {file_path}: {e}")
            return False, f"Erreur chiffrement: {e}", None
    
    def decrypt_file(self, vault_path: str, output_path: str = None) -> tuple[bool, str]:
        """Déchiffrer un fichier du vault"""
        try:
            vault_file = Path(vault_path)
            if not vault_file.exists():
                return False, f"Fichier vault non trouvé: {vault_path}"
            
            # Lire le fichier chiffré
            with open(vault_file, 'rb') as f:
                salt = f.read(16)  # Les 16 premiers bytes sont le salt
                encrypted_data = f.read()  # Le reste est les données chiffrées
            
            # Générer la clé avec le salt
            key = self.generate_encryption_key(self.password, salt)
            fernet = Fernet(key)
            
            # Déchiffrer
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Déterminer le chemin de sortie
            if output_path is None:
                # Utiliser le répertoire courant avec le nom original
                original_name = vault_file.stem.replace('_' + vault_file.stem.split('_')[-1], '')
                output_path = Path.cwd() / f"{original_name}_decrypted{Path(original_name).suffix}"
            
            # Sauvegarder le fichier déchiffré
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            # Logger l'accès
            self.log_vault_access(vault_path, "decrypt", True)
            
            logger.info(f"✅ Fichier déchiffré: {vault_file.name} → {output_path}")
            return True, f"Fichier déchiffré vers: {output_path}"
            
        except Exception as e:
            logger.error(f"❌ Erreur déchiffrement {vault_path}: {e}")
            self.log_vault_access(vault_path, "decrypt", False)
            return False, f"Erreur déchiffrement: {e}"
    
    def log_vault_access(self, vault_path: str, action: str, success: bool):
        """Logger les accès au vault"""
        try:
            with sqlite3.connect(self.vault_db) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO access_log 
                    (vault_path, action, success, ip_address, user_agent, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    vault_path,
                    action,
                    success,
                    "localhost",  # En mode local
                    "Security Agent",
                    datetime.now().isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Erreur log accès: {e}")
    
    def quarantine_file(self, file_path: str, reason: str = "") -> tuple[bool, str]:
        """Mettre un fichier en quarantaine"""
        try:
            original_path = Path(file_path)
            if not original_path.exists():
                return False, f"Fichier non trouvé: {file_path}"
            
            # Créer le répertoire de quarantaine
            quarantine_dir = self.vault_dir / "quarantine"
            quarantine_dir.mkdir(exist_ok=True)
            
            # Déplacer le fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_path = quarantine_dir / f"{original_path.stem}_{timestamp}{original_path.suffix}"
            
            # Copier le fichier en quarantaine
            import shutil
            shutil.copy2(original_path, quarantine_path)
            
            logger.info(f"⚠️ Fichier mis en quarantaine: {original_path.name} → {quarantine_path.name}")
            return True, f"Fichier mis en quarantaine: {quarantine_path}"
            
        except Exception as e:
            logger.error(f"❌ Erreur quarantaine {file_path}: {e}")
            return False, f"Erreur quarantaine: {e}"
    
    async def secure_files(self, session_id: str, sensitive_files: List[Dict[str, Any]]) -> SecurityReport:
        """Sécuriser une liste de fichiers sensibles"""
        logger.info(f"🔒 Sécurisation démarrée - Session: {session_id} - {len(sensitive_files)} fichiers")
        
        actions_performed = []
        files_encrypted = 0
        files_quarantined = 0
        
        for file_info in sensitive_files:
            file_path = file_info.get('file_path')
            reason = file_info.get('warning_reason', 'Détection automatique')
            pii_detected = file_info.get('pii_detected', [])
            
            # Déterminer le niveau de sensibilité
            pii_count = len(pii_detected) if pii_detected else 0
            
            if pii_count >= 3:  # Très sensible
                # Chiffrement + quarantaine
                success, message, vault_path = self.encrypt_file(file_path, f"PII détectées: {pii_count}")
                if success:
                    files_encrypted += 1
                    actions_performed.append(SecurityAction(
                        action_type="encrypt",
                        file_path=file_path,
                        vault_path=vault_path,
                        success=True,
                        message=message,
                        timestamp=datetime.now().isoformat()
                    ))
                    
                    # Quarantaine en plus
                    q_success, q_message = self.quarantine_file(file_path, f"Fichier très sensible - {pii_count} PII")
                    if q_success:
                        files_quarantined += 1
                        actions_performed.append(SecurityAction(
                            action_type="quarantine",
                            file_path=file_path,
                            vault_path=None,
                            success=True,
                            message=q_message,
                            timestamp=datetime.now().isoformat()
                        ))
                else:
                    actions_performed.append(SecurityAction(
                        action_type="encrypt",
                        file_path=file_path,
                        vault_path=None,
                        success=False,
                        message=message,
                        timestamp=datetime.now().isoformat()
                    ))
            
            elif pii_count > 0:  # Sensible
                # Chiffrement seulement
                success, message, vault_path = self.encrypt_file(file_path, f"PII détectées: {pii_count}")
                if success:
                    files_encrypted += 1
                
                actions_performed.append(SecurityAction(
                    action_type="encrypt",
                    file_path=file_path,
                    vault_path=vault_path,
                    success=success,
                    message=message,
                    timestamp=datetime.now().isoformat()
                ))
            
            else:
                # Alerte seulement
                actions_performed.append(SecurityAction(
                    action_type="alert",
                    file_path=file_path,
                    vault_path=None,
                    success=True,
                    message=f"Fichier signalé comme sensible: {reason}",
                    timestamp=datetime.now().isoformat()
                ))
        
        # Créer le rapport
        report = SecurityReport(
            session_id=session_id,
            total_files_processed=len(sensitive_files),
            files_encrypted=files_encrypted,
            files_quarantined=files_quarantined,
            actions_performed=actions_performed,
            vault_location=str(self.vault_dir),
            created_at=datetime.now().isoformat()
        )
        
        # Sauvegarder le rapport
        report_path = Config.LOGS_DIR / f"security_report_{session_id}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report.dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Sécurisation terminée: {files_encrypted} chiffrés, {files_quarantined} en quarantaine")
        logger.info(f"📄 Rapport sécurité sauvegardé: {report_path}")
        
        return report
    
    def list_vault_files(self) -> List[Dict[str, Any]]:
        """Lister les fichiers dans le vault"""
        try:
            with sqlite3.connect(self.vault_db) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT original_path, vault_path, file_hash, reason, created_at 
                    FROM encrypted_files 
                    ORDER BY created_at DESC
                ''')
                
                files = []
                for row in cursor.fetchall():
                    files.append({
                        "original_path": row[0],
                        "vault_path": row[1],
                        "file_hash": row[2],
                        "reason": row[3],
                        "created_at": row[4]
                    })
                
                return files
                
        except Exception as e:
            logger.error(f"❌ Erreur listage vault: {e}")
            return []

# ──────────────────────────────────────────────────────────────────────────
# Serveur MCP pour l'Agent Security
# ──────────────────────────────────────────────────────────────────────────

# Instance globale de l'agent
security_agent = RealSecurityAgent()

if MCP_AVAILABLE:
    # Serveur MCP
    mcp = FastMCP("Agent Security MCP Réel")

    @mcp.tool()
    async def secure_files(session_id: str, sensitive_files: List[Dict[str, Any]]) -> dict:
        """Sécuriser une liste de fichiers sensibles"""
        report = await security_agent.secure_files(session_id, sensitive_files)
        return report.dict()

    @mcp.tool()
    async def decrypt_file(vault_path: str, output_path: str = None) -> dict:
        """Déchiffrer un fichier du vault"""
        success, message = security_agent.decrypt_file(vault_path, output_path)
        return {
            "success": success,
            "message": message,
            "output_path": output_path
        }

    @mcp.tool()
    async def list_vault_files() -> dict:
        """Lister les fichiers dans le vault"""
        files = security_agent.list_vault_files()
        return {"vault_files": files}

    @mcp.tool()
    async def get_agent_status() -> dict:
        """Obtenir le statut de l'agent Security"""
        vault_files = security_agent.list_vault_files()
        return {
            "agent_name": security_agent.agent_name,
            "vault_directory": str(security_agent.vault_dir),
            "vault_database": str(security_agent.vault_db),
            "files_in_vault": len(vault_files)
        }

# ──────────────────────────────────────────────────────────────────────────
# Interface CLI et serveur HTTP simple
# ──────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

class SecureFilesRequest(BaseModel):
    session_id: str
    sensitive_files: List[Dict[str, Any]]

class DecryptFileRequest(BaseModel):
    vault_path: str
    output_path: Optional[str] = None

# API HTTP pour la compatibilité
app = FastAPI(title="Agent Security MCP Réel", version="1.0.0")

@app.post("/secure_files")
async def api_secure_files(request: SecureFilesRequest):
    """Endpoint HTTP pour la sécurisation"""
    try:
        report = await security_agent.secure_files(
            request.session_id, 
            request.sensitive_files
        )
        
        # Format compatible orchestrateur
        return {
            "actions": [action.dict() for action in report.actions_performed],
            "summary": {
                "total_processed": report.total_files_processed,
                "encrypted": report.files_encrypted,
                "quarantined": report.files_quarantined
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decrypt_file")
async def api_decrypt_file(request: DecryptFileRequest):
    """Endpoint HTTP pour le déchiffrement"""
    try:
        success, message = security_agent.decrypt_file(
            request.vault_path, 
            request.output_path
        )
        return {
            "success": success,
            "message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vault_files")
async def api_vault_files():
    """Lister les fichiers du vault"""
    files = security_agent.list_vault_files()
    return {"vault_files": files}

@app.get("/health")
async def health_check():
    """Check de santé de l'agent"""
    return {
        "status": "healthy",
        "agent": "security",
        "vault_ready": security_agent.vault_dir.exists()
    }

async def main():
    """Interface principale pour l'agent Security"""
    print("Démarrage du serveur Agent Security sur le port 8006...")
    config = uvicorn.Config(app, host="0.0.0.0", port=8006, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    if MCP_AVAILABLE:
        # Mode serveur MCP
        mcp.run()
    else:
        # Mode serveur HTTP
        asyncio.run(main())
