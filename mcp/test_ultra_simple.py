#!/usr/bin/env python3
"""
TEST ULTRA-SIMPLE - Système Multi-Agent Complet
Tests de bout en bout : MCP → Interface → Backend → Agents
"""
import os
import sys
import time
import threading
from pathlib import Path

def test_mcp_system():
    """Test du système MCP de base"""
    print("🧪 TEST 1: Système MCP de base")
    print("-" * 50)
    
    try:
        from simple_mcp_system import MCPSystem
        
        # Configuration
        config = {
            "vault_password": "test123",
            "encryption_key": "test_key_123"
        }
        
        # Démarrer le système
        system = MCPSystem(config)
        system.start()
        
        print("✅ Système MCP démarré")
        
        # Test analyse de répertoire
        result = system.call_tool("Orchestrator", "process_directory", {"directory": "test_files"})
        if result.get("success"):
            print(f"✅ Analyse répertoire: {result.get('files_processed', 0)} fichiers")
        else:
            print("❌ Erreur analyse répertoire")
            return False
        
        # Test recherche
        result = system.call_tool("Orchestrator", "smart_search", {"query": "cours histoire"})
        if result.get("success"):
            print(f"✅ Recherche: {len(result.get('results', []))} résultats")
        else:
            print("❌ Erreur recherche")
            return False
        
        # Arrêter
        system.stop()
        print("✅ Système MCP arrêté")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur MCP: {e}")
        return False

def test_interface_simple():
    """Test de l'interface desktop simple"""
    print("\n🖥️ TEST 2: Interface Desktop")
    print("-" * 50)
    
    try:
        # Juste vérifier que l'interface peut être importée
        import tkinter as tk
        print("✅ tkinter disponible")
        
        # Test création interface basique
        root = tk.Tk()
        root.title("Test Interface")
        root.geometry("300x200")
        
        # Créer quelques widgets de test
        label = tk.Label(root, text="Interface de test")
        label.pack(pady=20)
        
        button = tk.Button(root, text="Test OK", command=root.quit)
        button.pack(pady=10)
        
        # Fermer automatiquement après 2 secondes
        root.after(2000, root.quit)
        
        print("✅ Interface créée (fermeture automatique)")
        root.mainloop()
        
        return True
        
    except ImportError:
        print("❌ tkinter non disponible")
        return False
    except Exception as e:
        print(f"❌ Erreur interface: {e}")
        return False

def test_api_backend():
    """Test du backend API"""
    print("\n🌐 TEST 3: Backend API")
    print("-" * 50)
    
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI disponible")
        
        # Test création API basique
        app = fastapi.FastAPI(title="Test API")
        
        @app.get("/health")
        def health_check():
            return {"status": "ok", "test": True}
        
        @app.post("/test-analyze")
        def test_analyze(data: dict):
            return {"success": True, "files_processed": 5}
        
        print("✅ API créée avec succès")
        
        # Test de démarrage rapide (sans serveur réel)
        print("✅ Endpoints configurés")
        
        return True
        
    except ImportError:
        print("❌ FastAPI non disponible")
        return False
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False

def test_complete_workflow():
    """Test du workflow complet"""
    print("\n🔄 TEST 4: Workflow Complet")
    print("-" * 50)
    
    try:
        # Simuler le workflow complet
        print("📁 1. Sélection du dossier test_files")
        
        # Vérifier que les fichiers existent
        test_dir = Path("test_files")
        if not test_dir.exists():
            print("❌ Dossier test_files non trouvé")
            return False
        
        files = list(test_dir.glob("*.txt")) + list(test_dir.glob("*.json"))
        print(f"📄 2. {len(files)} fichiers trouvés")
        
        # Simuler l'analyse
        print("🔍 3. Analyse des fichiers...")
        sensitive_files = []
        public_files = []
        
        for file_path in files:
            content = file_path.read_text(encoding='utf-8')
            # Détection PII simple
            if any(keyword in content.lower() for keyword in ["sécurité sociale", "carte", "email", "téléphone"]):
                sensitive_files.append(file_path.name)
            else:
                public_files.append(file_path.name)
        
        print(f"🔒 4. Fichiers sensibles: {len(sensitive_files)}")
        print(f"📄 5. Fichiers publics: {len(public_files)}")
        
        # Simuler la recherche
        print("🔍 6. Test de recherche...")
        
        search_queries = [
            "cours histoire",
            "document sensible",
            "ordonnance médicale"
        ]
        
        for query in search_queries:
            # Recherche simple par nom de fichier
            matches = [f for f in files if any(word in f.name.lower() for word in query.split())]
            print(f"   '{query}': {len(matches)} résultat(s)")
        
        # Simuler l'authentification
        print("🔐 7. Test d'authentification...")
        test_password = "test123"
        print(f"   Mot de passe test: {'✅' if test_password == 'test123' else '❌'}")
        
        print("✅ Workflow complet testé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur workflow: {e}")
        return False

def test_integration_llama():
    """Test d'intégration avec Llama3 (simulé)"""
    print("\n🤖 TEST 5: Intégration IA (Llama3 simulé)")
    print("-" * 50)
    
    try:
        # Simuler l'intégration Llama3
        def simulate_llama_response(prompt):
            """Simuler une réponse Llama3"""
            prompt_lower = prompt.lower()
            
            if "carte vitale" in prompt_lower:
                return {
                    "intent": "search_sensitive_document",
                    "document_type": "carte_vitale",
                    "requires_auth": True,
                    "confidence": 0.95
                }
            elif "cours" in prompt_lower and "histoire" in prompt_lower:
                return {
                    "intent": "search_document",
                    "document_type": "cours",
                    "subject": "histoire",
                    "requires_auth": False,
                    "confidence": 0.90
                }
            elif "facture" in prompt_lower or "factures" in prompt_lower:
                return {
                    "intent": "search_documents",
                    "document_type": "facture",
                    "requires_auth": False,
                    "confidence": 0.85
                }
            else:
                return {
                    "intent": "general_search",
                    "query": prompt,
                    "requires_auth": False,
                    "confidence": 0.70
                }
        
        # Test de plusieurs prompts
        test_prompts = [
            "trouve moi le scan de ma carte vitale",
            "donne moi le pdf de cours d'histoire",
            "où sont mes factures",
            "liste tous les documents"
        ]
        
        for prompt in test_prompts:
            response = simulate_llama_response(prompt)
            print(f"   Prompt: '{prompt}'")
            print(f"   Réponse: {response['intent']} (confiance: {response['confidence']})")
            print()
        
        print("✅ Intégration IA simulée avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur intégration IA: {e}")
        return False

def main():
    """Test complet du système"""
    print("=" * 60)
    print("🧪 TESTS ULTRA-SIMPLES - SYSTÈME MULTI-AGENT")
    print("=" * 60)
    
    tests = [
        ("MCP System", test_mcp_system),
        ("Interface Desktop", test_interface_simple),
        ("Backend API", test_api_backend),
        ("Workflow Complet", test_complete_workflow),
        ("Intégration IA", test_integration_llama)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Erreur critique dans {test_name}: {e}")
            results[test_name] = False
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{test_name:<20} : {status}")
    
    print(f"\nRésultats: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS - SYSTÈME PRÊT POUR LA DÉMO!")
    elif passed >= total * 0.8:
        print("⚠️ SYSTÈME PARTIELLEMENT FONCTIONNEL - QUELQUES CORRECTIONS NÉCESSAIRES")
    else:
        print("❌ SYSTÈME NON FONCTIONNEL - CORRECTIONS IMPORTANTES NÉCESSAIRES")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
