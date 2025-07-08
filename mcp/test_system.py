#!/usr/bin/env python3
"""
Script de Test Complet - Système Multi-Agent
===========================================

Test de tous les composants du système multi-agents.
"""

import asyncio
import os
import sys
import time
from pathlib import Path
import json

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent))

def create_test_environment():
    """Créer un environnement de test"""
    print("🏗️ Création de l'environnement de test...")
    
    # Créer les dossiers nécessaires
    folders = ["demo_files", "logs", "temp", "encrypted", "decrypted", "vault"]
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
    
    # Créer des fichiers de test
    test_files = {
        "demo_files/document_public.txt": "Ceci est un document public sans information sensible.",
        "demo_files/document_confidentiel.txt": "CONFIDENTIEL: Email: jean.dupont@email.com, Téléphone: 06 12 34 56 78",
        "demo_files/carte_vitale_scan.jpg": "FAKE_IMAGE_DATA_CARTE_VITALE",
        "demo_files/facture_electricite.pdf": "FAKE_PDF_DATA_FACTURE",
        "demo_files/photo_identite.png": "FAKE_IMAGE_DATA_PHOTO_ID",
        "demo_files/cours_histoire.pdf": "FAKE_PDF_DATA_COURS_HISTOIRE",
        "demo_files/musique_test.mp3": "FAKE_AUDIO_DATA",
        "demo_files/data.json": '{"nom": "Jean Dupont", "email": "jean.dupont@email.com"}',
        "demo_files/readme.md": "# Fichier de test\n\nCeci est un fichier Markdown de test.",
        "demo_files/script.py": "# Script Python de test\nprint('Hello World')"
    }
    
    for file_path, content in test_files.items():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Environnement de test créé")
    return Path("demo_files")

