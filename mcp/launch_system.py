#!/usr/bin/env python3
"""
Lanceur Principal - Système Multi-Agent
=====================================

Script principal pour lancer le système multi-agents complet.
"""

import os
import sys
import subprocess
import time
import requests
import threading
from pathlib import Path
import argparse

def print_banner():
    """Afficher la bannière du système"""
    print("="*70)
    print("🤖 SYSTÈME MULTI-AGENT - KACM QUALCOMM HACKATHON")
    print("   Intelligence Artificielle Agentique")
    print("   Version 1.0.0 - Décembre 2024")
    print("="*70)
    print()

def check_python_version():
    """Vérifier la version de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_dependencies():
    """Installer les dépendances"""
    print("📦 Vérification des dépendances...")
    
    required_packages = [
        "tkinter",
        "requests", 
        "pathlib",
        "sqlite3",
        "threading",
        "asyncio"
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == "tkinter":
                import tkinter
            elif package == "sqlite3":
                import sqlite3
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n📦 Installation des packages manquants...")
        try:
            # Essayer d'installer les packages manquants
            for package in missing:
                if package == "tkinter":
                    print("⚠️ tkinter doit être installé via le gestionnaire de paquets du système")
                elif package not in ["pathlib", "sqlite3", "threading", "asyncio"]:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except Exception as e:
            print(f"❌ Erreur lors de l'installation: {e}")
            return False
    
    return True

def create_demo_environment():
    """Créer l'environnement de démonstration"""
    print("🏗️ Création de l'environnement de démonstration...")
    
    # Créer les dossiers nécessaires
    folders = [
        "demo_files", "logs", "temp", "encrypted", 
        "decrypted", "vault", "temp_decrypted"
    ]
    
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
    
    # Créer des fichiers de démonstration réalistes
    demo_files = {
        "demo_files/document_public.txt": """
# Rapport Public - Projet Innovation
Date: 15 Décembre 2024

## Résumé Exécutif
Ce document présente les résultats du projet d'innovation technologique.
Aucune information confidentielle n'est présente dans ce rapport.

## Objectifs
- Développer une solution IA
- Améliorer l'efficacité
- Réduire les coûts

## Conclusion
Le projet a atteint ses objectifs principaux.
        """,
        
        "demo_files/document_confidentiel.txt": """
DOCUMENT CONFIDENTIEL - ACCÈS RESTREINT

Informations personnelles:
- Nom: Jean Dupont
- Email: jean.dupont@entreprise.com
- Téléphone: 06 12 34 56 78
- Numéro de sécurité sociale: 1 23 45 67 890 123 45
- IBAN: FR14 2004 1010 0505 0001 3M02 606

Ces informations sont strictement confidentielles.
        """,
        
        "demo_files/carte_vitale_scan.jpg": "FAKE_IMAGE_DATA_CARTE_VITALE_SENSIBLE",
        "demo_files/photo_identite.png": "FAKE_IMAGE_DATA_PHOTO_IDENTITE_SENSIBLE",
        "demo_files/passeport_scan.pdf": "FAKE_PDF_DATA_PASSEPORT_SENSIBLE",
        "demo_files/facture_electricite.pdf": "FAKE_PDF_DATA_FACTURE_NORMALE",
        "demo_files/cours_histoire.pdf": "FAKE_PDF_DATA_COURS_HISTOIRE_NORMALE",
        "demo_files/musique_test.mp3": "FAKE_AUDIO_DATA_NORMALE",
        "demo_files/enregistrement_vocal.wav": "FAKE_AUDIO_DATA_NORMALE",
        
        "demo_files/data_clients.json": """{
    "clients": [
        {
            "nom": "Jean Dupont",
            "email": "jean.dupont@email.com",
            "telephone": "06 12 34 56 78"
        },
        {
            "nom": "Marie Martin", 
            "email": "marie.martin@email.com",
            "telephone": "06 98 76 54 32"
        }
    ]
}""",
        
        "demo_files/readme.md": """# Documentation du Projet

## Description
Ceci est un fichier de documentation normal sans informations sensibles.

## Installation
1. Télécharger le projet
2. Installer les dépendances
3. Lancer l'application

## Usage
L'application permet de traiter différents types de fichiers.
        """,
        
        "demo_files/script_exemple.py": """#!/usr/bin/env python3
# Script d'exemple normal

def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
        """
    }
    
    for file_path, content in demo_files.items():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
    
    print("✅ Environnement de démonstration créé")
    print(f"📁 Fichiers créés dans: {Path('demo_files').absolute()}")
    
    return Path("demo_files")

