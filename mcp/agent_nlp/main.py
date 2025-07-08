#!/usr/bin/env python3
"""
Main Script - Multi-Agent System
================================

Script principal pour démarrer et tester le système multi-agents.
Point d'entrée unique pour l'utilisateur.
"""

import asyncio
import os
import sys
import argparse
from pathlib import Path
import logging

# Ajouter le répertoire du projet au chemin Python
sys.path.insert(0, str(Path(__file__).parent))

# Imports des modules du système
from startup_multi_agent_system import MCPSystemManager
from test_multi_agent_workflow import MultiAgentTestSuite

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Affiche la bannière du système"""
    print("="*80)
    print("🚀 SYSTÈME MULTI-AGENTS MCP")
    print("   Intelligence Artificielle Distribuée")
    print("   Hackathon Qualcomm Edge-AI")
    print("="*80)
    print()

def print_help():
    """Affiche l'aide du système"""
    print("📋 COMMANDES DISPONIBLES:")
    print()
    print("🔧 GESTION DU SYSTÈME:")
    print("  start                    - Démarrer tous les agents")
    print("  stop                     - Arrêter tous les agents")
    print("  restart                  - Redémarrer tous les agents")
    print("  status                   - Afficher le statut des agents")
    print()
    print("🧪 TESTS ET VALIDATION:")
    print("  test                     - Lancer la suite de tests complète")
    print("  test-quick               - Tests rapides")
    print("  demo                     - Démonstration du système")
    print()
    print("🔍 TRAITEMENT DE FICHIERS:")
    print("  process <directory>      - Traiter tous les fichiers d'un répertoire")
    print("  scan <directory>         - Scanner un répertoire (sans traitement)")
    print("  analyze <file>           - Analyser un fichier spécifique")
    print()
    print("📊 UTILITAIRES:")
    print("  logs                     - Afficher les logs récents")
    print("  config                   - Afficher la configuration")
    print("  help                     - Afficher cette aide")
    print()

async def process_directory(directory_path: str):
    """Traite un répertoire avec le système multi-agents"""
    print(f"🔍 Traitement du répertoire: {directory_path}")
    print("-" * 50)
    
    try:
        # Vérifier que le répertoire existe
        path = Path(directory_path)
        if not path.exists():
            print(f"❌ Répertoire non trouvé: {directory_path}")
            return False
        
        # Importer et utiliser l'orchestrateur
        from agent_orchestrator_mcp import AgentOrchestrator
        
        orchestrator = AgentOrchestrator()
        
        # Scanner le répertoire
        print("📂 Scan du répertoire...")
        scan_result = await orchestrator.scan_directory(directory_path)
        
        print(f"✅ Scan terminé:")
        print(f"  📁 Fichiers trouvés: {len(scan_result.files)}")
        print(f"  📝 Fichiers texte: {len([f for f in scan_result.files if f.file_type == 'text'])}")
        print(f"  🖼️  Fichiers image: {len([f for f in scan_result.files if f.file_type == 'image'])}")
        print(f"  🎵 Fichiers audio: {len([f for f in scan_result.files if f.file_type == 'audio'])}")
        print()
        
        # Traiter les fichiers
        print("⚙️ Traitement par les agents spécialisés...")
        processing_result = await orchestrator.process_directory(directory_path)
        
        print(f"✅ Traitement terminé:")
        print(f"  📋 Fichiers traités: {len(processing_result.get('processed_files', []))}")
        print(f"  ⚠️  Avertissements: {len(processing_result.get('warnings', []))}")
        print(f"  🔒 Actions de sécurité: {len(processing_result.get('security_actions', []))}")
        
        # Afficher les résultats détaillés
        if processing_result.get('processed_files'):
            print("\n📊 RÉSULTATS DÉTAILLÉS:")
            for result in processing_result['processed_files'][:5]:  # Afficher les 5 premiers
                print(f"  📁 {Path(result['file_path']).name}")
                print(f"     🤖 Agent: {result.get('agent_type', 'unknown')}")
                print(f"     📝 Résumé: {result.get('summary', 'N/A')[:80]}...")
                print(f"     ⚠️  Warning: {result.get('warning', False)}")
                print()
            
            if len(processing_result['processed_files']) > 5:
                print(f"  ... et {len(processing_result['processed_files']) - 5} autres fichiers")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du traitement: {e}")
        logger.error(f"Erreur traitement répertoire {directory_path}: {e}")
        return False

async def demo_system():
    """Démonstration du système avec des fichiers d'exemple"""
    print("🎬 DÉMONSTRATION DU SYSTÈME MULTI-AGENTS")
    print("-" * 50)
    
    # Créer un répertoire de démonstration
    demo_dir = Path("demo_files")
    demo_dir.mkdir(exist_ok=True)
    
    # Créer des fichiers d'exemple
    demo_files = {
        "document_normal.txt": "Ceci est un document de test normal contenant des informations publiques.",
        "document_sensible.txt": "Ce document contient des informations sensibles comme jean.dupont@example.com et 06 12 34 56 78.",
        "rapport.json": '{"titre": "Rapport mensuel", "contenu": "Données de performance", "date": "2024-01-01"}',
        "image_test.jpg": "FAKE_IMAGE_DATA_FOR_DEMO",
        "audio_test.mp3": "FAKE_AUDIO_DATA_FOR_DEMO"
    }
    
    print("📝 Création des fichiers de démonstration...")
    for filename, content in demo_files.items():
        file_path = demo_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ {len(demo_files)} fichiers créés dans {demo_dir}")
    print()
    
    # Traiter le répertoire de démonstration
    success = await process_directory(str(demo_dir))
    
    if success:
        print("🎉 Démonstration terminée avec succès!")
    else:
        print("❌ Démonstration échouée")
    
    # Nettoyer les fichiers de démonstration
    print("\n🧹 Nettoyage des fichiers de démonstration...")
    import shutil
    shutil.rmtree(demo_dir)
    print("✅ Nettoyage terminé")