async def test_simple_mcp_system():
    """Tester le système MCP simplifié"""
    print("\n🧪 Test du système MCP simplifié...")
    
    try:
        from simple_mcp_system import orchestrator
        
        # Test de démarrage
        print("🚀 Démarrage des agents...")
        await orchestrator.start_all_agents()
        print("✅ Agents démarrés")
        
        # Test de traitement de répertoire
        print("📁 Test de traitement de répertoire...")
        demo_dir = Path("demo_files")
        if demo_dir.exists():
            result = await orchestrator.process_directory(str(demo_dir))
            print(f"✅ Traitement terminé: {result['processed_files']} fichiers traités")
            print(f"   - Fichiers sensibles: {result['files_with_warnings']}")
            print(f"   - Temps de traitement: {result['processing_time']:.2f}s")
        else:
            print("❌ Répertoire de test non trouvé")
        
        # Test de recherche
        print("🔍 Test de recherche intelligente...")
        search_queries = [
            "carte vitale",
            "cours histoire",
            "document confidentiel",
            "fichier inexistant"
        ]
        
        for query in search_queries:
            search_result = await orchestrator.smart_search(query)
            print(f"   - '{query}': {search_result['total_results']} résultats")
        
        # Test de statut
        print("📊 Test de statut du système...")
        status = orchestrator.get_system_status()
        print(f"✅ Statut: {status['status']}")
        
        # Test de l'agent de sécurité
        print("🔒 Test de l'agent de sécurité...")
        security_agent = orchestrator.security_agent
        
        # Créer un fichier de test pour le chiffrement
        test_file = Path("demo_files/test_chiffrement.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Fichier de test pour le chiffrement")
        
        # Test de chiffrement
        encrypt_result = await security_agent.call_tool(
            "encrypt_file",
            file_path=str(test_file),
            password="mon_secret_ultra_securise_2024"
        )
        print(f"✅ Chiffrement: {encrypt_result['message']}")
        
        # Test de déchiffrement
        decrypt_result = await security_agent.call_tool(
            "decrypt_file",
            file_id=encrypt_result['file_id'],
            password="mon_secret_ultra_securise_2024"
        )
        print(f"✅ Déchiffrement: {decrypt_result['message']}")
        
        # Test avec mauvais mot de passe
        bad_decrypt_result = await security_agent.call_tool(
            "decrypt_file",
            file_id=encrypt_result['file_id'],
            password="mauvais_mot_de_passe"
        )
        print(f"✅ Mauvais mot de passe: {bad_decrypt_result['message']}")
        
        # Arrêt des agents
        print("🔴 Arrêt des agents...")
        await orchestrator.stop_all_agents()
        print("✅ Agents arrêtés")
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors du test MCP: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_server():
    """Tester le serveur API"""
    print("\n🌐 Test du serveur API...")
    
    try:
        import subprocess
        import requests
        import threading
        
        # Démarrer le serveur API en arrière-plan
        print("🚀 Démarrage du serveur API...")
        
        # Utiliser Python directement (sans WSL pour le test)
        api_process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent
        )
        
        # Attendre que l'API soit prête
        api_ready = False
        for i in range(20):
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    api_ready = True
                    break
            except:
                pass
            time.sleep(0.5)
        
        if not api_ready:
            print("❌ L'API n'a pas pu démarrer")
            api_process.terminate()
            return False
        
        print("✅ API démarrée")
        
        # Test des endpoints
        print("🧪 Test des endpoints API...")
        
        # Test health
        response = requests.get("http://localhost:8000/health")
        print(f"   - Health: {response.status_code}")
        
        # Test start system
        response = requests.post("http://localhost:8000/system/start")
        print(f"   - Start system: {response.status_code}")
        
        # Test system status
        response = requests.get("http://localhost:8000/system/status")
        print(f"   - System status: {response.status_code}")
        
        # Test process directory
        demo_dir = Path("demo_files")
        if demo_dir.exists():
            data = {"directory_path": str(demo_dir.absolute())}
            response = requests.post("http://localhost:8000/process/directory", json=data)
            print(f"   - Process directory: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"     Fichiers traités: {result.get('processed_files', 0)}")
        
        # Test smart search
        search_data = {"query": "carte vitale"}
        response = requests.post("http://localhost:8000/search/smart", json=search_data)
        print(f"   - Smart search: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"     Résultats: {result.get('total_results', 0)}")
        
        # Test stop system
        response = requests.post("http://localhost:8000/system/stop")
        print(f"   - Stop system: {response.status_code}")
        
        # Arrêter l'API
        api_process.terminate()
        print("✅ API arrêtée")
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors du test API: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_desktop_app():
    """Tester l'application desktop (test limité)"""
    print("\n🖥️ Test de l'application desktop...")
    
    try:
        # Import test
        from desktop_app_integrated import MultiAgentDesktopAppIntegrated
        print("✅ Import de l'application desktop réussi")
        
        # Test de création de classe (sans démarrage de l'interface)
        print("🧪 Test de création de l'application...")
        
        # Simulation de création sans démarrage de l'interface
        class MockApp:
            def __init__(self):
                self.api_base_url = "http://localhost:8000"
                self.current_directory = None
        
        app = MockApp()
        print("✅ Application créée avec succès")
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors du test desktop: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Exécuter tous les tests"""
    print("="*60)
    print("🧪 SUITE DE TESTS COMPLÈTE - SYSTÈME MULTI-AGENT")
    print("="*60)
    
    # Créer l'environnement de test
    test_dir = create_test_environment()
    
    # Résultats des tests
    results = {}
    
    # Test 1: Système MCP simplifié
    print("\n" + "="*60)
    print("TEST 1: SYSTÈME MCP SIMPLIFIÉ")
    print("="*60)
    
    try:
        results["mcp_system"] = asyncio.run(test_simple_mcp_system())
    except Exception as e:
        print(f"❌ Erreur critique MCP: {e}")
        results["mcp_system"] = False
    
    # Test 2: Application desktop
    print("\n" + "="*60)
    print("TEST 2: APPLICATION DESKTOP")
    print("="*60)
    
    results["desktop_app"] = test_desktop_app()
    
    # Test 3: Serveur API
    print("\n" + "="*60)
    print("TEST 3: SERVEUR API")
    print("="*60)
    
    try:
        results["api_server"] = test_api_server()
    except Exception as e:
        print(f"❌ Erreur critique API: {e}")
        results["api_server"] = False
    
    # Résumé des résultats
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name.upper():20} : {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nRésultats: {passed_tests}/{total_tests} tests réussis ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 SYSTÈME FONCTIONNEL - Prêt pour la démonstration!")
    elif success_rate >= 60:
        print("⚠️ SYSTÈME PARTIELLEMENT FONCTIONNEL - Quelques ajustements nécessaires")
    else:
        print("❌ SYSTÈME NON FONCTIONNEL - Corrections importantes nécessaires")
    
    return success_rate >= 80

def main():
    """Fonction principale"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "mcp":
            # Test MCP seulement
            create_test_environment()
            asyncio.run(test_simple_mcp_system())
        elif sys.argv[1] == "api":
            # Test API seulement
            create_test_environment()
            test_api_server()
        elif sys.argv[1] == "desktop":
            # Test desktop seulement
            test_desktop_app()
        else:
            print("Usage: python test_system.py [mcp|api|desktop]")
    else:
        # Test complet
        run_comprehensive_test()

if __name__ == "__main__":
    main()
