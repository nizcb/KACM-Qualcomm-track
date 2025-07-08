#!/usr/bin/env python3
"""
Test Complet du Système Multi-Agent MCP
=======================================

Ce script teste tous les composants du système :
1. Interface Desktop (tkinter simple)
2. Backend MCP avec orchestrateur
3. Agents (NLP, Vision, Audio, Security)
4. API FastAPI
5. Vault sécurisé avec chiffrement
6. Recherche intelligente

Usage:
    python test_complete_system.py
"""

import os
import sys
import time
import json
import threading
import subprocess
from pathlib import Path

# Configuration des chemins
BASE_DIR = Path(__file__).parent
TEST_FILES_DIR = BASE_DIR / "test_files"
VAULT_DIR = BASE_DIR / "vault"
LOGS_DIR = BASE_DIR / "logs"

# Créer les répertoires nécessaires
for dir_path in [TEST_FILES_DIR, VAULT_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

class SystemTester:
    def __init__(self):
        self.test_results = []
        self.api_server_process = None
        
    def log_test(self, test_name, success, message=""):
        """Enregistre le résultat d'un test"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
    
    def test_dependencies(self):
        """Test 1: Vérifier les dépendances Python"""
        print("\n🔍 Test 1: Vérification des dépendances")
        
        required_modules = [
            "tkinter", "json", "sqlite3", "pathlib", "threading",
            "cryptography", "requests", "logging"
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
                print(f"  ✓ {module}")
            except ImportError:
                missing_modules.append(module)
                print(f"  ✗ {module} - MANQUANT")
        
        if missing_modules:
            self.log_test("Dependencies", False, f"Modules manquants: {missing_modules}")
        else:
            self.log_test("Dependencies", True, "Tous les modules requis sont disponibles")
    
    def test_mcp_system(self):
        """Test 2: Système MCP simple"""
        print("\n🤖 Test 2: Système MCP")
        
        try:
            # Import du système MCP
            sys.path.append(str(BASE_DIR))
            from simple_mcp_system import SimpleMCPSystem
            
            # Initialisation
            mcp = SimpleMCPSystem()
            
            # Test d'analyse d'un fichier
            test_file = TEST_FILES_DIR / "cours_histoire.txt"
            if test_file.exists():
                result = mcp.analyze_file(str(test_file))
                
                if result and result.get("success"):
                    self.log_test("MCP System", True, "Analyse de fichier réussie")
                else:
                    self.log_test("MCP System", False, "Échec de l'analyse")
            else:
                self.log_test("MCP System", False, "Fichier de test non trouvé")
                
        except Exception as e:
            self.log_test("MCP System", False, f"Erreur: {str(e)}")
    
    def test_security_vault(self):
        """Test 3: Système de sécurité et vault"""
        print("\n🔐 Test 3: Système de sécurité")
        
        try:
            sys.path.append(str(BASE_DIR))
            from simple_mcp_system import SimpleMCPSystem
            
            mcp = SimpleMCPSystem()
            
            # Test de chiffrement
            test_content = "Contenu secret pour test"
            password = "motdepasse123"
            
            encrypted = mcp.encrypt_content(test_content, password)
            if encrypted:
                decrypted = mcp.decrypt_content(encrypted, password)
                
                if decrypted == test_content:
                    self.log_test("Security Vault", True, "Chiffrement/déchiffrement réussi")
                else:
                    self.log_test("Security Vault", False, "Échec du déchiffrement")
            else:
                self.log_test("Security Vault", False, "Échec du chiffrement")
                
        except Exception as e:
            self.log_test("Security Vault", False, f"Erreur: {str(e)}")
    
    def test_intelligent_search(self):
        """Test 4: Recherche intelligente"""
        print("\n🔍 Test 4: Recherche intelligente")
        
        try:
            sys.path.append(str(BASE_DIR))
            from simple_mcp_system import SimpleMCPSystem
            
            mcp = SimpleMCPSystem()
            
            # Analyser tous les fichiers de test
            for file_path in TEST_FILES_DIR.glob("*.txt"):
                mcp.analyze_file(str(file_path))
            
            # Test de recherche
            search_results = mcp.search_files("carte vitale")
            
            if search_results:
                self.log_test("Intelligent Search", True, f"Trouvé {len(search_results)} résultats")
            else:
                self.log_test("Intelligent Search", False, "Aucun résultat trouvé")
                
        except Exception as e:
            self.log_test("Intelligent Search", False, f"Erreur: {str(e)}")
    
    def test_desktop_interface(self):
        """Test 5: Interface Desktop"""
        print("\n🖥️ Test 5: Interface Desktop")
        
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # Test de création d'interface simple
            root = tk.Tk()
            root.title("Test Interface")
            root.geometry("300x200")
            
            # Créer quelques widgets de test
            label = tk.Label(root, text="Test réussi!")
            label.pack(pady=20)
            
            button = tk.Button(root, text="OK", command=root.destroy)
            button.pack(pady=10)
            
            # Fermer automatiquement après 1 seconde
            root.after(1000, root.destroy)
            root.mainloop()
            
            self.log_test("Desktop Interface", True, "Interface tkinter fonctionnelle")
            
        except Exception as e:
            self.log_test("Desktop Interface", False, f"Erreur tkinter: {str(e)}")
    
    def test_api_server(self):
        """Test 6: API FastAPI"""
        print("\n🌐 Test 6: API Server")
        
        try:
            import requests
            
            # Tenter de démarrer l'API en arrière-plan
            try:
                import uvicorn
                import fastapi
                
                # Démarrer le serveur API dans un thread séparé
                def start_api():
                    try:
                        sys.path.append(str(BASE_DIR))
                        from api_server import app
                        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
                    except Exception as e:
                        print(f"Erreur API: {e}")
                
                api_thread = threading.Thread(target=start_api, daemon=True)
                api_thread.start()
                
                # Attendre que l'API démarre
                time.sleep(3)
                
                # Tester l'API
                response = requests.get("http://127.0.0.1:8000/health", timeout=5)
                
                if response.status_code == 200:
                    self.log_test("API Server", True, "API FastAPI fonctionnelle")
                else:
                    self.log_test("API Server", False, f"Code de statut: {response.status_code}")
                    
            except ImportError:
                self.log_test("API Server", False, "FastAPI ou uvicorn non installé")
                
        except Exception as e:
            self.log_test("API Server", False, f"Erreur: {str(e)}")
    
    def test_complete_workflow(self):
        """Test 7: Workflow complet"""
        print("\n🔄 Test 7: Workflow complet")
        
        try:
            sys.path.append(str(BASE_DIR))
            from simple_mcp_system import SimpleMCPSystem
            
            mcp = SimpleMCPSystem()
            
            # Scénario complet
            print("  📁 Analyse du dossier de test...")
            results = mcp.analyze_directory(str(TEST_FILES_DIR))
            
            if results:
                sensitive_files = [f for f in results if f.get("sensitive")]
                normal_files = [f for f in results if not f.get("sensitive")]
                
                print(f"  📊 Fichiers analysés: {len(results)}")
                print(f"  🔐 Fichiers sensibles: {len(sensitive_files)}")
                print(f"  📄 Fichiers normaux: {len(normal_files)}")
                
                # Test de recherche
                search_query = "cours histoire"
                search_results = mcp.search_files(search_query)
                print(f"  🔍 Recherche '{search_query}': {len(search_results)} résultats")
                
                self.log_test("Complete Workflow", True, 
                            f"Workflow complet: {len(results)} fichiers analysés")
            else:
                self.log_test("Complete Workflow", False, "Aucun résultat d'analyse")
                
        except Exception as e:
            self.log_test("Complete Workflow", False, f"Erreur: {str(e)}")
    
    def generate_report(self):
        """Génère un rapport final"""
        print("\n" + "="*60)
        print("📊 RAPPORT DE TEST FINAL")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total des tests: {total_tests}")
        print(f"Tests réussis: {passed_tests} ✅")
        print(f"Tests échoués: {failed_tests} ❌")
        print(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔴 TESTS ÉCHOUÉS:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  - {test['test']}: {test['message']}")
        
        print("\n📋 RÉSUMÉ DES COMPOSANTS:")
        components = {
            "Dependencies": "Dépendances Python",
            "MCP System": "Système multi-agents",
            "Security Vault": "Coffre-fort sécurisé",
            "Intelligent Search": "Recherche intelligente",
            "Desktop Interface": "Interface graphique",
            "API Server": "Serveur API",
            "Complete Workflow": "Workflow complet"
        }
        
        for test in self.test_results:
            status = "✅" if test["success"] else "❌"
            component_name = components.get(test["test"], test["test"])
            print(f"  {status} {component_name}")
        
        # Sauvegarder le rapport
        report_file = LOGS_DIR / f"test_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport détaillé sauvegardé: {report_file}")
        
        return passed_tests, failed_tests
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🚀 DÉMARRAGE DES TESTS DU SYSTÈME MCP")
        print("="*60)
        
        # Exécuter tous les tests
        self.test_dependencies()
        self.test_mcp_system()
        self.test_security_vault()
        self.test_intelligent_search()
        self.test_desktop_interface()
        self.test_api_server()
        self.test_complete_workflow()
        
        # Générer le rapport final
        passed, failed = self.generate_report()
        
        return failed == 0

def main():
    """Fonction principale"""
    print("🎯 Test Complet du Système Multi-Agent MCP")
    print("==========================================")
    
    tester = SystemTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
            print("Le système est prêt pour la démonstration.")
        else:
            print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
            print("Vérifiez les erreurs ci-dessus avant la démonstration.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")

if __name__ == "__main__":
    main()
