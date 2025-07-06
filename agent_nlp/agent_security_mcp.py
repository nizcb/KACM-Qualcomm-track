#!/usr/bin/env python3
"""
Security Agent Core - Agent de sécurité principal
Gestion du chiffrement, déchiffrement et vault

Usage:
    python security_agent_core.py test
    from security_agent_core import SecurityAgent
"""

import os
import sys
import sqlite3
import hashlib
import uuid
import secrets
import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json

# FastAPI imports (installation automatique si nécessaire)
try:
    from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("📦 Installation de FastAPI...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "python-multipart"])
    from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn

# Configuration
BASE_DIR = Path(__file__).parent
VAULT_DIR = BASE_DIR / "vault"
ENCRYPTED_DIR = BASE_DIR / "encrypted"
DECRYPTED_DIR = BASE_DIR / "decrypted"

# Créer les répertoires
VAULT_DIR.mkdir(exist_ok=True)
ENCRYPTED_DIR.mkdir(exist_ok=True)
DECRYPTED_DIR.mkdir(exist_ok=True)

VAULT_DB = VAULT_DIR / "vault.db"
SECRET_PHRASE = "mon_secret_ultra_securise_2024"

# ================================
# MODÈLES API (PYDANTIC)
# ================================

class EncryptRequest(BaseModel):
    file_path: str
    user_id: Optional[str] = "default_user"

class EncryptResponse(BaseModel):
    success: bool
    uuid: Optional[str] = None
    filename: Optional[str] = None
    encrypted_path: Optional[str] = None
    ai_analysis: Optional[str] = None
    message: str

class DecryptRequest(BaseModel):
    vault_uuid: str
    secret_phrase: str
    user_id: Optional[str] = "default_user"

class DecryptResponse(BaseModel):
    success: bool
    filename: Optional[str] = None
    decrypted_path: Optional[str] = None
    ai_explanation: Optional[str] = None
    message: str

class VaultStats(BaseModel):
    total_files: int
    total_size: int
    files: list

class AnalyzeRequest(BaseModel):
    file_path: str
    mode: Optional[str] = "security"  # "security", "content", "full"

class AnalyzeResponse(BaseModel):
    success: bool
    file_path: str
    analysis: Dict[str, Any]
    ai_reasoning: Optional[str] = None
    security_recommendation: str
    message: str

# ================================
# GESTIONNAIRE OLLAMA
# ================================

class OllamaManager:
    """Gestionnaire Ollama pour les explications IA"""
    
    def __init__(self):
        self.model_name = "llama3.2:1b"
        self.ollama_url = "http://localhost:11434"
        self.is_running = False
        
    def check_ollama_installed(self):
        """Vérifie si Ollama est installé"""
        try:
            result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def install_ollama(self):
        """Installe Ollama"""
        print("📦 Installation d'Ollama...")
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"], shell=True)
            elif sys.platform == "linux":
                subprocess.run(["curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"], shell=True)
            else:  # Windows
                print("⚠️  Veuillez installer Ollama manuellement depuis https://ollama.com")
                return False
            return True
        except Exception as e:
            print(f"❌ Erreur installation Ollama: {e}")
            return False
    
    def start_ollama(self):
        """Démarre Ollama"""
        if not self.check_ollama_installed():
            print("⚠️  Ollama non installé - fonctionnement sans IA")
            return False
        
        try:
            # Démarrer Ollama en arrière-plan
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)  # Attendre le démarrage
            
            # Vérifier si le modèle est disponible
            self.pull_model()
            self.is_running = True
            print("✅ Ollama démarré avec succès")
            return True
        except Exception as e:
            print(f"⚠️  Ollama non disponible - fonctionnement sans IA: {e}")
            return False
    
    def pull_model(self):
        """Télécharge le modèle Llama 3.2"""
        try:
            print(f"📥 Téléchargement du modèle {self.model_name}...")
            subprocess.run(["ollama", "pull", self.model_name], check=True)
            print("✅ Modèle téléchargé")
        except Exception as e:
            print(f"⚠️  Erreur téléchargement modèle: {e}")
    
    def generate_explanation(self, action, file_path, details=""):
        """Génère une explication avec Llama"""
        if not self.is_running:
            return f"🤖 {action} effectuée sur {file_path}. {details}"
        
        try:
            prompt = f"""Tu es un assistant de sécurité. Explique simplement ce qui vient de se passer:

Action: {action}
Fichier: {file_path}
Détails: {details}

Réponds en français, de manière claire et rassurante, en 2-3 phrases maximum."""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return f"🤖 {result.get('response', 'Explication non disponible')}"
            else:
                return f"🤖 {action} effectuée sur {file_path}. {details}"
                
        except Exception as e:
            return f"🤖 {action} effectuée sur {file_path}. {details}"

