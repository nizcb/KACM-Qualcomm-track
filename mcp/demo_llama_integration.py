#!/usr/bin/env python3
"""
Démonstration Complète du Système MCP avec Llama3 Local
=====================================================

Ce script simule l'intégration complète avec Llama3 pour traiter
les requêtes en langage naturel et interagir avec le système MCP.
"""

import os
import sys
import json
import time
import re
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

class LlamaIntegration:
    """Simulation de l'intégration Llama3 local"""
    
    def __init__(self):
        self.patterns = {
            "search_card": [
                r"trouve.*carte vitale",
                r"cherche.*carte vitale",
                r"carte vitale",
                r"sécurité sociale"
            ],
            "search_medical": [
                r"ordonnance",
                r"médical",
                r"prescription",
                r"docteur"
            ],
            "search_payroll": [
                r"bulletin.*paie",
                r"salaire",
                r"fiche.*paie"
            ],
            "search_course": [
                r"cours.*histoire",
                r"pdf.*cours",
                r"histoire",
                r"éducation"
            ],
            "search_recipe": [
                r"recette",
                r"cuisine",
                r"culinaire"
            ]
        }
    
    def understand_query(self, query):
        """Comprend la requête utilisateur et retourne une action"""
        query_lower = query.lower()
        
        # Analyser la requête
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return {
                        "intent": intent,
                        "query": query,
                        "search_terms": self.extract_search_terms(query_lower, intent),
                        "requires_auth": self.requires_authentication(intent)
                    }
        
        # Requête générique
        return {
            "intent": "general_search",
            "query": query,
            "search_terms": query_lower,
            "requires_auth": False
        }
    
    def extract_search_terms(self, query, intent):
        """Extrait les termes de recherche pertinents"""
        if intent == "search_card":
            return "carte vitale sécurité sociale"
        elif intent == "search_medical":
            return "ordonnance médical prescription"
        elif intent == "search_payroll":
            return "bulletin paie salaire"
        elif intent == "search_course":
            return "cours histoire éducation"
        elif intent == "search_recipe":
            return "recette cuisine"
        else:
            return query
    
    def requires_authentication(self, intent):
        """Détermine si l'intent nécessite une authentification"""
        sensitive_intents = ["search_card", "search_medical", "search_payroll"]
        return intent in sensitive_intents
    
    def generate_response(self, query, results):
        """Génère une réponse naturelle"""
        if not results:
            return f"Je n'ai pas trouvé de fichiers correspondant à votre demande: '{query}'"
        
        count = len(results)
        if count == 1:
            file_name = os.path.basename(results[0].get('file_path', ''))
            return f"J'ai trouvé un fichier qui correspond à votre recherche: {file_name}"
        else:
            return f"J'ai trouvé {count} fichiers qui correspondent à votre recherche."

