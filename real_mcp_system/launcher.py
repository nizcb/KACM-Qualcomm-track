#!/usr/bin/env python3
"""
🚀 Lancement Rapide - Système MCP Multi-Agents
=============================================

Script de lancement rapide avec menu pour toutes les fonctionnalités.
"""

import os
import sys
import subprocess
from pathlib import Path

class QuickLauncher:
    """Lanceur rapide pour le système MCP"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        
    def print_banner(self):
        """Bannière principale"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║      🚀 SYSTÈME MCP MULTI-AGENTS - LANCEMENT RAPIDE 🚀           ║
║                                                                  ║
║      🎯 KACM Qualcomm Track                                      ║
║      🤖 6 Agents Spécialisés + IA Ollama/Llama                  ║
║      🔐 Détection PII + Sécurisation Automatique                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    
    def print_menu(self):
        """Menu principal"""
        print("=" * 70)
        print("🎯 MENU PRINCIPAL")
        print("=" * 70)
        print()
        print("📊 GESTION DU SYSTÈME:")
        print("  1. 🚀 Démarrer tous les agents")
        print("  2. 🛑 Arrêter tous les agents")
        print("  3. 🏥 Vérifier la santé du système")
        print("  4. 📋 Statut des agents")
        print()
        print("🧪 TESTS ET DÉMONSTRATIONS:")
        print("  5. 🎬 Démonstration automatique complète")
        print("  6. 🎯 Interface interactive avec Ollama")
        print("  7. ⚡ Test rapide du workflow")
        print("  8. 🧪 Test d'un fichier spécifique")
        print()
        print("📚 DOCUMENTATION ET AIDE:")
        print("  9. 📖 Voir la documentation")
        print(" 10. 🔧 Vérifier les prérequis")
        print(" 11. 📁 Explorer les fichiers de test")
        print()
        print("  0. 🚪 Quitter")
        print()
        print("=" * 70)
    
    def check_prerequisites(self):
        """Vérifier les prérequis"""
        print("\n🔍 Vérification des prérequis...")
        
        # Python
        python_version = sys.version_info
        if python_version >= (3, 9):
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            print(f"❌ Python {python_version.major}.{python_version.minor} (requis: 3.9+)")
        
        # Ollama
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Ollama installé")
                if "llama3.2:1b" in result.stdout:
                    print("✅ Modèle Llama 3.2:1b disponible")
                else:
                    print("⚠️ Modèle Llama 3.2:1b non trouvé")
                    print("   Installez avec: ollama pull llama3.2:1b")
            else:
                print("❌ Ollama non trouvé")
        except FileNotFoundError:
            print("❌ Ollama non installé")
            print("   Installez depuis: https://ollama.ai/download")
        
        # Dépendances Python
        try:
            import mcp
            import fastmcp
            import requests
            import pydantic
            print("✅ Dépendances Python installées")
        except ImportError as e:
            print(f"❌ Dépendances manquantes: {e}")
            print("   Installez avec: pip install -r requirements.txt")
        
        # Structure des fichiers
        agents_dir = self.base_dir / "agents"
        if agents_dir.exists():
            agents = list(agents_dir.glob("agent_*_mcp.py"))
            print(f"✅ {len(agents)} agents trouvés")
        else:
            print("❌ Répertoire agents/ non trouvé")
        
        data_dir = self.base_dir / "data" / "test_files"
        if data_dir.exists():
            files = list(data_dir.glob("*"))
            print(f"✅ {len(files)} fichiers de test trouvés")
        else:
            print("❌ Fichiers de test non trouvés")
    
    def run_command(self, command: list, description: str):
        """Exécuter une commande"""
        print(f"\n{description}...")
        try:
            result = subprocess.run(command, cwd=str(self.base_dir), check=True)
            print("✅ Terminé avec succès")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ Commande non trouvée: {' '.join(command)}")
            return False
    
    def explore_test_files(self):
        """Explorer les fichiers de test"""
        print("\n📁 Fichiers de test disponibles:")
        
        data_dir = self.base_dir / "data" / "test_files"
        if not data_dir.exists():
            print("❌ Répertoire de test non trouvé!")
            return
        
        files = list(data_dir.glob("*"))
        if not files:
            print("❌ Aucun fichier de test trouvé!")
            return
        
        print()
        for i, file in enumerate(files, 1):
            if file.is_file():
                size = file.stat().st_size
                # Indiquer le type de contenu
                content_type = "📄 Texte"
                if file.suffix.lower() in ['.json']:
                    content_type = "📋 JSON"
                elif file.suffix.lower() in ['.csv']:
                    content_type = "📊 CSV"
                elif file.suffix.lower() in ['.md']:
                    content_type = "📝 Markdown"
                elif 'jpg' in file.name.lower() or 'png' in file.name.lower():
                    content_type = "🖼️ Image"
                elif 'mp3' in file.name.lower() or 'wav' in file.name.lower():
                    content_type = "🔊 Audio"
                
                # Indiquer si sensible
                sensitive = ""
                if any(word in file.name.lower() for word in ['pii', 'confidential', 'carte_identite', 'reunion']):
                    sensitive = " 🔴"
                
                print(f"  {i:2d}. {content_type} {file.name:<25} ({size:,} bytes){sensitive}")
        
        print(f"\n🔴 = Fichier potentiellement sensible")
        print(f"Total: {len(files)} fichiers")
    
    def show_documentation(self):
        """Afficher la documentation"""
        print("\n📖 Documentation du système:")
        print()
        print("📁 Fichiers de documentation:")
        print("  • README.md - Guide complet du système")
        print("  • config.py - Configuration des agents")
        print("  • requirements.txt - Dépendances Python")
        print()
        print("🎯 Scripts principaux:")
        print("  • system_manager.py - Gestion des agents")
        print("  • interactive_interface.py - Interface complète")
        print("  • auto_demo.py - Démonstration automatique")
        print("  • test_interface.py - Tests de workflow")
        print()
        print("🤖 Agents disponibles:")
        print("  • agent_orchestrator_mcp.py - Coordination générale")
        print("  • agent_nlp_mcp.py - Analyse de texte + IA")
        print("  • agent_vision_mcp.py - Traitement d'images")
        print("  • agent_audio_mcp.py - Analyse audio")
        print("  • agent_file_manager_mcp.py - Consolidation")
        print("  • agent_security_mcp.py - Chiffrement/sécurité")
        print()
        print("🌐 Ports utilisés:")
        print("  • 8001 - Orchestrateur")
        print("  • 8002 - Agent NLP")
        print("  • 8003 - Agent Vision")
        print("  • 8004 - Agent Audio")
        print("  • 8005 - File Manager")
        print("  • 8006 - Security Agent")
    
    def run_interactive(self):
        """Boucle interactive principale"""
        while True:
            self.print_banner()
            self.print_menu()
            
            try:
                choice = input("Votre choix: ").strip()
                
                if choice == "1":
                    self.run_command(
                        [sys.executable, "system_manager.py", "start"],
                        "🚀 Démarrage de tous les agents"
                    )
                
                elif choice == "2":
                    self.run_command(
                        [sys.executable, "system_manager.py", "stop"],
                        "🛑 Arrêt de tous les agents"
                    )
                
                elif choice == "3":
                    self.run_command(
                        [sys.executable, "system_manager.py", "health"],
                        "🏥 Vérification de la santé du système"
                    )
                
                elif choice == "4":
                    self.run_command(
                        [sys.executable, "system_manager.py", "status"],
                        "📋 Statut des agents"
                    )
                
                elif choice == "5":
                    self.run_command(
                        [sys.executable, "auto_demo.py"],
                        "🎬 Lancement de la démonstration automatique"
                    )
                
                elif choice == "6":
                    self.run_command(
                        [sys.executable, "interactive_interface.py"],
                        "🎯 Lancement de l'interface interactive"
                    )
                
                elif choice == "7":
                    self.run_command(
                        [sys.executable, "test_interface.py", "--workflow"],
                        "⚡ Test rapide du workflow complet"
                    )
                
                elif choice == "8":
                    self.run_command(
                        [sys.executable, "test_interface.py"],
                        "🧪 Interface de test de fichiers"
                    )
                
                elif choice == "9":
                    self.show_documentation()
                
                elif choice == "10":
                    self.check_prerequisites()
                
                elif choice == "11":
                    self.explore_test_files()
                
                elif choice == "0":
                    print("\n👋 Au revoir!")
                    break
                
                else:
                    print("\n❌ Choix invalide!")
                
                if choice != "0":
                    input("\nAppuyez sur Entrée pour continuer...")
                    
            except KeyboardInterrupt:
                print("\n👋 Au revoir!")
                break

def main():
    """Point d'entrée principal"""
    launcher = QuickLauncher()
    launcher.run_interactive()

if __name__ == "__main__":
    main()