async def run_tests(quick: bool = False):
    """Lance les tests du système"""
    print("🧪 LANCEMENT DES TESTS")
    print("-" * 50)
    
    try:
        test_suite = MultiAgentTestSuite()
        
        if quick:
            print("⚡ Mode test rapide")
            # Tests rapides seulement
            test_suite.setup_test_environment()
            await test_suite.test_orchestrator_scan()
            test_suite.cleanup()
        else:
            print("🔍 Suite de tests complète")
            # Tests complets
            await test_suite.run_all_tests()
        
        print("✅ Tests terminés")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        logger.error(f"Erreur tests: {e}")
        return False

def show_logs():
    """Affiche les logs récents"""
    print("📋 LOGS RÉCENTS")
    print("-" * 30)
    
    log_dir = Path("logs")
    if not log_dir.exists():
        print("ℹ️ Aucun log disponible")
        return
    
    log_files = list(log_dir.glob("*.log"))
    if not log_files:
        print("ℹ️ Aucun fichier log trouvé")
        return
    
    # Afficher les dernières lignes de chaque log
    for log_file in log_files[-3:]:  # 3 derniers fichiers
        print(f"\n📄 {log_file.name}:")
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Afficher les 10 dernières lignes
                for line in lines[-10:]:
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"  ❌ Erreur lecture: {e}")

def show_config():
    """Affiche la configuration du système"""
    print("⚙️ CONFIGURATION DU SYSTÈME")
    print("-" * 40)
    
    try:
        from startup_multi_agent_system import MCPSystemManager
        manager = MCPSystemManager()
        
        print("🤖 AGENTS CONFIGURÉS:")
        for agent_name, config in manager.agent_configs.items():
            print(f"  {agent_name}:")
            print(f"    📄 Script: {config['script']}")
            print(f"    🌐 Port: {config['port']}")
            print(f"    📝 Description: {config['description']}")
            print()
        
        print("📁 RÉPERTOIRES:")
        print(f"  logs/")
        print(f"  output/")
        print(f"  results/")
        print()
        
        print("🔧 VARIABLES D'ENVIRONNEMENT:")
        env_vars = ['OLLAMA_BASE_URL', 'LLAMA_MODEL', 'LOG_LEVEL']
        for var in env_vars:
            value = os.getenv(var, 'Non défini')
            print(f"  {var}: {value}")
        
    except Exception as e:
        print(f"❌ Erreur affichage configuration: {e}")

async def main():
    """Point d'entrée principal"""
    print_banner()
    
    # Parser les arguments
    parser = argparse.ArgumentParser(description="Système Multi-Agents MCP")
    parser.add_argument('command', nargs='?', help='Commande à exécuter')
    parser.add_argument('target', nargs='?', help='Cible (répertoire ou fichier)')
    parser.add_argument('--quick', action='store_true', help='Mode rapide pour les tests')
    
    args = parser.parse_args()
    
    # Gestionnaire du système
    manager = MCPSystemManager()
    
    if not args.command:
        print_help()
        return
    
    command = args.command.lower()
    
    try:
        if command == 'start':
            print("🚀 Démarrage du système...")
            manager.start_all_agents()
            
        elif command == 'stop':
            print("🛑 Arrêt du système...")
            manager.stop_all_agents()
            
        elif command == 'restart':
            print("🔄 Redémarrage du système...")
            manager.stop_all_agents()
            await asyncio.sleep(2)
            manager.start_all_agents()
            
        elif command == 'status':
            manager.status()
            
        elif command == 'test':
            await run_tests(quick=args.quick)
            
        elif command == 'test-quick':
            await run_tests(quick=True)
            
        elif command == 'demo':
            await demo_system()
            
        elif command == 'process':
            if not args.target:
                print("❌ Spécifiez un répertoire à traiter")
                return
            await process_directory(args.target)
            
        elif command == 'scan':
            if not args.target:
                print("❌ Spécifiez un répertoire à scanner")
                return
            # Scanner seulement
            from agent_orchestrator_mcp import AgentOrchestrator
            orchestrator = AgentOrchestrator()
            result = await orchestrator.scan_directory(args.target)
            print(f"📂 Résultats du scan: {len(result.files)} fichiers trouvés")
            
        elif command == 'analyze':
            if not args.target:
                print("❌ Spécifiez un fichier à analyser")
                return
            print(f"🔍 Analyse du fichier: {args.target}")
            # Analyser un fichier spécifique
            
        elif command == 'logs':
            show_logs()
            
        elif command == 'config':
            show_config()
            
        elif command == 'help':
            print_help()
            
        else:
            print(f"❌ Commande inconnue: {command}")
            print_help()
            
    except KeyboardInterrupt:
        print("\n👋 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        logger.error(f"Erreur dans main: {e}")

if __name__ == "__main__":
    asyncio.run(main())