def start_api_server():
    """Démarrer le serveur API"""
    print("🚀 Démarrage du serveur API...")
    
    try:
        # Démarrer le serveur API
        api_process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent
        )
        
        # Attendre que l'API soit prête
        print("⏳ Attente du démarrage de l'API...")
        for i in range(20):
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print("✅ API démarrée avec succès")
                    print("📡 URL: http://localhost:8000")
                    print("📚 Documentation: http://localhost:8000/docs")
                    return api_process
            except:
                pass
            
            time.sleep(0.5)
            if i % 4 == 0:
                print(f"   Tentative {i//4 + 1}/5...")
        
        print("❌ Échec du démarrage de l'API")
        api_process.terminate()
        return None
    
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de l'API: {e}")
        return None

def start_desktop_app():
    """Démarrer l'application desktop"""
    print("🖥️ Démarrage de l'interface desktop...")
    
    try:
        # Démarrer l'application desktop
        subprocess.run([sys.executable, "desktop_app_integrated.py"])
    
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de l'interface: {e}")

def run_tests():
    """Exécuter les tests du système"""
    print("🧪 Exécution des tests...")
    
    try:
        result = subprocess.run(
            [sys.executable, "test_system.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        print(result.stdout)
        if result.stderr:
            print("Erreurs:")
            print(result.stderr)
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

def demo_mode():
    """Mode démonstration complète"""
    print("🎬 LANCEMENT DE LA DÉMONSTRATION COMPLÈTE")
    print("-" * 50)
    
    # Créer l'environnement
    demo_dir = create_demo_environment()
    
    # Démarrer l'API
    api_process = start_api_server()
    if not api_process:
        print("❌ Impossible de démarrer l'API")
        return False
    
    try:
        # Lancer l'interface desktop
        print("\n🖥️ Lancement de l'interface desktop...")
        print("📋 Instructions pour la démonstration:")
        print("   1. Sélectionnez le dossier 'demo_files' dans l'interface")
        print("   2. Cliquez sur 'Analyser le Dossier'")
        print("   3. Testez la recherche avec: 'trouve moi le scan de ma carte vitale'")
        print("   4. Utilisez le mot de passe: 'mon_secret_ultra_securise_2024'")
        print()
        
        start_desktop_app()
        
    finally:
        # Arrêter l'API
        if api_process:
            api_process.terminate()
            print("🔴 API arrêtée")
    
    return True

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Système Multi-Agent KACM Qualcomm")
    parser.add_argument("--mode", choices=["demo", "api", "desktop", "test"], 
                       default="demo", help="Mode de fonctionnement")
    parser.add_argument("--skip-deps", action="store_true", 
                       help="Ignorer la vérification des dépendances")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Vérifications préliminaires
    if not check_python_version():
        return 1
    
    if not args.skip_deps:
        if not install_dependencies():
            print("❌ Échec de l'installation des dépendances")
            return 1
    
    # Exécution selon le mode
    if args.mode == "demo":
        success = demo_mode()
        if success:
            print("🎉 Démonstration terminée avec succès!")
            return 0
        else:
            print("❌ Erreur lors de la démonstration")
            return 1
    
    elif args.mode == "api":
        # Mode API seulement
        create_demo_environment()
        api_process = start_api_server()
        if api_process:
            print("\n📡 Serveur API en cours d'exécution...")
            print("   Appuyez sur Ctrl+C pour arrêter")
            try:
                api_process.wait()
            except KeyboardInterrupt:
                api_process.terminate()
                print("\n🔴 API arrêtée")
        return 0
    
    elif args.mode == "desktop":
        # Mode desktop seulement
        print("⚠️ Note: Assurez-vous que l'API est démarrée séparément")
        create_demo_environment()
        start_desktop_app()
        return 0
    
    elif args.mode == "test":
        # Mode test seulement
        create_demo_environment()
        success = run_tests()
        return 0 if success else 1
    
    else:
        print("❌ Mode non reconnu")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🔴 Arrêt demandé par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
