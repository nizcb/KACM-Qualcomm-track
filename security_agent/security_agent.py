#!/usr/bin/env python3
"""
Security Agent - Version Simplifiée
Agent de sécurité avec chiffrement et interface Streamlit

Usage:
    python security_agent.py

Fonctionnalités:
- Chiffrement/déchiffrement de fichiers
- Interface Streamlit simple
- Intégration Llama 3.2 pour les explications
- Authentification par phrase secrète
"""

import os
import sys
import sqlite3
import hashlib
import uuid
import secrets
import subprocess
import threading
import time
import requests
import json
from pathlib import Path
from datetime import datetime
import tempfile

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
SECRET_PHRASE = "mon_secret_ultra_securise_2024"  # Phrase secrète pour l'authentification

# ================================
# INSTALLATION DES DÉPENDANCES
# ================================

def install_dependencies():
    """Installe les dépendances nécessaires"""
    print("🔍 Vérification des dépendances...")
    
    packages = ["streamlit", "pyAesCrypt", "requests", "pandas"]
    
    for package in packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   📦 Installation de {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ Dépendances OK")

# Installation des dépendances
install_dependencies()

# Imports après installation
import streamlit as st
import pyAesCrypt
import pandas as pd

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
# INTERFACE STREAMLIT
# ================================

def main():
    """Interface principale Streamlit"""
    st.set_page_config(
        page_title="🔐 Security Agent",
        page_icon="🔐",
        layout="wide"
    )
    
    st.title("🔐 Security Agent - Chiffrement de Fichiers")
    st.markdown("---")
    
    # Initialiser les managers
    if 'vault_manager' not in st.session_state:
        st.session_state.vault_manager = VaultManager()
    
    if 'ollama_manager' not in st.session_state:
        st.session_state.ollama_manager = OllamaManager()
        # Démarrer Ollama en arrière-plan
        if not st.session_state.ollama_manager.is_running:
            with st.spinner("🚀 Démarrage d'Ollama..."):
                st.session_state.ollama_manager.start_ollama()
    
    # Sidebar pour les stats
    with st.sidebar:
        st.header("📊 Statistiques")
        stats = st.session_state.vault_manager.get_stats()
        st.metric("Fichiers chiffrés", stats["total_files"])
        st.metric("Taille totale", f"{stats['total_size']:,} bytes")
        
        st.markdown("---")
        st.header("🔑 Phrase secrète")
        st.info(f"Phrase actuelle: `{SECRET_PHRASE}`")
        st.caption("Cette phrase est nécessaire pour déchiffrer les fichiers")
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["🔒 Chiffrement", "🔓 Déchiffrement", "📁 Fichiers"])
    
    with tab1:
        st.header("🔒 Chiffrer un fichier")
        
        # Input pour le chemin du fichier
        file_path = st.text_input("📂 Chemin du fichier à chiffrer:", placeholder="/path/to/your/file.txt")
        
        if st.button("🔒 Chiffrer le fichier", type="primary"):
            if not file_path:
                st.error("❌ Veuillez saisir un chemin de fichier")
            elif not os.path.exists(file_path):
                st.error(f"❌ Fichier non trouvé: {file_path}")
            else:
                try:
                    with st.spinner("🔄 Chiffrement en cours..."):
                        # Chiffrer le fichier
                        result = st.session_state.vault_manager.encrypt_file(file_path)
                        
                        # Générer l'explication avec Llama
                        explanation = st.session_state.ollama_manager.generate_explanation(
                            "Chiffrement",
                            file_path,
                            f"Le fichier a été chiffré avec succès et stocké dans le vault sécurisé avec l'UUID {result['uuid']}"
                        )
                        
                        # Afficher les résultats
                        st.success("✅ Fichier chiffré avec succès!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.info("📋 Informations du fichier")
                            st.write(f"**Nom:** {result['filename']}")
                            st.write(f"**UUID:** {result['uuid']}")
                            st.write(f"**Chemin chiffré:** {result['encrypted_path']}")
                        
                        with col2:
                            st.info("🤖 Explication IA")
                            st.write(explanation)
                        
                        st.warning("⚠️ Gardez précieusement l'UUID pour pouvoir déchiffrer le fichier plus tard!")
                        
                except Exception as e:
                    st.error(f"❌ Erreur lors du chiffrement: {e}")
    
    with tab2:
        st.header("🔓 Déchiffrer un fichier")
        
        # Authentification
        secret_input = st.text_input("🔑 Phrase secrète:", type="password", placeholder="Saisissez la phrase secrète")
        
        if secret_input == SECRET_PHRASE:
            st.success("✅ Authentification réussie!")
            
            # Liste des fichiers disponibles
            files = st.session_state.vault_manager.list_files()
            
            if files:
                file_options = {f"{file['filename']} ({file['uuid'][:8]}...)": file['uuid'] for file in files}
                selected_file = st.selectbox("📁 Sélectionnez un fichier à déchiffrer:", options=list(file_options.keys()))
                
                if st.button("🔓 Déchiffrer le fichier", type="primary"):
                    try:
                        with st.spinner("🔄 Déchiffrement en cours..."):
                            selected_uuid = file_options[selected_file]
                            result = st.session_state.vault_manager.decrypt_file(selected_uuid)
                            
                            # Générer l'explication avec Llama
                            explanation = st.session_state.ollama_manager.generate_explanation(
                                "Déchiffrement",
                                result['filename'],
                                f"Le fichier a été déchiffré avec succès et est maintenant disponible dans le dossier 'decrypted'"
                            )
                            
                            # Afficher les résultats
                            st.success("✅ Fichier déchiffré avec succès!")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.info("📋 Informations du fichier")
                                st.write(f"**Nom:** {result['filename']}")
                                st.write(f"**UUID:** {result['uuid']}")
                                st.write(f"**Chemin déchiffré:** {result['decrypted_path']}")
                            
                            with col2:
                                st.info("🤖 Explication IA")
                                st.write(explanation)
                            
                    except Exception as e:
                        st.error(f"❌ Erreur lors du déchiffrement: {e}")
            else:
                st.info("📭 Aucun fichier chiffré dans le vault")
        
        elif secret_input:
            st.error("❌ Phrase secrète incorrecte!")
    
    with tab3:
        st.header("📁 Fichiers dans le vault")
        
        files = st.session_state.vault_manager.list_files()
        
        if files:
            # Convertir en DataFrame pour affichage
            df = pd.DataFrame(files)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            df['file_size'] = df['file_size'].apply(lambda x: f"{x:,} bytes")
            
            st.dataframe(
                df[['filename', 'uuid', 'created_at', 'file_size']],
                use_container_width=True
            )
        else:
            st.info("📭 Aucun fichier dans le vault")

# ================================
# DÉMARRAGE
# ================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Mode test
        print("🧪 Mode test...")
        vm = VaultManager()
        print(f"✅ Vault initialisé: {vm.get_stats()}")
        
        # Créer un fichier de test
        test_file = BASE_DIR / "test_file.txt"
        with open(test_file, 'w') as f:
            f.write("Ceci est un fichier de test pour le chiffrement.")
        
        # Tester le chiffrement
        result = vm.encrypt_file(str(test_file))
        print(f"✅ Fichier chiffré: {result['uuid']}")
        
        # Tester le déchiffrement
        decrypted = vm.decrypt_file(result['uuid'])
        print(f"✅ Fichier déchiffré: {decrypted['decrypted_path']}")
        
        # Nettoyer
        os.remove(test_file)
        print("✅ Test terminé")
    else:
        # Mode Streamlit
        main()