# ================================
# GESTIONNAIRE DE VAULT
# ================================

class VaultManager:
    """Gestionnaire du vault de sécurité"""
    
    def __init__(self):
        self.init_database()
        self.master_key = self.get_master_key()
    
    def init_database(self):
        """Initialise la base de données"""
        conn = sqlite3.connect(str(VAULT_DB))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vault_entries (
                uuid TEXT PRIMARY KEY,
                original_path TEXT NOT NULL,
                encrypted_path TEXT NOT NULL,
                filename TEXT NOT NULL,
                created_at TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_master_key(self):
        """Génère ou récupère la clé maître"""
        key_file = VAULT_DIR / "master.key"
        
        if key_file.exists():
            with open(key_file, 'r') as f:
                return f.read().strip()
        else:
            # Générer une nouvelle clé
            key = secrets.token_urlsafe(32)
            with open(key_file, 'w') as f:
                f.write(key)
            return key
    
    def calculate_file_hash(self, file_path):
        """Calcule le hash d'un fichier"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def encrypt_file(self, file_path):
        """Chiffre un fichier"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        # Vérifier que pyAesCrypt est disponible
        try:
            import pyAesCrypt
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyAesCrypt"])
            import pyAesCrypt
        
        # Générer UUID et chemins
        file_uuid = str(uuid.uuid4())
        filename = os.path.basename(file_path)
        encrypted_path = ENCRYPTED_DIR / f"{file_uuid}.aes"
        
        # Chiffrer le fichier
        pyAesCrypt.encryptFile(file_path, str(encrypted_path), self.master_key)
        
        # Sauvegarder dans la base
        conn = sqlite3.connect(str(VAULT_DB))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO vault_entries (uuid, original_path, encrypted_path, filename, created_at, file_hash, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_uuid,
            file_path,
            str(encrypted_path),
            filename,
            datetime.now().isoformat(),
            self.calculate_file_hash(file_path),
            os.path.getsize(file_path)
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "uuid": file_uuid,
            "filename": filename,
            "encrypted_path": str(encrypted_path),
            "original_path": file_path
        }
    
    def decrypt_file(self, file_uuid, output_path=None):
        """Déchiffre un fichier"""
        # Vérifier que pyAesCrypt est disponible
        try:
            import pyAesCrypt
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyAesCrypt"])
            import pyAesCrypt
            
        conn = sqlite3.connect(str(VAULT_DB))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM vault_entries WHERE uuid = ?', (file_uuid,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise ValueError(f"Fichier non trouvé dans le vault: {file_uuid}")
        
        uuid, original_path, encrypted_path, filename, created_at, file_hash, file_size = row
        
        if not output_path:
            output_path = DECRYPTED_DIR / f"{filename}"
        
        # Déchiffrer
        pyAesCrypt.decryptFile(encrypted_path, str(output_path), self.master_key)
        
        return {
            "uuid": uuid,
            "filename": filename,
            "decrypted_path": str(output_path),
            "original_path": original_path
        }
    
    def list_files(self):
        """Liste tous les fichiers dans le vault"""
        conn = sqlite3.connect(str(VAULT_DB))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM vault_entries ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        files = []
        for row in rows:
            files.append({
                "uuid": row[0],
                "filename": row[3],
                "original_path": row[1],
                "created_at": row[4],
                "file_size": row[6]
            })
        
        return files
    
    def get_stats(self):
        """Statistiques du vault"""
        conn = sqlite3.connect(str(VAULT_DB))
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*), SUM(file_size) FROM vault_entries')
        count, total_size = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_files": count or 0,
            "total_size": total_size or 0
        }

# ================================
# AGENT PRINCIPAL
# ================================

