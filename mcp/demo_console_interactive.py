#!/usr/bin/env python3
"""
DÉMONSTRATION CONSOLE INTERACTIVE COMPLÈTE
Système Multi-Agent avec interface console riche
"""
import os
import sys
import time
import threading
from pathlib import Path
import json

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️ Rich non disponible - Interface console basique")

class DemoConsoleComplete:
    def __init__(self):
        if RICH_AVAILABLE:
            self.console = Console()
        
        self.mcp_system = None
        self.demo_data = {
            "files_analyzed": [],
            "search_results": [],
            "vault_password": "test123",
            "system_status": "Initialisation..."
        }
        
    def print_header(self, title):
        """Afficher un header formaté"""
        if RICH_AVAILABLE:
            self.console.print(Panel(title, style="bold blue"))
        else:
            print("=" * 70)
            print(f"🎯 {title}")
            print("=" * 70)
            
    def print_success(self, message):
        """Message de succès"""
        if RICH_AVAILABLE:
            self.console.print(f"✅ {message}", style="bold green")
        else:
            print(f"✅ {message}")
            
    def print_error(self, message):
        """Message d'erreur"""
        if RICH_AVAILABLE:
            self.console.print(f"❌ {message}", style="bold red")
        else:
            print(f"❌ {message}")
            
    def print_info(self, message):
        """Message d'info"""
        if RICH_AVAILABLE:
            self.console.print(f"ℹ️ {message}", style="bold cyan")
        else:
            print(f"ℹ️ {message}")
            
    def init_mcp_system(self):
        """Initialiser le système MCP"""
        self.print_header("INITIALISATION DU SYSTÈME MCP")
        
        try:
            # Import ici pour éviter les erreurs
            sys.path.append(os.getcwd())
            
            # Créer et configurer le système MCP manuellement
            self.mcp_system = self.create_mock_mcp_system()
            
            self.print_success("Système MCP initialisé avec succès")
            self.demo_data["system_status"] = "MCP Actif"
            return True
            
        except Exception as e:
            self.print_error(f"Erreur lors de l'initialisation MCP: {e}")
            self.demo_data["system_status"] = "MCP Indisponible"
            return False
            
    def create_mock_mcp_system(self):
        """Créer un système MCP simulé pour la démo"""
        class MockMCPSystem:
            def __init__(self):
                self.active = True
                
            def start(self):
                self.active = True
                
            def stop(self):
                self.active = False
                
            def call_tool(self, agent, tool, params):
                # Simuler les réponses des agents
                if tool == "process_directory":
                    return {
                        "success": True,
                        "files_processed": 5,
                        "sensitive_files": 2,
                        "processing_time": 1.2,
                        "files": [
                            {"name": "document_sensible.txt", "type": "text", "sensitive": True, "summary": "Document avec PII"},
                            {"name": "cours_histoire.txt", "type": "text", "sensitive": False, "summary": "Cours d'histoire moderne"},
                            {"name": "ordonnance_medicale.json", "type": "json", "sensitive": True, "summary": "Données médicales"},
                            {"name": "bulletin_paie.txt", "type": "text", "sensitive": True, "summary": "Bulletin de salaire"},
                            {"name": "recette_cuisine.txt", "type": "text", "sensitive": False, "summary": "Recette de cuisine"}
                        ]
                    }
                elif tool == "smart_search":
                    query = params.get("query", "").lower()
                    results = []
                    
                    if "carte vitale" in query or "vitale" in query:
                        results.append({
                            "name": "document_sensible.txt",
                            "encrypted": True,
                            "confidence": 95,
                            "summary": "Document contenant des informations de carte vitale",
                            "id": "doc_001"
                        })
                    elif "histoire" in query:
                        results.append({
                            "name": "cours_histoire.txt",
                            "encrypted": False,
                            "confidence": 90,
                            "summary": "Cours d'histoire moderne - contenu éducatif",
                            "id": "doc_002"
                        })
                    elif "ordonnance" in query or "médical" in query:
                        results.append({
                            "name": "ordonnance_medicale.json",
                            "encrypted": True,
                            "confidence": 92,
                            "summary": "Ordonnance médicale personnelle",
                            "id": "doc_003"
                        })
                    elif "sensible" in query or "confidentiel" in query:
                        results.extend([
                            {
                                "name": "document_sensible.txt",
                                "encrypted": True,
                                "confidence": 88,
                                "summary": "Document contenant des données sensibles",
                                "id": "doc_001"
                            },
                            {
                                "name": "bulletin_paie.txt",
                                "encrypted": True,
                                "confidence": 85,
                                "summary": "Bulletin de paie avec données personnelles",
                                "id": "doc_004"
                            }
                        ])
                    
                    return {
                        "success": True,
                        "results": results
                    }
                elif tool == "decrypt_file":
                    file_id = params.get("file_id")
                    password = params.get("password")
                    
                    if password == "test123":
                        return {
                            "success": True,
                            "decrypted_path": f"temp_decrypted/{file_id}.txt",
                            "message": "Fichier déchiffré avec succès"
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Mot de passe incorrect"
                        }
                
                return {"success": False, "error": "Outil non reconnu"}
        
        return MockMCPSystem()
        
    def analyze_directory(self):
        """Analyser un répertoire"""
        self.print_header("ANALYSE DE RÉPERTOIRE")
        
        # Demander le répertoire
        if RICH_AVAILABLE:
            directory = Prompt.ask("📁 Répertoire à analyser", default="test_files")
        else:
            directory = input("📁 Répertoire à analyser [test_files]: ") or "test_files"
        
        if not os.path.exists(directory):
            self.print_error(f"Répertoire {directory} non trouvé")
            return False
        
        # Simuler l'analyse avec progress bar
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("🔍 Analyse en cours...", total=None)
                time.sleep(2)  # Simuler le traitement
        else:
            print("🔍 Analyse en cours...")
            time.sleep(2)
        
        # Utiliser le système MCP
        if self.mcp_system:
            result = self.mcp_system.call_tool("Orchestrator", "process_directory", {"directory": directory})
            
            if result.get("success"):
                files_processed = result.get("files_processed", 0)
                sensitive_files = result.get("sensitive_files", 0)
                processing_time = result.get("processing_time", 0)
                
                self.print_success(f"Analyse terminée: {files_processed} fichiers traités")
                
                # Afficher les résultats dans un tableau
                if RICH_AVAILABLE:
                    table = Table(title="📊 Résultats de l'Analyse")
                    table.add_column("Fichier", style="cyan")
                    table.add_column("Type", style="magenta")
                    table.add_column("Statut", style="green")
                    table.add_column("Résumé", style="yellow")
                    
                    for file_info in result.get("files", []):
                        status = "🔒 Sensible" if file_info["sensitive"] else "📄 Public"
                        table.add_row(
                            file_info["name"],
                            file_info["type"],
                            status,
                            file_info.get("summary", "N/A")
                        )
                    
                    self.console.print(table)
                else:
                    print("\n📊 Résultats de l'Analyse:")
                    print("-" * 60)
                    for file_info in result.get("files", []):
                        status = "🔒 Sensible" if file_info["sensitive"] else "📄 Public"
                        print(f"• {file_info['name']} - {status}")
                        print(f"  {file_info.get('summary', 'N/A')}")
                
                # Sauvegarder les résultats
                self.demo_data["files_analyzed"] = result.get("files", [])
                
                return True
            else:
                self.print_error(f"Erreur lors de l'analyse: {result.get('error', 'Erreur inconnue')}")
                return False
        else:
            self.print_error("Système MCP non disponible")
            return False
            
    def smart_search(self):
        """Recherche intelligente"""
        self.print_header("RECHERCHE INTELLIGENTE IA")
        
        # Exemples de recherche
        examples = [
            "trouve ma carte vitale",
            "cours d'histoire", 
            "ordonnance médicale",
            "documents sensibles"
        ]
        
        if RICH_AVAILABLE:
            self.console.print("💡 Exemples de recherche:")
            for i, example in enumerate(examples, 1):
                self.console.print(f"  {i}. {example}")
            self.console.print()
            
            query = Prompt.ask("🤖 Votre recherche")
        else:
            print("💡 Exemples de recherche:")
            for i, example in enumerate(examples, 1):
                print(f"  {i}. {example}")
            print()
            
            query = input("🤖 Votre recherche: ")
        
        if not query:
            self.print_error("Requête vide")
            return False
        
        # Simuler l'analyse IA
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("🧠 Analyse IA du prompt...", total=None)
                time.sleep(1)
        else:
            print("🧠 Analyse IA du prompt...")
            time.sleep(1)
        
        # Utiliser le système MCP pour la recherche
        if self.mcp_system:
            result = self.mcp_system.call_tool("Orchestrator", "smart_search", {"query": query})
            
            if result.get("success"):
                results = result.get("results", [])
                
                if results:
                    self.print_success(f"{len(results)} résultat(s) trouvé(s)")
                    
                    # Afficher les résultats
                    if RICH_AVAILABLE:
                        table = Table(title="🎯 Résultats de Recherche")
                        table.add_column("Fichier", style="cyan")
                        table.add_column("Confiance", style="green")
                        table.add_column("Statut", style="red")
                        table.add_column("Description", style="yellow")
                        
                        for file_result in results:
                            confidence = f"{file_result.get('confidence', 0)}%"
                            status = "🔒 Chiffré" if file_result.get('encrypted') else "📄 Public"
                            table.add_row(
                                file_result['name'],
                                confidence,
                                status,
                                file_result.get('summary', 'N/A')
                            )
                        
                        self.console.print(table)
                    else:
                        print("\n🎯 Résultats de Recherche:")
                        print("-" * 60)
                        for i, file_result in enumerate(results, 1):
                            confidence = file_result.get('confidence', 0)
                            status = "🔒 Chiffré" if file_result.get('encrypted') else "📄 Public"
                            print(f"{i}. {file_result['name']} - {status}")
                            print(f"   Confiance: {confidence}%")
                            print(f"   {file_result.get('summary', 'N/A')}")
                            print()
                    
                    # Proposer l'accès aux fichiers
                    for file_result in results:
                        if file_result.get('encrypted'):
                            if RICH_AVAILABLE:
                                access = Confirm.ask(f"🔐 Accéder à {file_result['name']} (authentification requise)?")
                            else:
                                access = input(f"🔐 Accéder à {file_result['name']} (o/n)? ").lower().startswith('o')
                            
                            if access:
                                self.decrypt_file(file_result)
                        else:
                            self.print_info(f"📂 {file_result['name']} est accessible directement")
                    
                    return True
                else:
                    self.print_error("Aucun résultat trouvé")
                    return False
            else:
                self.print_error(f"Erreur de recherche: {result.get('error', 'Erreur inconnue')}")
                return False
        else:
            self.print_error("Système MCP non disponible")
            return False
            
    def decrypt_file(self, file_result):
        """Déchiffrer un fichier"""
        self.print_info(f"🔐 Accès au fichier sensible: {file_result['name']}")
        
        if RICH_AVAILABLE:
            password = Prompt.ask("Mot de passe", password=True)
        else:
            import getpass
            password = getpass.getpass("Mot de passe: ")
        
        if self.mcp_system:
            result = self.mcp_system.call_tool("Security", "decrypt_file", {
                "file_id": file_result['id'],
                "password": password
            })
            
            if result.get("success"):
                self.print_success("Fichier déchiffré avec succès!")
                self.print_info(f"📁 Emplacement: {result.get('decrypted_path', 'temp_decrypted/')}")
                
                # Proposer d'ouvrir le fichier
                if RICH_AVAILABLE:
                    open_file = Confirm.ask("📂 Ouvrir le fichier?")
                else:
                    open_file = input("📂 Ouvrir le fichier (o/n)? ").lower().startswith('o')
                
                if open_file:
                    self.print_info("📄 Simulation de l'ouverture du fichier...")
                    self.print_info("Contenu: [DONNÉES DÉCHIFFRÉES - CONFIDENTIEL]")
                
            else:
                self.print_error("Mot de passe incorrect")
        else:
            self.print_error("Système MCP non disponible")
            
    def show_system_status(self):
        """Afficher le statut du système"""
        self.print_header("STATUT DU SYSTÈME")
        
        if RICH_AVAILABLE:
            table = Table(title="🖥️ État des Composants")
            table.add_column("Composant", style="cyan")
            table.add_column("Statut", style="green")
            table.add_column("Description", style="yellow")
            
            table.add_row("MCP System", "✅ Actif" if self.mcp_system else "❌ Inactif", "Système multi-agents")
            table.add_row("Agent NLP", "✅ Opérationnel", "Traitement de texte et PII")
            table.add_row("Agent Vision", "✅ Opérationnel", "Analyse d'images")
            table.add_row("Agent Audio", "✅ Opérationnel", "Traitement audio")
            table.add_row("Agent Security", "✅ Opérationnel", "Chiffrement et sécurité")
            table.add_row("File Manager", "✅ Opérationnel", "Gestion de fichiers")
            table.add_row("Vault", "🔒 Sécurisé", "Stockage chiffré")
            table.add_row("IA Llama3", "🤖 Simulé", "Traitement langage naturel")
            
            self.console.print(table)
        else:
            print("🖥️ État des Composants:")
            print("-" * 60)
            print(f"MCP System      : {'✅ Actif' if self.mcp_system else '❌ Inactif'}")
            print(f"Agent NLP       : ✅ Opérationnel")
            print(f"Agent Vision    : ✅ Opérationnel") 
            print(f"Agent Audio     : ✅ Opérationnel")
            print(f"Agent Security  : ✅ Opérationnel")
            print(f"File Manager    : ✅ Opérationnel")
            print(f"Vault           : 🔒 Sécurisé")
            print(f"IA Llama3       : 🤖 Simulé")
            
    def show_help(self):
        """Afficher l'aide"""
        help_text = """
🆘 AIDE - SYSTÈME MULTI-AGENT KACM QUALCOMM

🎯 OBJECTIF:
Démontrer un système multi-agent intelligent pour l'analyse
et la sécurisation automatique de documents avec IA.

🎮 FONCTIONNALITÉS:

1. 📁 ANALYSE DE RÉPERTOIRE
   • Scan automatique des fichiers
   • Détection PII intelligente
   • Classification sensible/public
   • Chiffrement automatique

2. 🤖 RECHERCHE IA
   • Requêtes en langage naturel
   • Analyse d'intention par IA
   • Résultats pertinents
   • Authentification pour fichiers sensibles

3. 🔐 SÉCURITÉ
   • Chiffrement automatique
   • Vault sécurisé
   • Authentification par mot de passe
   • Audit trail complet

🔑 INFORMATIONS IMPORTANTES:
• Mot de passe vault: test123
• Répertoire de test: test_files/
• Types supportés: TXT, JSON, PDF, Images, Audio

🎪 EXEMPLES DE DÉMONSTRATION:
• "trouve ma carte vitale" → Fichier sensible + auth
• "cours d'histoire" → Fichier public + accès direct
• "documents sensibles" → Liste tous les fichiers chiffrés

🔧 ARCHITECTURE:
Interface Console ↔ MCP System ↔ Agents (NLP, Vision, Audio, Security)
"""
        
        if RICH_AVAILABLE:
            self.console.print(Panel(help_text, title="🆘 AIDE", border_style="blue"))
        else:
            print(help_text)
            
    def main_menu(self):
        """Menu principal"""
        while True:
            self.print_header("SYSTÈME MULTI-AGENT - KACM QUALCOMM")
            
            if RICH_AVAILABLE:
                self.console.print("🎮 MENU PRINCIPAL", style="bold magenta")
                self.console.print("1. 📁 Analyser un répertoire")
                self.console.print("2. 🤖 Recherche intelligente")
                self.console.print("3. 🖥️ Statut du système")
                self.console.print("4. 🆘 Aide")
                self.console.print("5. 🚪 Quitter")
                self.console.print()
                
                choice = Prompt.ask("Votre choix", choices=["1", "2", "3", "4", "5"])
            else:
                print("🎮 MENU PRINCIPAL")
                print("1. 📁 Analyser un répertoire")
                print("2. 🤖 Recherche intelligente")
                print("3. 🖥️ Statut du système")
                print("4. 🆘 Aide")
                print("5. 🚪 Quitter")
                print()
                
                choice = input("Votre choix (1-5): ")
            
            if choice == "1":
                self.analyze_directory()
            elif choice == "2":
                self.smart_search()
            elif choice == "3":
                self.show_system_status()
            elif choice == "4":
                self.show_help()
            elif choice == "5":
                self.print_info("Au revoir!")
                break
            else:
                self.print_error("Choix invalide")
            
            if RICH_AVAILABLE:
                Prompt.ask("\nAppuyez sur Entrée pour continuer", default="")
            else:
                input("\nAppuyez sur Entrée pour continuer...")
                
    def run(self):
        """Lancer la démonstration"""
        try:
            # Initialiser le système
            self.init_mcp_system()
            
            # Lancer le menu principal
            self.main_menu()
            
        except KeyboardInterrupt:
            self.print_info("\n🔴 Arrêt demandé par l'utilisateur")
        except Exception as e:
            self.print_error(f"Erreur inattendue: {e}")
        finally:
            if self.mcp_system:
                self.mcp_system.stop()
                self.print_info("🔴 Système MCP arrêté")

def main():
    """Fonction principale"""
    demo = DemoConsoleComplete()
    demo.run()

if __name__ == "__main__":
    main()
