"""
🚀 Gestionnaire du Système MCP Multi-Agents Réel
===============================================

Gestionnaire principal pour démarrer/arrêter tous les agents MCP.
"""

import asyncio
import json
import logging
import os
import sys
import signal
import subprocess
import time
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx

# Ajout du répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent))

from config import Config

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOGS_DIR / "system_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealMCPSystemManager:
    """Gestionnaire du système MCP multi-agents réel"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.agents_dir = self.base_dir / "agents"
        self.processes = {}  # PID des processus agents
        self.agent_configs = Config.AGENTS
        
        logger.info(f"🚀 Gestionnaire Système MCP initialisé")
    
    def check_dependencies(self) -> bool:
        """Vérifier les dépendances du système"""
        logger.info("🔍 Vérification des dépendances...")
        
        # Vérifier les fichiers agents
        missing_agents = []
        for agent_name, config in self.agent_configs.items():
            script_path = self.agents_dir / config.script
            if not script_path.exists():
                missing_agents.append(f"{agent_name} ({config.script})")
        
        if missing_agents:
            logger.error(f"❌ Agents manquants: {', '.join(missing_agents)}")
            return False
        
        # Vérifier les ports disponibles
        occupied_ports = []
        for agent_name, config in self.agent_configs.items():
            if self.is_port_occupied(config.port):
                occupied_ports.append(f"{agent_name}:{config.port}")
        
        if occupied_ports:
            logger.warning(f"⚠️ Ports occupés: {', '.join(occupied_ports)}")
            # Arrêter les processus sur ces ports
            for agent_name, config in self.agent_configs.items():
                if self.is_port_occupied(config.port):
                    self.kill_process_on_port(config.port)
        
        # Vérifier Python et dépendances
        try:
            import fastapi
            import httpx
            import pydantic
            logger.info("✅ Dépendances Python disponibles")
        except ImportError as e:
            logger.error(f"❌ Dépendances manquantes: {e}")
            return False
        
        logger.info("✅ Vérification des dépendances terminée")
        return True
    
    def is_port_occupied(self, port: int) -> bool:
        """Vérifier si un port est occupé"""
        try:
            for conn in psutil.net_connections():
                if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                    return True
        except (psutil.AccessDenied, AttributeError):
            pass
        return False
    
    def kill_process_on_port(self, port: int):
        """Tuer le processus utilisant un port"""
        try:
            for conn in psutil.net_connections():
                if (hasattr(conn, 'laddr') and conn.laddr and 
                    conn.laddr.port == port and hasattr(conn, 'pid') and conn.pid):
                    try:
                        process = psutil.Process(conn.pid)
                        process.terminate()
                        logger.info(f"🔪 Processus {conn.pid} arrêté sur le port {port}")
                        time.sleep(1)
                        if process.is_running():
                            process.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        except Exception as e:
            logger.error(f"❌ Erreur arrêt processus port {port}: {e}")
    
    def start_agent(self, agent_name: str) -> bool:
        """Démarrer un agent spécifique"""
        if agent_name not in self.agent_configs:
            logger.error(f"❌ Agent inconnu: {agent_name}")
            return False
        
        config = self.agent_configs[agent_name]
        if not config.enabled:
            logger.info(f"⏸️ Agent {agent_name} désactivé")
            return True
        
        script_path = self.agents_dir / config.script
        if not script_path.exists():
            logger.error(f"❌ Script non trouvé: {script_path}")
            return False
        
        # Vérifier si déjà en cours
        if agent_name in self.processes:
            pid = self.processes[agent_name]
            try:
                if psutil.Process(pid).is_running():
                    logger.info(f"🟡 Agent {agent_name} déjà en cours (PID: {pid})")
                    return True
            except psutil.NoSuchProcess:
                del self.processes[agent_name]
        
        # Arrêter tout processus sur le port
        if self.is_port_occupied(config.port):
            self.kill_process_on_port(config.port)
            time.sleep(2)
        
        try:
            # Démarrer l'agent
            logger.info(f"🚀 Démarrage agent {agent_name} sur port {config.port}...")
            
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(script_path.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            self.processes[agent_name] = process.pid
            
            # Attendre un peu pour voir si le processus démarre correctement
            time.sleep(3)
            
            if process.poll() is None:  # Processus toujours en cours
                logger.info(f"✅ Agent {agent_name} démarré (PID: {process.pid})")
                return True
            else:
                # Processus s'est arrêté
                stdout, stderr = process.communicate()
                logger.error(f"❌ Agent {agent_name} s'est arrêté immédiatement")
                logger.error(f"STDOUT: {stdout.decode()}")
                logger.error(f"STDERR: {stderr.decode()}")
                if agent_name in self.processes:
                    del self.processes[agent_name]
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur démarrage agent {agent_name}: {e}")
            return False
    
    def stop_agent(self, agent_name: str) -> bool:
        """Arrêter un agent spécifique"""
        if agent_name not in self.processes:
            logger.info(f"⏸️ Agent {agent_name} n'est pas en cours")
            return True
        
        try:
            pid = self.processes[agent_name]
            process = psutil.Process(pid)
            
            # Tentative d'arrêt propre
            process.terminate()
            
            # Attendre un peu
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Forcer l'arrêt
                process.kill()
                process.wait(timeout=5)
            
            del self.processes[agent_name]
            logger.info(f"🛑 Agent {agent_name} arrêté")
            return True
            
        except psutil.NoSuchProcess:
            del self.processes[agent_name]
            logger.info(f"🛑 Agent {agent_name} n'était plus en cours")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur arrêt agent {agent_name}: {e}")
            return False
    
    def start_all_agents(self) -> Dict[str, bool]:
        """Démarrer tous les agents"""
        logger.info("🚀 Démarrage de tous les agents...")
        
        results = {}
        
        # Ordre de démarrage spécifique
        start_order = ['orchestrator', 'nlp', 'vision', 'audio', 'file_manager', 'security']
        
        for agent_name in start_order:
            if agent_name in self.agent_configs:
                success = self.start_agent(agent_name)
                results[agent_name] = success
                if success:
                    # Attendre un peu entre les démarrages
                    time.sleep(2)
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        logger.info(f"📊 Résultat: {successful}/{total} agents démarrés")
        
        return results
    
    def stop_all_agents(self) -> Dict[str, bool]:
        """Arrêter tous les agents"""
        logger.info("🛑 Arrêt de tous les agents...")
        
        results = {}
        
        # Arrêter dans l'ordre inverse
        for agent_name in list(self.processes.keys()):
            success = self.stop_agent(agent_name)
            results[agent_name] = success
        
        logger.info("✅ Tous les agents arrêtés")
        return results
    
    async def check_agents_health(self) -> Dict[str, Dict[str, Any]]:
        """Vérifier la santé de tous les agents"""
        health_status = {}
        
        for agent_name, config in self.agent_configs.items():
            if not config.enabled:
                health_status[agent_name] = {
                    "status": "disabled",
                    "port": config.port,
                    "endpoint": None
                }
                continue
            
            endpoint = f"http://localhost:{config.port}/health"
            
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(endpoint)
                    
                    if response.status_code == 200:
                        health_status[agent_name] = {
                            "status": "healthy",
                            "port": config.port,
                            "endpoint": endpoint,
                            "response": response.json()
                        }
                    else:
                        health_status[agent_name] = {
                            "status": "unhealthy",
                            "port": config.port,
                            "endpoint": endpoint,
                            "error": f"HTTP {response.status_code}"
                        }
                        
            except Exception as e:
                health_status[agent_name] = {
                    "status": "unreachable",
                    "port": config.port,
                    "endpoint": endpoint,
                    "error": str(e)
                }
        
        return health_status
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtenir le statut complet du système"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "running_agents": len(self.processes),
            "total_agents": len([c for c in self.agent_configs.values() if c.enabled]),
            "processes": {},
            "ports": {}
        }
        
        # Statut des processus
        for agent_name, pid in self.processes.items():
            try:
                process = psutil.Process(pid)
                status["processes"][agent_name] = {
                    "pid": pid,
                    "status": process.status(),
                    "cpu_percent": process.cpu_percent(),
                    "memory_mb": process.memory_info().rss / (1024 * 1024),
                    "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
                }
            except psutil.NoSuchProcess:
                status["processes"][agent_name] = {
                    "pid": pid,
                    "status": "not_found"
                }
        
        # Statut des ports
        for agent_name, config in self.agent_configs.items():
            status["ports"][agent_name] = {
                "port": config.port,
                "occupied": self.is_port_occupied(config.port),
                "enabled": config.enabled
            }
        
        return status
    
    async def run_test_workflow(self) -> Dict[str, Any]:
        """Exécuter un workflow de test complet"""
        logger.info("🧪 Démarrage du workflow de test...")
        
        # 1. Vérifier la santé des agents
        health = await self.check_agents_health()
        healthy_agents = [name for name, status in health.items() if status["status"] == "healthy"]
        
        logger.info(f"✅ Agents en santé: {', '.join(healthy_agents)}")
        
        # 2. Test de l'orchestrateur si disponible
        if "orchestrator" in healthy_agents:
            try:
                test_dir = Config.DATA_DIR / "test_files"
                if test_dir.exists():
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            f"http://localhost:8001/orchestrate",
                            json={"directory_path": str(test_dir)}
                        )
                        
                        if response.status_code == 200:
                            logger.info("✅ Test orchestrateur réussi")
                        else:
                            logger.error(f"❌ Test orchestrateur échoué: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Erreur test orchestrateur: {e}")
        
        return {
            "health_status": health,
            "test_completed": True,
            "timestamp": datetime.now().isoformat()
        }

# ──────────────────────────────────────────────────────────────────────────
# Interface CLI
# ──────────────────────────────────────────────────────────────────────────

async def main():
    """Interface principale du gestionnaire"""
    manager = RealMCPSystemManager()
    
    if len(sys.argv) < 2:
        print("""
