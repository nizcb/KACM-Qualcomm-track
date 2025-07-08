#!/usr/bin/env python3
"""
Setup script pour Windows - Installation complète du système multi-agent
"""
import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def check_python_version():
    """Vérifier la version de Python"""
    print("🐍 Vérification de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ requis")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} détecté")
    return True

def install_requirements():
    """Installer les dépendances"""
    print("📦 Installation des dépendances...")
    try:
        # Installer pip si nécessaire
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Installer les dépendances
        req_file = Path("requirements_fixed.txt")
        if req_file.exists():
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
            print("✅ Dépendances installées")
        else:
            print("❌ Fichier requirements_fixed.txt non trouvé")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False
    return True

def check_tkinter():
    """Vérifier tkinter"""
    print("🖥️ Vérification de tkinter...")
    try:
        import tkinter as tk
        print("✅ tkinter disponible")
        return True
    except ImportError:
        print("❌ tkinter non disponible")
        print("Sur Windows, tkinter est normalement inclus avec Python")
        print("Réinstallez Python depuis python.org avec l'option 'tcl/tk and IDLE'")
        return False

def create_directories():
    """Créer les répertoires nécessaires"""
    print("📁 Création des répertoires...")
    dirs = [
        "demo_files", "encrypted", "decrypted", "vault", 
        "logs", "temp", "config", "data"
    ]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    print("✅ Répertoires créés")

def create_demo_files():
    """Créer les fichiers de démonstration"""
    print("📄 Création des fichiers de démonstration...")
    
    demo_files = {
        "demo_files/carte_vitale_scan.jpg": "Fichier image simulé - carte vitale",
        "demo_files/cours_histoire.pdf": "Contenu du cours d'histoire - Document public",
        "demo_files/document_confidentiel.txt": "CONFIDENTIEL: Données sensibles importantes",
        "demo_files/document_public.txt": "Document public accessible à tous",
        "demo_files/facture_electricite.pdf": "Facture électricité - Jean Dupont\nAdresse: 123 rue de la Paix",
        "demo_files/photo_identite.png": "Fichier image simulé - photo d'identité",
        "demo_files/data.json": json.dumps({
            "nom": "Dupont", 
            "prenom": "Jean",
            "email": "jean.dupont@email.com",
            "telephone": "0123456789"
        }, indent=2),
        "demo_files/data_clients.json": json.dumps([
            {"nom": "Martin", "email": "martin@test.com", "carte_bancaire": "4111111111111111"},
            {"nom": "Bernard", "email": "bernard@test.com", "carte_bancaire": "5555555555554444"}
        ], indent=2),
        "demo_files/readme.md": "# Documentation du projet\n\nCeci est un fichier public",
        "demo_files/passeport_scan.pdf": "Passeport français - Numéro: 12AB34567",
        "demo_files/test_chiffrement.txt": "Fichier test pour le chiffrement"
    }
    
    for file_path, content in demo_files.items():
        Path(file_path).parent.mkdir(exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Fichiers de démonstration créés")

def create_config():
    """Créer la configuration"""
    print("⚙️ Création de la configuration...")
    
    config = {
        "api": {
            "host": "127.0.0.1",
            "port": 8000,
            "debug": True
        },
        "agents": {
            "orchestrator": {"port": 8001},
            "nlp": {"port": 8002},
            "vision": {"port": 8003},
            "audio": {"port": 8004},
            "file_manager": {"port": 8005},
            "security": {"port": 8006}
        },
        "security": {
            "vault_password": "mon_secret_ultra_securise_2024",
            "encryption_key": "ma_cle_de_chiffrement_ultra_securisee_2024"
        },
        "paths": {
            "demo_files": "demo_files",
            "encrypted": "encrypted",
            "decrypted": "decrypted",
            "vault": "vault",
            "logs": "logs",
            "temp": "temp"
        }
    }
    
    with open("config/config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration créée")

def test_system():
    """Tester le système"""
    print("🧪 Test du système...")
    
    try:
        # Test du système MCP
        print("Test du système MCP...")
        result = subprocess.run([sys.executable, "simple_mcp_system.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Système MCP fonctionnel")
        else:
            print("❌ Problème avec le système MCP")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ Système MCP démarré (timeout normal)")
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🚀 SETUP SYSTÈME MULTI-AGENT - WINDOWS")
    print("=" * 60)
    
    # Vérifications préliminaires
    if not check_python_version():
        return False
    
    # Installation
    if not install_requirements():
        return False
    
    if not check_tkinter():
        print("⚠️ tkinter non disponible - interface desktop désactivée")
        print("Le système fonctionnera en mode API/Console uniquement")
    
    # Préparation de l'environnement
    create_directories()
    create_demo_files()
    create_config()
    
    # Test final
    if test_system():
        print("\n" + "=" * 60)
        print("✅ INSTALLATION RÉUSSIE!")
        print("=" * 60)
        print("🚀 Pour démarrer la démonstration:")
        print("   python launch_demo_windows.py")
        print("\n📖 Commandes disponibles:")
        print("   python simple_mcp_system.py     # Système MCP seul")
        print("   python demo_console.py          # Démonstration console")
        print("   python test_system.py           # Tests complets")
        print("\n🔑 Mot de passe du vault: mon_secret_ultra_securise_2024")
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ PROBLÈME LORS DE L'INSTALLATION")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