class MCPDemo:
    """Démonstration complète du système MCP"""
    
    def __init__(self):
        self.llama = LlamaIntegration()
        self.mcp_system = None
        self.setup_mcp()
        
    def setup_mcp(self):
        """Initialise le système MCP"""
        try:
            from simple_mcp_system import SimpleMCPSystem
            self.mcp_system = SimpleMCPSystem()
            print("✅ Système MCP initialisé")
        except Exception as e:
            print(f"❌ Erreur MCP: {e}")
            return False
        return True
    
    def demonstrate_workflow(self):
        """Démontre le workflow complet"""
        print("\n" + "="*60)
        print("🚀 DÉMONSTRATION DU SYSTÈME MCP")
        print("="*60)
        
        # Étape 1: Analyser les fichiers de test
        print("\n📁 Étape 1: Analyse des fichiers de test")
        test_folder = BASE_DIR / "test_files"
        if test_folder.exists():
            results = self.mcp_system.analyze_directory(str(test_folder))
            print(f"   📊 {len(results)} fichiers analysés")
            
            # Afficher les résultats
            for result in results:
                file_name = os.path.basename(result.get('file_path', ''))
                status = "🔐 Sensible" if result.get('sensitive') else "📄 Normal"
                print(f"   {status} {file_name}")
        
        # Étape 2: Démonstration des requêtes
        print("\n🗣️ Étape 2: Requêtes en langage naturel")
        
        test_queries = [
            "Trouve-moi le scan de ma carte vitale",
            "Je cherche le PDF du cours d'histoire",
            "Peux-tu me donner mon bulletin de paie?",
            "Où est ma recette de tarte aux pommes?",
            "Montre-moi l'ordonnance du médecin"
        ]
        
        for query in test_queries:
            self.process_user_query(query)
            time.sleep(1)  # Pause pour la démo
        
        # Étape 3: Scénario d'authentification
        print("\n🔐 Étape 3: Scénario d'authentification")
        self.demonstrate_authentication()
        
        print("\n🎉 Démonstration terminée!")
    
    def process_user_query(self, query):
        """Traite une requête utilisateur complète"""
        print(f"\n👤 Utilisateur: {query}")
        
        # Étape 1: Comprendre la requête avec Llama
        understood = self.llama.understand_query(query)
        print(f"🧠 Compréhension: {understood['intent']}")
        
        # Étape 2: Effectuer la recherche
        search_results = self.mcp_system.search_files(understood['search_terms'])
        
        # Étape 3: Vérifier l'authentification
        if understood['requires_auth'] and search_results:
            print("🔐 Authentification requise pour les fichiers sensibles")
            # Simulation de l'authentification
            auth_success = self.simulate_authentication()
            if not auth_success:
                print("❌ Authentification échouée - Accès refusé")
                return
        
        # Étape 4: Générer la réponse
        response = self.llama.generate_response(query, search_results)
        print(f"🤖 Système: {response}")
        
        # Étape 5: Afficher les résultats
        if search_results:
            print("📋 Fichiers trouvés:")
            for result in search_results:
                file_name = os.path.basename(result.get('file_path', ''))
                score = result.get('score', 0)
                print(f"   • {file_name} (score: {score:.2f})")
    
    def simulate_authentication(self):
        """Simule le processus d'authentification"""
        print("   🔑 Demande de mot de passe...")
        print("   ✅ Authentification réussie")
        return True
    
    def demonstrate_authentication(self):
        """Démontre le système d'authentification"""
        print("Scénario: Accès à un fichier sensible")
        
        # Créer un fichier sensible fictif
        sensitive_file = "document_sensible.txt"
        password = "motdepasse123"
        
        print(f"🔐 Chiffrement du fichier: {sensitive_file}")
        
        # Simuler le chiffrement
        encrypted_content = self.mcp_system.encrypt_content(
            "Contenu sensible pour test", password
        )
        
        if encrypted_content:
            print("✅ Fichier chiffré avec succès")
            
            # Simuler le déchiffrement
            print("🔓 Tentative de déchiffrement...")
            decrypted_content = self.mcp_system.decrypt_content(
                encrypted_content, password
            )
            
            if decrypted_content:
                print("✅ Déchiffrement réussi - Accès accordé")
            else:
                print("❌ Déchiffrement échoué - Accès refusé")
        else:
            print("❌ Échec du chiffrement")
    
    def interactive_demo(self):
        """Mode interactif pour tester le système"""
        print("\n🎮 MODE INTERACTIF")
        print("Tapez vos requêtes (ou 'quit' pour quitter)")
        print("-" * 50)
        
        while True:
            try:
                query = input("\n👤 Votre requête: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Au revoir!")
                    break
                
                if not query:
                    continue
                
                self.process_user_query(query)
                
            except KeyboardInterrupt:
                print("\n👋 Démonstration interrompue")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🤖 Système Multi-Agent MCP - Démonstration")
    
    # Créer la démonstration
    demo = MCPDemo()
    
    if not demo.mcp_system:
        print("❌ Impossible d'initialiser le système MCP")
        return
    
    print("\nChoisissez le mode de démonstration:")
    print("1. Démonstration automatique")
    print("2. Mode interactif")
    print("3. Les deux")
    
    try:
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == "1":
            demo.demonstrate_workflow()
        elif choice == "2":
            demo.interactive_demo()
        elif choice == "3":
            demo.demonstrate_workflow()
            demo.interactive_demo()
        else:
            print("Choix invalide, lancement de la démonstration automatique")
            demo.demonstrate_workflow()
            
    except KeyboardInterrupt:
        print("\n👋 Démonstration interrompue")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