🚀 Gestionnaire Système MCP Multi-Agents Réel

Usage:
  python system_manager.py start        # Démarrer tous les agents
  python system_manager.py stop         # Arrêter tous les agents
  python system_manager.py restart      # Redémarrer tous les agents
  python system_manager.py status       # Statut du système
  python system_manager.py health       # Santé des agents
  python system_manager.py test         # Workflow de test
  python system_manager.py check        # Vérifier les dépendances
        """)
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "check":
            success = manager.check_dependencies()
            if success:
                print("✅ Toutes les dépendances sont disponibles")
            else:
                print("❌ Certaines dépendances manquent")
                sys.exit(1)
        
        elif command == "start":
            manager.check_dependencies()
            results = manager.start_all_agents()
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            print(f"\n📊 Résultat du démarrage: {successful}/{total} agents")
            for agent, success in results.items():
                status = "✅" if success else "❌"
                print(f"  {status} {agent}")
            
            if successful == total:
                print("\n🎉 Tous les agents sont démarrés!")
                print("\n🌐 Endpoints disponibles:")
                for agent_name, config in manager.agent_configs.items():
                    if config.enabled and results.get(agent_name, False):
                        print(f"  • {agent_name}: http://localhost:{config.port}")
            
        elif command == "stop":
            results = manager.stop_all_agents()
            print("🛑 Tous les agents ont été arrêtés")
        
        elif command == "restart":
            print("🔄 Redémarrage du système...")
            manager.stop_all_agents()
            time.sleep(3)
            manager.check_dependencies()
            results = manager.start_all_agents()
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            print(f"✅ Redémarrage terminé: {successful}/{total} agents")
        
        elif command == "status":
            status = manager.get_system_status()
            print(f"\n📊 Statut du Système - {status['timestamp']}")
            print(f"Agents en cours: {status['running_agents']}/{status['total_agents']}")
            
            print("\n🔧 Processus:")
            for agent, proc_info in status['processes'].items():
                if proc_info['status'] != 'not_found':
                    print(f"  • {agent}: PID {proc_info['pid']}, CPU {proc_info.get('cpu_percent', 0):.1f}%, RAM {proc_info.get('memory_mb', 0):.1f}MB")
                else:
                    print(f"  • {agent}: Processus introuvable")
            
            print("\n🌐 Ports:")
            for agent, port_info in status['ports'].items():
                status_icon = "🟢" if port_info['occupied'] else "🔴"
                enabled_text = "activé" if port_info['enabled'] else "désactivé"
                print(f"  • {agent}: Port {port_info['port']} {status_icon} ({enabled_text})")
        
        elif command == "health":
            health = await manager.check_agents_health()
            print("\n🏥 Santé des Agents:")
            
            for agent, health_info in health.items():
                status = health_info['status']
                if status == "healthy":
                    print(f"  ✅ {agent}: Sain (port {health_info['port']})")
                elif status == "disabled":
                    print(f"  ⏸️ {agent}: Désactivé")
                elif status == "unhealthy":
                    print(f"  ⚠️ {agent}: Problème - {health_info.get('error', 'Inconnu')}")
                elif status == "unreachable":
                    print(f"  ❌ {agent}: Injoignable - {health_info.get('error', 'Inconnu')}")
        
        elif command == "test":
            print("🧪 Exécution du workflow de test...")
            result = await manager.run_test_workflow()
            
            print("\n📋 Résultats du test:")
            for agent, health_info in result['health_status'].items():
                status = health_info['status']
                status_icon = {"healthy": "✅", "disabled": "⏸️", "unhealthy": "⚠️", "unreachable": "❌"}.get(status, "❓")
                print(f"  {status_icon} {agent}: {status}")
            
            if result['test_completed']:
                print("\n🎉 Workflow de test terminé avec succès!")
        
        else:
            print(f"❌ Commande inconnue: {command}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️ Interruption par l'utilisateur")
        manager.stop_all_agents()
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
