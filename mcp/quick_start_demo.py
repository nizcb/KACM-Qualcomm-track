#!/usr/bin/env python3
"""
Script de Démarrage Rapide - Multi-Agent System
==============================================

Script pour démarrer et tester rapidement le système multi-agents.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Vérifier les dépendances"""
    print("🔍 Vérification des dépendances...")
    
    # Vérifier Python
    try:
        import sys
        print(f"✅ Python {sys.version}")
    except:
        print("❌ Python non trouvé")
        return False
    
    # Vérifier les packages nécessaires
    required_packages = [
        'tkinter', 'requests', 'pathlib'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n📦 Packages manquants: {missing}")
        print("Installez avec: pip install -r requirements_fixed.txt")
        return False
    
    return True

def install_dependencies():
    """Installer les dépendances"""
    print("📦 Installation des dépendances...")
    
    try:
        # Utiliser WSL si on est sur Windows
        if os.name == 'nt':
            cmd = [
                "wsl", "-e", "bash", "-c",
                "cd /mnt/c/Users/chaki/Desktop/hackathon/KACM-Qualcomm-track/mcp && pip3 install -r requirements_fixed.txt"
            ]
        else:
            cmd = ["pip3", "install", "-r", "requirements_fixed.txt"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dépendances installées")
            return True
        else:
            print(f"❌ Erreur d'installation: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False

def start_api_server():
    """Démarrer le serveur API"""
    print("🚀 Démarrage du serveur API...")
    
    try:
        # Utiliser WSL si on est sur Windows
        if os.name == 'nt':
            cmd = [
                "wsl", "-e", "bash", "-c",
                "cd /mnt/c/Users/chaki/Desktop/hackathon/KACM-Qualcomm-track/mcp && python3 -c \"import sys; sys.path.insert(0, '.'); exec(open('api_server.py').read())\""
            ]
        else:
            cmd = ["python3", "api_server.py"]
        
        # Démarrer en arrière-plan
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent
        )
        
        # Attendre que l'API soit prête
        print("⏳ Attente du démarrage de l'API...")
        for i in range(10):
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print("✅ API démarrée avec succès")
                    return process
            except:
                pass
            
            time.sleep(1)
            print(f"   Tentative {i+1}/10...")
        
        print("❌ Échec du démarrage de l'API")
        return None
    
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de l'API: {e}")
        return None

def start_desktop_app():
    """Démarrer l'application desktop"""
    print("🖥️ Démarrage de l'interface desktop...")
    
    try:
        # Utiliser WSL si on est sur Windows
        if os.name == 'nt':
            cmd = [
                "wsl", "-e", "bash", "-c",
                "cd /mnt/c/Users/chaki/Desktop/hackathon/KACM-Qualcomm-track/mcp && DISPLAY=:0 python3 desktop_app_integrated.py"
            ]
        else:
            cmd = ["python3", "desktop_app_integrated.py"]
        
        subprocess.run(cmd, cwd=Path(__file__).parent)
    
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de l'interface: {e}")

def create_demo_files():
    """Créer des fichiers de démonstration"""
    print("📁 Création des fichiers de démonstration...")
    
    demo_dir = Path("demo_files")
    demo_dir.mkdir(exist_ok=True)
    
    # Fichiers de test
    test_files = {
        "document_public.txt": "Ceci est un document public sans information sensible.",
        "carte_vitale_scan.jpg": "FAKE_IMAGE_DATA_CARTE_VITALE",
        "facture_electricite.pdf": "FAKE_PDF_DATA_FACTURE",
        "photo_identite.png": "FAKE_IMAGE_DATA_PHOTO_ID",
        "cours_histoire.pdf": "FAKE_PDF_DATA_COURS_HISTOIRE",
        "document_confidentiel.txt": "CONFIDENTIEL: jean.dupont@email.com, téléphone 06 12 34 56 78, carte bancaire 1234 5678 9012 3456"
    }
    
    for filename, content in test_files.items():
        file_path = demo_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ {filename}")
    
    print(f"📁 Fichiers créés dans: {demo_dir.absolute()}")
    return demo_dir

def main():
    """Fonction principale"""
    print("="*60)
    print("🤖 MULTI-AGENT SYSTEM - DÉMARRAGE RAPIDE")
    print("   KACM Qualcomm Hackathon")
    print("="*60)
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("\n❌ Dépendances manquantes")
        
        if input("Installer les dépendances? (y/n): ").lower() == 'y':
            if not install_dependencies():
                print("❌ Échec de l'installation. Arrêt.")
                return
        else:
            print("❌ Installation annulée. Arrêt.")
            return
    
    # Créer les fichiers de démonstration
    demo_dir = create_demo_files()
    
    print("\n🎬 DÉMARRAGE DE LA DÉMONSTRATION")
    print("-" * 40)
    
    # Choix du mode de démarrage
    print("\nModes disponibles:")
    print("1. Demo complète (API + Interface Desktop)")
    print("2. API seulement")
    print("3. Interface Desktop seulement")
    print("4. Test API")
    
    choice = input("\nVotre choix (1-4): ").strip()
    
    if choice == "1":
        # Démarrage complet
        print("\n🚀 Démarrage complet du système...")
        
        # Démarrer l'API
        api_process = start_api_server()
        if not api_process:
            print("❌ Impossible de démarrer l'API")
            return
        
        # Démarrer l'interface
        try:
            start_desktop_app()
        finally:
            # Arrêter l'API
            if api_process:
                api_process.terminate()
                print("🔴 API arrêtée")
    
    elif choice == "2":
        # API seulement
        print("\n🌐 Démarrage de l'API seulement...")
        api_process = start_api_server()
        if api_process:
            print("✅ API démarrée sur http://localhost:8000")
            print("📚 Documentation: http://localhost:8000/docs")
            print("\nAppuyez sur Ctrl+C pour arrêter...")
            try:
                api_process.wait()
            except KeyboardInterrupt:
                api_process.terminate()
                print("\n🔴 API arrêtée")
    
    elif choice == "3":
        # Interface seulement
        print("\n🖥️ Démarrage de l'interface seulement...")
        print("⚠️ Note: L'API doit être démarrée séparément")
        start_desktop_app()
    
    elif choice == "4":
        # Test API
        print("\n🧪 Test de l'API...")
        
        # Démarrer l'API
        api_process = start_api_server()
        if not api_process:
            print("❌ Impossible de démarrer l'API")
            return
        
        try:
            # Tests basiques
            print("\n🔍 Tests API...")
            
            # Test health
            response = requests.get("http://localhost:8000/health")
            print(f"Health check: {response.status_code}")
            
            # Test process directory
            data = {"directory_path": str(demo_dir.absolute())}
            response = requests.post("http://localhost:8000/process/directory", json=data)
            print(f"Process directory: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Fichiers traités: {result.get('processed_files', 0)}")
                print(f"Fichiers sensibles: {result.get('files_with_warnings', 0)}")
            
            # Test search
            search_data = {"query": "carte vitale"}
            response = requests.post("http://localhost:8000/search/smart", json=search_data)
            print(f"Smart search: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Résultats trouvés: {result.get('total_results', 0)}")
            
            print("\n✅ Tests terminés")
        
        finally:
            # Arrêter l'API
            api_process.terminate()
            print("🔴 API arrêtée")
    
    else:
        print("❌ Choix invalide")
    
    print("\n🎉 Démonstration terminée!")
    print(f"📁 Fichiers de test dans: {demo_dir.absolute()}")

if __name__ == "__main__":
    main()