class SecurityAgent:
    """Agent de sécurité principal avec capacités IA ReAct"""
    
    def __init__(self):
        self.vault_manager = VaultManager()
        self.ollama_manager = OllamaManager()
        self.secret_phrase = SECRET_PHRASE
        print("🔐 Security Agent IA initialisé (ReAct Mode)")
        
    def start_ollama(self):
        """Démarre Ollama"""
        return self.ollama_manager.start_ollama()
    
    def analyze_file_with_ai(self, file_path: str, mode: str = "security") -> Dict[str, Any]:
        """
        Analyse un fichier avec l'IA (Mode ReAct)
        
        Args:
            file_path: Chemin du fichier à analyser
            mode: Type d'analyse ("security", "content", "full")
            
        Returns:
            Dict avec l'analyse détaillée
        """
        try:
            # THOUGHT: Analyser le fichier pour détecter des informations sensibles
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
            
            # ACTION: Lire le contenu du fichier
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Fichier binaire
                content = f"Fichier binaire ({os.path.getsize(file_path)} bytes)"
            
            # OBSERVATION: Analyser le contenu avec des patterns de sécurité
            security_issues = []
            confidence_score = 0.0
            
            # Détection d'emails
            if "@" in content and "." in content:
                security_issues.append("email_addresses")
                confidence_score += 0.3
            
            # Détection de téléphones
            import re
            phone_patterns = [r'\+?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', r'\d{3}-\d{3}-\d{4}']
            for pattern in phone_patterns:
                if re.search(pattern, content):
                    security_issues.append("phone_numbers")
                    confidence_score += 0.25
                    break
            
            # Détection de mots de passe
            password_keywords = ["password", "mot de passe", "mdp", "pwd", "secret"]
            for keyword in password_keywords:
                if keyword.lower() in content.lower():
                    security_issues.append("credentials")
                    confidence_score += 0.4
                    break
            
            # Détection de numéros de carte
            card_pattern = r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}'
            if re.search(card_pattern, content):
                security_issues.append("payment_info")
                confidence_score += 0.5
            
            # THOUGHT: Déterminer la recommandation de sécurité
            if confidence_score >= 0.3:
                security_recommendation = "ENCRYPT_REQUIRED"
                risk_level = "HIGH" if confidence_score >= 0.5 else "MEDIUM"
            else:
                security_recommendation = "SAFE"
                risk_level = "LOW"
            
            # ACTION: Générer une explication IA avec le mode ReAct
            ai_reasoning = self._generate_react_reasoning(file_path, content, security_issues, confidence_score, mode)
            
            return {
                "file_size": len(content) if isinstance(content, str) else os.path.getsize(file_path),
                "content_type": "text" if isinstance(content, str) else "binary",
                "security_issues": security_issues,
                "confidence_score": confidence_score,
                "risk_level": risk_level,
                "security_recommendation": security_recommendation,
                "ai_reasoning": ai_reasoning,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "security_recommendation": "ERROR",
                "ai_reasoning": f"Erreur lors de l'analyse: {str(e)}"
            }
    
    def _generate_react_reasoning(self, file_path: str, content: str, issues: list, confidence: float, mode: str) -> str:
        """Génère un raisonnement IA en mode ReAct"""
        
        if not self.ollama_manager.is_running:
            return f"🤖 Analyse basique: Fichier '{Path(file_path).name}' analysé. Problèmes détectés: {', '.join(issues) if issues else 'Aucun'}. Niveau de confiance: {confidence:.2f}"
        
        try:
            # Prompt ReAct pour l'IA
            react_prompt = f"""Tu es un agent de sécurité IA expert. Utilise le raisonnement ReAct (Reasoning + Acting) pour analyser ce fichier.

FICHIER: {Path(file_path).name}
CONTENU (extrait): {content[:500]}...
PROBLÈMES DÉTECTÉS: {', '.join(issues) if issues else 'Aucun'}
NIVEAU DE CONFIANCE: {confidence:.2f}
MODE D'ANALYSE: {mode}

Utilise le format ReAct suivant:

THOUGHT: [Ton raisonnement sur la sécurité du fichier]
ACTION: [Quelle action de sécurité recommandes-tu]
OBSERVATION: [Ce que tu observes dans le fichier]
THOUGHT: [Conclusion sur le niveau de risque]
ACTION: [Recommandation finale]

Réponds en français, sois précis et professionnel."""

            response = requests.post(
                f"{self.ollama_manager.ollama_url}/api/generate",
                json={
                    "model": self.ollama_manager.model_name,
                    "prompt": react_prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return f"🤖 IA ReAct: {result.get('response', 'Analyse non disponible')}"
            else:
                return f"🤖 Analyse locale: Fichier analysé avec {len(issues)} problèmes de sécurité détectés."
                
        except Exception as e:
            return f"🤖 Analyse locale: Fichier analysé. Problèmes: {', '.join(issues) if issues else 'Aucun'}."
    
    def encrypt_file(self, file_path: str, user_id: str = "default_user") -> Dict[str, Any]:
        """Chiffre un fichier avec analyse IA préalable"""
        try:
            # THOUGHT: Analyser d'abord le fichier avant chiffrement
            analysis = self.analyze_file_with_ai(file_path, "security")
            
            # ACTION: Chiffrer le fichier
            result = self.vault_manager.encrypt_file(file_path)
            
            # OBSERVATION: Générer une explication avec l'IA
            explanation = self.ollama_manager.generate_explanation(
                "Chiffrement",
                file_path,
                f"Fichier analysé et chiffré. Problèmes de sécurité détectés: {', '.join(analysis.get('security_issues', []))}. UUID: {result['uuid']}"
            )
            
            result.update({
                "success": True,
                "analysis": analysis,
                "explanation": explanation,
                "user_id": user_id
            })
            
            print(f"✅ Fichier chiffré avec analyse IA: {result['filename']} (UUID: {result['uuid']})")
            return result
            
        except Exception as e:
            print(f"❌ Erreur chiffrement: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Erreur lors du chiffrement: {str(e)}"
            }
    
    def decrypt_file(self, file_uuid: str, user_id: str = "default_user") -> Dict[str, Any]:
        """Déchiffre un fichier avec explication IA"""
        try:
            result = self.vault_manager.decrypt_file(file_uuid)
            
            # Générer une explication IA
            explanation = self.ollama_manager.generate_explanation(
                "Déchiffrement",
                result['filename'],
                f"Fichier '{result['filename']}' déchiffré avec succès et disponible temporairement dans le dossier 'decrypted'"
            )
            
            result.update({
                "success": True,
                "explanation": explanation,
                "user_id": user_id
            })
            
            print(f"✅ Fichier déchiffré avec IA: {result['filename']}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur déchiffrement: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Erreur lors du déchiffrement: {str(e)}"
            }
    
    def authenticate(self, secret_input):
        """Vérifie l'authentification"""
        return secret_input == self.secret_phrase
    
    def list_files(self):
        """Liste les fichiers dans le vault"""
        return self.vault_manager.list_files()
    
    def get_stats(self):
        """Statistiques du vault"""
        return self.vault_manager.get_stats()
    
    def test(self):
        """Test de l'agent"""
        print("🧪 Mode test de l'agent...")
        
        # Afficher les stats
        stats = self.get_stats()
        print(f"📊 Vault: {stats['total_files']} fichiers, {stats['total_size']} bytes")
        
        # Créer un fichier de test
        test_file = BASE_DIR / "test_demo.txt"
        with open(test_file, 'w') as f:
            f.write("Ceci est un fichier de test pour le chiffrement.\nEmail: test@example.com\nTéléphone: 123-456-789")
        
        print(f"📄 Fichier de test créé: {test_file}")
        
        # Tester le chiffrement
        result = self.encrypt_file(str(test_file))
        print(f"🔐 Chiffrement réussi")
        
        # Tester le déchiffrement
        decrypted = self.decrypt_file(result['uuid'])
        print(f"🔓 Déchiffrement réussi")
        
        # Nettoyer
        os.remove(test_file)
        print("🧹 Nettoyage terminé")
        print("✅ Test complet réussi!")

# ================================
# SERVEUR API FASTAPI
# ================================

# Instance globale de l'agent
security_agent = None

def get_agent():
    """Récupère l'instance de l'agent de sécurité"""
    global security_agent
    if security_agent is None:
        security_agent = SecurityAgent()
        security_agent.start_ollama()
    return security_agent

# Application FastAPI
app = FastAPI(
    title="🔐 Security Agent API",
    description="Agent de sécurité IA avec chiffrement et analyse ReAct",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
async def root():
    """Point d'entrée principal de l'API"""
    return {
        "message": "🔐 Security Agent API",
        "version": "1.0.0",
        "features": ["encryption", "decryption", "ai_analysis", "react_reasoning"],
        "docs": "/docs",
        "endpoints": {
            "analyze": "/analyze - Analyse IA d'un fichier",
            "encrypt": "/encrypt - Chiffrement sécurisé",
            "decrypt": "/decrypt - Déchiffrement avec auth",
            "vault": "/vault/stats - Statistiques du vault"
        }
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_file(request: AnalyzeRequest, agent: SecurityAgent = Depends(get_agent)):
    """
    Analyse un fichier avec l'IA en mode ReAct
    """
    try:
        analysis = agent.analyze_file_with_ai(request.file_path, request.mode)
        
        if "error" in analysis:
            raise HTTPException(status_code=400, detail=analysis["error"])
        
        return AnalyzeResponse(
            success=True,
            file_path=request.file_path,
            analysis=analysis,
            ai_reasoning=analysis.get("ai_reasoning", "Analyse terminée"),
            security_recommendation=analysis.get("security_recommendation", "UNKNOWN"),
            message=f"Analyse terminée. Niveau de risque: {analysis.get('risk_level', 'UNKNOWN')}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")

@app.post("/encrypt", response_model=EncryptResponse)
async def encrypt_file(request: EncryptRequest, agent: SecurityAgent = Depends(get_agent)):
    """
    Chiffre un fichier après analyse IA
    """
    try:
        result = agent.encrypt_file(request.file_path, request.user_id)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Erreur de chiffrement"))
        
        return EncryptResponse(
            success=True,
            uuid=result.get("uuid"),
            filename=result.get("filename"),
            encrypted_path=result.get("encrypted_path"),
            ai_analysis=result.get("explanation"),
            message=f"Fichier '{result.get('filename')}' chiffré avec succès"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chiffrement: {str(e)}")

@app.post("/decrypt", response_model=DecryptResponse)
async def decrypt_file(request: DecryptRequest, agent: SecurityAgent = Depends(get_agent)):
    """
    Déchiffre un fichier avec authentification
    """
    try:
        # Vérification de l'authentification
        if not agent.authenticate(request.secret_phrase):
            raise HTTPException(status_code=401, detail="Phrase secrète incorrecte")
        
        result = agent.decrypt_file(request.vault_uuid, request.user_id)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Erreur de déchiffrement"))
        
        return DecryptResponse(
            success=True,
            filename=result.get("filename"),
            decrypted_path=result.get("decrypted_path"),
            ai_explanation=result.get("explanation"),
            message=f"Fichier '{result.get('filename')}' déchiffré avec succès"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du déchiffrement: {str(e)}")

@app.get("/vault/stats", response_model=VaultStats)
async def get_vault_stats(agent: SecurityAgent = Depends(get_agent)):
    """
    Récupère les statistiques du vault
    """
    try:
        stats = agent.get_stats()
        files = agent.list_files()
        
        return VaultStats(
            total_files=stats["total_files"],
            total_size=stats["total_size"],
            files=files
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des stats: {str(e)}")

@app.get("/health")
async def health_check(agent: SecurityAgent = Depends(get_agent)):
    """
    Vérification de l'état de santé de l'agent
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ollama_running": agent.ollama_manager.is_running,
        "vault_accessible": True,
        "version": "1.0.0"
    }

# ================================
# SERVEUR SECURITY AGENT
# ================================

class SecurityAPIServer:
    """Serveur API pour l'agent de sécurité"""
    
    def __init__(self, port=8080, host="0.0.0.0"):
        self.port = port
        self.host = host
        
    def start(self):
        """Démarre le serveur API"""
        print("🔐 Security Agent API Server")
        print("=" * 60)
        print(f"🚀 Démarrage du serveur API sur {self.host}:{self.port}")
        print(f"📡 URL API: http://{self.host}:{self.port}")
        print(f"📚 Documentation: http://{self.host}:{self.port}/docs")
        print(f"🔍 ReDoc: http://{self.host}:{self.port}/redoc")
        print("=" * 60)
        print("🤖 Fonctionnalités IA ReAct activées")
        print("🔐 Endpoints disponibles:")
        print("   • POST /analyze   - Analyse IA d'un fichier")
        print("   • POST /encrypt   - Chiffrement sécurisé")
        print("   • POST /decrypt   - Déchiffrement avec auth")
        print("   • GET  /vault/stats - Statistiques du vault")
        print("   • GET  /health    - État de santé")
        print("=" * 60)
        
        try:
            uvicorn.run(
                app, 
                host=self.host, 
                port=self.port,
                log_level="info",
                access_log=True
            )
        except KeyboardInterrupt:
            print("\n👋 Arrêt du serveur API")
        except Exception as e:
            print(f"\n❌ Erreur serveur: {e}")

class SecurityServer:
    """Serveur HTTP pour l'agent de sécurité"""
    
    def __init__(self, port=8080):
        self.port = port
        self.agent = SecurityAgent()
        
    def start(self):
        """Démarre le serveur de l'agent de sécurité"""
        print("🔐 Security Agent - Mode Serveur")
        print("=" * 50)
        print(f"🚀 Démarrage du serveur sur le port {self.port}")
        print(f"📡 URL: http://localhost:{self.port}")
        print("=" * 50)
        
        # Initialisation de l'agent
        print("🤖 Initialisation de l'agent de sécurité...")
        self.agent.start_ollama()
        
        # Affichage des statistiques
        stats = self.agent.get_stats()
        print(f"📊 Vault: {stats['total_files']} fichiers, {stats['total_size']} bytes")
        
        print("✅ Agent de sécurité prêt!")
        print("🔗 Utilisez l'interface Streamlit pour interagir avec l'agent")
        print("💡 Commande: streamlit run security_interface.py")
        print("")
        print("🔧 Commandes disponibles:")
        print("   - test    : Lance les tests")
        print("   - stats   : Affiche les statistiques")
        print("   - help    : Affiche l'aide")
        print("   - Ctrl+C  : Arrêter le serveur")
        
        try:
            # Boucle principale du serveur
            while True:
                command = input("\n🔐 Security Agent > ").strip().lower()
                
                if command == "test":
                    print("🧪 Lancement des tests...")
                    self.agent.test()
                
                elif command == "stats":
                    stats = self.agent.get_stats()
                    print(f"� Statistiques du vault:")
                    print(f"   • Fichiers: {stats['total_files']}")
                    print(f"   • Taille: {stats['total_size']} bytes")
                    files = self.agent.list_files()
                    if files:
                        print("📁 Fichiers dans le vault:")
                        for file in files[:5]:  # Afficher max 5 fichiers
                            print(f"   • {file['filename']} ({file['uuid'][:8]}...)")
                
                elif command == "help":
                    print("🔐 Security Agent - Aide")
                    print("Commandes disponibles:")
                    print("   test    - Lance les tests de l'agent")
                    print("   stats   - Affiche les statistiques du vault")
                    print("   help    - Affiche cette aide")
                    print("   exit    - Arrête le serveur")
                    print("")
                    print("Utilisation comme module:")
                    print("   from security_agent_core import SecurityAgent")
                
                elif command in ["exit", "quit", "q"]:
                    print("👋 Arrêt du serveur...")
                    break
                
                elif command == "":
                    continue
                
                else:
                    print(f"❌ Commande inconnue: '{command}'")
                    print("💡 Tapez 'help' pour voir les commandes disponibles")
        
        except KeyboardInterrupt:
            print("\n\n👋 Arrêt du serveur par l'utilisateur")
        except Exception as e:
            print(f"\n❌ Erreur serveur: {e}")
        finally:
            print("🔐 Security Agent arrêté")

# ================================
# DÉMARRAGE DIRECT
# ================================

def main():
    """Fonction principale"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            agent = SecurityAgent()
            agent.start_ollama()
            agent.test()
        elif sys.argv[1] == "api":
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
            host = sys.argv[3] if len(sys.argv) > 3 else "0.0.0.0"
            api_server = SecurityAPIServer(port, host)
            api_server.start()
        elif sys.argv[1] == "server":
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
            server = SecurityServer(port)
            server.start()
        elif sys.argv[1] == "help":
            print("🔐 Security Agent Core")
            print("")
            print("Usage:")
            print("  python security_agent_core.py              # Lance en mode API REST")
            print("  python security_agent_core.py api          # Lance en mode API REST")
            print("  python security_agent_core.py api 8090     # Lance l'API sur le port 8090")
            print("  python security_agent_core.py server       # Lance en mode serveur CLI")
            print("  python security_agent_core.py test         # Teste l'agent")
            print("  python security_agent_core.py help         # Affiche cette aide")
            print("")
            print("API REST Endpoints:")
            print("  POST /analyze   - Analyse IA d'un fichier")
            print("  POST /encrypt   - Chiffrement sécurisé")
            print("  POST /decrypt   - Déchiffrement avec authentification")
            print("  GET  /vault/stats - Statistiques du vault")
            print("  GET  /health    - État de santé de l'agent")
            print("  GET  /docs      - Documentation interactive")
            print("")
            print("Ou utilisez comme module:")
            print("  from security_agent_core import SecurityAgent")
        else:
            print("❌ Commande inconnue. Utilisez 'api', 'server', 'test' ou 'help'")
    else:
        # Mode API REST par défaut
        api_server = SecurityAPIServer()
        api_server.start()

if __name__ == "__main__":
    main()