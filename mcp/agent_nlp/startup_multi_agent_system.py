"""
Startup Script - Multi-Agent MCP System
=======================================

Script pour démarrer tous les serveurs MCP du système multi-agents.
Chaque agent fonctionne sur un port différent pour permettre la communication A2A.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List
import psutil

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPSystemManager:
    """Gestionnaire du système MCP multi-agents"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.processes = {}
        self.agent_configs = {
            'orchestrator': {
                'script': 'agent_orchestrator_mcp.py',
                'port': 8001,
                'description': 'Agent Orchestrateur - Coordination générale'
            },
            'nlp': {
                'script': 'agent_nlp_mcp.py',
                'port': 8002,
                'description': 'Agent NLP - Traitement de texte'
            },
            'vision': {
                'script': 'agent_vision_mcp.py',
                'port': 8003,
                'description': 'Agent Vision - Traitement d\'images'
            },
            'audio': {
                'script': 'agent_audio_mcp.py',
                'port': 8004,
                'description': 'Agent Audio - Traitement audio'
            },
            'file_manager': {
                'script': 'agent_file_manager_mcp.py',
                'port': 8005,
                'description': 'Agent File Manager - Gestion des fichiers'
            },
            'security': {
                'script': 'agent_security_mcp.py',
                'port': 8006,
                'description': 'Agent Security - Sécurisation des données'
            }
        }
    
    def check_dependencies(self):
        """Vérifie les dépendances du système"""
        print("🔍 Vérification des dépendances...")
        
        # Vérifier les fichiers agents
        missing_agents = []
        for agent_name, config in self.agent_configs.items():
            script_path = self.base_dir / config['script']
            if not script_path.exists():
                missing_agents.append(f"{agent_name} ({config['script']})")
        
        if missing_agents:
            print(f"❌ Agents manquants: {', '.join(missing_agents)}")
            return False
        
        # Vérifier les ports disponibles
        occupied_ports = []
        for agent_name, config in self.agent_configs.items():
            if self.is_port_occupied(config['port']):
                occupied_ports.append(f"{agent_name}:{config['port']}")
        
        if occupied_ports:
            print(f"⚠️ Ports occupés: {', '.join(occupied_ports)}")
            print("  Utilisez stop_all_agents() pour arrêter les processus existants")
        
        # Vérifier Python et les packages
        try:
            import mcp
            import pydantic
            print("✅ Packages MCP disponibles")
        except ImportError as e:
            print(f"❌ Packages manquants: {e}")
            return False
        
        print("✅ Vérification terminée")
        return True
    
    def is_port_occupied(self, port: int) -> bool:
        """Vérifie si un port est occupé"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False
    
    def start_agent(self, agent_name: str) -> bool:
        """Démarre un agent spécifique"""
        if agent_name not in self.agent_configs:
            print(f"❌ Agent inconnu: {agent_name}")
            return False
        
        config = self.agent_configs[agent_name]
        script_path = self.base_dir / config['script']
        
        print(f"🚀 Démarrage {agent_name} ({config['description']})...")
        
        try:
            # Démarrer le processus
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.base_dir),
                text=True
            )
            
            # Attendre un peu pour vérifier le démarrage
            time.sleep(2)
            
            if process.poll() is None:  # Processus encore en cours
                self.processes[agent_name] = {
                    'process': process,
                    'config': config,
                    'started_at': time.time()
                }
                print(f"✅ {agent_name} démarré (PID: {process.pid}, Port: {config['port']})")
                return True
            else:
                # Processus terminé immédiatement
                stdout, stderr = process.communicate()
                print(f"❌ {agent_name} échec de démarrage:")
                print(f"  stdout: {stdout}")
                print(f"  stderr: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur démarrage {agent_name}: {e}")
            return False
    
    def stop_agent(self, agent_name: str) -> bool:
        """Arrête un agent spécifique"""
        if agent_name not in self.processes:
            print(f"⚠️ Agent {agent_name} non démarré")
            return False
        
        process_info = self.processes[agent_name]
        process = process_info['process']
        
        try:
            print(f"🛑 Arrêt {agent_name}...")
            process.terminate()
            
            # Attendre l'arrêt gracieux
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"⚠️ Arrêt forcé de {agent_name}")
                process.kill()
                process.wait()
            
            del self.processes[agent_name]
            print(f"✅ {agent_name} arrêté")
            return True
            
        except Exception as e:
            print(f"❌ Erreur arrêt {agent_name}: {e}")
            return False
    
    def start_all_agents(self):
        """Démarre tous les agents"""
        print("🚀 Démarrage du système multi-agents MCP")
        print("="*60)
        
        if not self.check_dependencies():
            print("❌ Vérification des dépendances échouée")
            return False
        
        success_count = 0
        
        # Démarrer les agents dans l'ordre
        agent_order = ['nlp', 'vision', 'audio', 'file_manager', 'security', 'orchestrator']
        
        for agent_name in agent_order:
            if self.start_agent(agent_name):
                success_count += 1
            else:
                print(f"⚠️ Échec démarrage {agent_name}, continuons...")
        
        print(f"\n🎯 Système démarré: {success_count}/{len(agent_order)} agents")
        
        if success_count > 0:
            print(f"\n🌐 Agents disponibles:")
            for agent_name, process_info in self.processes.items():
                config = process_info['config']
                print(f"  - {agent_name}: http://localhost:{config['port']}")
            
            print(f"\n💡 Commandes disponibles:")
            print(f"  - status() : Statut des agents")
            print(f"  - stop_all_agents() : Arrêter tous les agents")
            print(f"  - restart_agent('nom') : Redémarrer un agent")
        
        return success_count > 0
    
    def stop_all_agents(self):
        """Arrête tous les agents"""
        print("🛑 Arrêt du système multi-agents")
        
        for agent_name in list(self.processes.keys()):
            self.stop_agent(agent_name)
        
        print("✅ Tous les agents arrêtés")
    
    def restart_agent(self, agent_name: str):
        """Redémarre un agent spécifique"""
        print(f"🔄 Redémarrage de {agent_name}")
        
        if agent_name in self.processes:
            self.stop_agent(agent_name)
        
        time.sleep(1)
        self.start_agent(agent_name)
    
    def status(self):
        """Affiche le statut du système"""
        print("📊 Statut du système multi-agents MCP")
        print("="*50)
        
        if not self.processes:
            print("ℹ️ Aucun agent démarré")
            return
        
        print(f"Agents actifs: {len(self.processes)}")
        
        for agent_name, process_info in self.processes.items():
            process = process_info['process']
            config = process_info['config']
            uptime = time.time() - process_info['started_at']
            
            status = "🟢 Actif" if process.poll() is None else "🔴 Arrêté"
            
            print(f"  {agent_name}:")
            print(f"    Status: {status}")
            print(f"    PID: {process.pid}")
            print(f"    Port: {config['port']}")
            print(f"    Uptime: {uptime:.1f}s")
            print(f"    Description: {config['description']}")
    
    def run_test_workflow(self):
        """Lance le workflow de test"""
        print("🧪 Lancement du workflow de test")
        
        if len(self.processes) < 3:
            print("⚠️ Pas assez d'agents démarrés pour les tests")
            return
        
        try:
            # Lancer le script de test
            result = subprocess.run(
                [sys.executable, 'test_multi_agent_workflow.py'],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True
            )
            
            print("📋 Résultat du test:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Erreurs:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")

# Instance globale du gestionnaire
manager = MCPSystemManager()

# Fonctions utilitaires pour l'utilisateur
def start_all_agents():
    """Démarre tous les agents"""
    return manager.start_all_agents()

def stop_all_agents():
    """Arrête tous les agents"""
    return manager.stop_all_agents()

def restart_agent(agent_name: str):
    """Redémarre un agent"""
    return manager.restart_agent(agent_name)

def status():
    """Affiche le statut"""
    return manager.status()

def test_workflow():
    """Lance les tests"""
    return manager.run_test_workflow()

def main():
    """Point d'entrée principal"""
    print("🎯 Multi-Agent MCP System Manager")
    print("Gestionnaire du système multi-agents avec MCP")
    print("="*60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            start_all_agents()
        elif command == "stop":
            stop_all_agents()
        elif command == "status":
            status()
        elif command == "test":
            test_workflow()
        elif command == "restart":
            if len(sys.argv) > 2:
                restart_agent(sys.argv[2])
            else:
                print("❌ Spécifiez le nom de l'agent à redémarrer")
        else:
            print(f"❌ Commande inconnue: {command}")
            print("Commandes disponibles: start, stop, status, test, restart <agent>")
    else:
        # Mode interactif
        print("🚀 Mode interactif activé")
        print("Commandes disponibles:")
        print("  start_all_agents() - Démarre tous les agents")
        print("  stop_all_agents() - Arrête tous les agents")
        print("  status() - Affiche le statut")
        print("  test_workflow() - Lance les tests")
        print("  restart_agent('nom') - Redémarre un agent")
        
        # Démarrer automatiquement en mode interactif
        start_all_agents()

if __name__ == "__main__":
    main()
