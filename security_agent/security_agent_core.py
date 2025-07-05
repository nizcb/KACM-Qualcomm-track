#!/usr/bin/env python3
"""
Security Agent Core - Agent de sécurité principal
Gestion du chiffrement, déchiffrement et vault

Usage:
    from security_agent_core import SecurityAgent
    agent = SecurityAgent()
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
            if not self.install_ollama():
                return False
        
        try:
            # Démarrer Ollama en arrière-plan
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)  # Attendre le démarrage
            
            # Vérifier si le modèle est disponible
            self.pull_model()
            self.is_running = True
            return True
        except Exception as e:
            print(f"❌ Erreur démarrage Ollama: {e}")
            return False
    
    def pull_model(self):
        """Télécharge le modèle Llama 3.2"""
        try:
            print(f"📥 Téléchargement du modèle {self.model_name}...")
            subprocess.run(["ollama", "pull", self.model_name], check=True)
            print("✅ Modèle téléchargé")
        except Exception as e:
            print(f"❌ Erreur téléchargement modèle: {e}")
    
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
    """Agent de sécurité principal"""
    
    def __init__(self):
        self.vault_manager = VaultManager()
        self.ollama_manager = OllamaManager()
        self.secret_phrase = SECRET_PHRASE
        
    def start_ollama(self):
        """Démarre Ollama"""
        return self.ollama_manager.start_ollama()
    
    def encrypt_file(self, file_path):
        """Chiffre un fichier et génère une explication"""
        try:
            result = self.vault_manager.encrypt_file(file_path)
            explanation = self.ollama_manager.generate_explanation(
                "Chiffrement",
                file_path,
                f"Le fichier a été chiffré avec succès et stocké dans le vault sécurisé avec l'UUID {result['uuid']}"
            )
            result["explanation"] = explanation
            return result
        except Exception as e:
            raise e
    
    def decrypt_file(self, file_uuid):
        """Déchiffre un fichier et génère une explication"""
        try:
            result = self.vault_manager.decrypt_file(file_uuid)
            explanation = self.ollama_manager.generate_explanation(
                "Déchiffrement",
                result['filename'],
                "Le fichier a été déchiffré avec succès et est maintenant disponible dans le dossier 'decrypted'"
            )
            result["explanation"] = explanation
            return result
        except Exception as e:
            raise e
    
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
        print(f"✅ Vault initialisé: {self.get_stats()}")
        
        # Créer un fichier de test
        test_file = BASE_DIR / "test_file.txt"
        with open(test_file, 'w') as f:
            f.write("Ceci est un fichier de test pour le chiffrement.")
        
        # Tester le chiffrement
        result = self.encrypt_file(str(test_file))
        print(f"✅ Fichier chiffré: {result['uuid']}")
        
        # Tester le déchiffrement
        decrypted = self.decrypt_file(result['uuid'])
        print(f"✅ Fichier déchiffré: {decrypted['decrypted_path']}")
        
        # Nettoyer
        os.remove(test_file)
        print("✅ Test terminé")

# ================================
# DÉMARRAGE DIRECT
# ================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        agent = SecurityAgent()
        agent.start_ollama()
        agent.test()
    else:
        print("🔐 Security Agent Core - Utilisez ce module dans votre interface")
        print("Pour tester: python security_agent_core.py test")
