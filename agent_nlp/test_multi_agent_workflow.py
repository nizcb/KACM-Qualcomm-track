"""
Test Workflow - Multi-Agent System Integration
=============================================

Script de test pour valider l'intégration complète du système multi-agents.
Tests d'orchestration, communication MCP, et workflow end-to-end.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import tempfile
import shutil

# Imports des agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_orchestrator_mcp import AgentOrchestrator
from agent_nlp_mcp import NLPAgent, NLPConfig
from agent_vision_mcp import VisionAgent, VisionConfig
from agent_audio_mcp import AudioAgent, AudioConfig
from agent_file_manager_mcp import FileManagerAgent, FileManagerConfig
from agent_security_mcp import SecurityAgent, SecurityConfig

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiAgentTestSuite:
    """Suite de tests pour le système multi-agents"""
    
    def __init__(self):
        self.test_dir = None
        self.orchestrator = None
        self.agents = {}
        self.results = []
        
    def setup_test_environment(self):
        """Prépare l'environnement de test"""
        print("🔧 Préparation de l'environnement de test...")
        
        # Créer un répertoire de test temporaire
        self.test_dir = tempfile.mkdtemp(prefix="multi_agent_test_")
        print(f"📁 Répertoire de test: {self.test_dir}")
        
        # Créer des fichiers de test
        self.create_test_files()
        
        # Initialiser les agents
        self.initialize_agents()
        
        print("✅ Environnement de test prêt")
    
    def create_test_files(self):
        """Crée des fichiers de test pour chaque type d'agent"""
        test_files = {
            # Fichiers texte pour l'agent NLP
            "document.txt": "Ceci est un document de test avec des informations normales.",
            "sensitive.txt": "Document contenant john.doe@example.com et +33 1 23 45 67 89",
            "report.json": '{"title": "Rapport", "content": "Données de test"}',
            
            # Fichiers image pour l'agent Vision (simulations)
            "image.jpg": "FAKE_IMAGE_DATA",
            "photo.png": "FAKE_PHOTO_DATA",
            
            # Fichiers audio pour l'agent Audio (simulations)  
            "audio.mp3": "FAKE_AUDIO_DATA",
            "voice.wav": "FAKE_VOICE_DATA"
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"📝 {len(test_files)} fichiers de test créés")
    
    def initialize_agents(self):
        """Initialise tous les agents du système"""
        print("🤖 Initialisation des agents...")
        
        # Orchestrator
        self.orchestrator = AgentOrchestrator()
        
        # Agents spécialisés
        self.agents = {
            'nlp': NLPAgent(NLPConfig()),
            'vision': VisionAgent(VisionConfig()),
            'audio': AudioAgent(AudioConfig()),
            'file_manager': FileManagerAgent(FileManagerConfig()),
            'security': SecurityAgent(SecurityConfig())
        }
        
        print(f"✅ {len(self.agents) + 1} agents initialisés")
    
    async def test_orchestrator_scan(self):
        """Test de scan de répertoire par l'orchestrateur"""
        print("\n🔍 Test 1: Scan de répertoire")
        
        try:
            # Utiliser la méthode scan_directory de l'orchestrateur
            scan_result = await self.orchestrator.scan_directory(self.test_dir)
            
            print(f"✅ Scan terminé:")
            print(f"  - Fichiers trouvés: {len(scan_result.files)}")
            print(f"  - Fichiers texte: {len([f for f in scan_result.files if f.file_type == 'text'])}")
            print(f"  - Fichiers image: {len([f for f in scan_result.files if f.file_type == 'image'])}")
            print(f"  - Fichiers audio: {len([f for f in scan_result.files if f.file_type == 'audio'])}")
            
            self.results.append({
                "test": "orchestrator_scan",
                "status": "success",
                "details": scan_result.dict() if hasattr(scan_result, 'dict') else str(scan_result)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du scan: {e}")
            self.results.append({
                "test": "orchestrator_scan",
                "status": "error",
                "error": str(e)
            })
            return False
    
    async def test_individual_agents(self):
        """Test des agents individuels"""
        print("\n🧪 Test 2: Agents individuels")
        
        # Test fichiers par type
        test_cases = [
            ("document.txt", "nlp"),
            ("sensitive.txt", "nlp"),
            ("image.jpg", "vision"),
            ("audio.mp3", "audio")
        ]
        
        for filename, agent_type in test_cases:
            file_path = os.path.join(self.test_dir, filename)
            
            try:
                agent = self.agents[agent_type]
                
                # Simuler l'analyse selon le type d'agent
                if agent_type == "nlp":
                    result = await agent.analyze_file(file_path)
                elif agent_type == "vision":
                    result = await agent.analyze_image(file_path)
                elif agent_type == "audio":
                    result = await agent.analyze_audio(file_path)
                
                print(f"✅ {agent_type.upper()} - {filename}: {result.get('summary', 'OK')[:50]}...")
                
                self.results.append({
                    "test": f"agent_{agent_type}_{filename}",
                    "status": "success",
                    "agent": agent_type,
                    "file": filename,
                    "result": result
                })
                
            except Exception as e:
                print(f"❌ {agent_type.upper()} - {filename}: {e}")
                self.results.append({
                    "test": f"agent_{agent_type}_{filename}",
                    "status": "error",
                    "agent": agent_type,
                    "file": filename,
                    "error": str(e)
                })
    
    async def test_end_to_end_workflow(self):
        """Test du workflow complet end-to-end"""
        print("\n🔄 Test 3: Workflow end-to-end")
        
        try:
            # Traitement complet par l'orchestrateur
            workflow_result = await self.orchestrator.process_directory(self.test_dir)
            
            print(f"✅ Workflow terminé:")
            print(f"  - Fichiers traités: {len(workflow_result.get('processed_files', []))}")
            print(f"  - Avertissements: {len(workflow_result.get('warnings', []))}")
            print(f"  - Actions de sécurité: {len(workflow_result.get('security_actions', []))}")
            
            # Test File Manager
            file_manager = self.agents['file_manager']
            consolidation_result = await file_manager.consolidate_results(workflow_result)
            
            print(f"✅ File Manager - Consolidation terminée")
            
            # Test Security Agent si des avertissements
            if workflow_result.get('warnings'):
                security_agent = self.agents['security']
                security_result = await security_agent.secure_files(workflow_result.get('warnings'))
                print(f"✅ Security Agent - {len(security_result)} actions de sécurité")
            
            self.results.append({
                "test": "end_to_end_workflow",
                "status": "success",
                "workflow_result": workflow_result,
                "consolidation": consolidation_result
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur workflow end-to-end: {e}")
            self.results.append({
                "test": "end_to_end_workflow",
                "status": "error",
                "error": str(e)
            })
            return False
    
    async def test_mcp_communication(self):
        """Test de communication MCP entre agents"""
        print("\n🌐 Test 4: Communication MCP")
        
        try:
            # Simuler des appels MCP entre agents
            print("  📡 Test communication orchestrateur → agents")
            
            # Test des endpoints MCP (simulation)
            endpoints_tested = []
            
            for agent_name, agent in self.agents.items():
                try:
                    # Simuler un appel MCP
                    if hasattr(agent, 'get_agent_status'):
                        status = agent.get_agent_status()
                        endpoints_tested.append({
                            "agent": agent_name,
                            "status": "available",
                            "info": status
                        })
                        print(f"  ✅ {agent_name}: MCP disponible")
                    else:
                        endpoints_tested.append({
                            "agent": agent_name,
                            "status": "no_mcp_method",
                            "info": "Agent sans méthode MCP standard"
                        })
                        print(f"  ⚠️ {agent_name}: Pas de méthode MCP standard")
                        
                except Exception as e:
                    endpoints_tested.append({
                        "agent": agent_name,
                        "status": "error",
                        "error": str(e)
                    })
                    print(f"  ❌ {agent_name}: Erreur MCP - {e}")
            
            self.results.append({
                "test": "mcp_communication",
                "status": "success",
                "endpoints": endpoints_tested
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur communication MCP: {e}")
            self.results.append({
                "test": "mcp_communication",
                "status": "error",
                "error": str(e)
            })
            return False
    
    def generate_test_report(self):
        """Génère un rapport de test complet"""
        print("\n📊 Génération du rapport de test")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            "test_session": {
                "timestamp": timestamp,
                "test_directory": self.test_dir,
                "total_tests": len(self.results)
            },
            "summary": {
                "passed": len([r for r in self.results if r.get("status") == "success"]),
                "failed": len([r for r in self.results if r.get("status") == "error"]),
                "success_rate": 0
            },
            "detailed_results": self.results
        }
        
        report["summary"]["success_rate"] = report["summary"]["passed"] / report["summary"]["total_tests"] * 100
        
        # Sauvegarder le rapport
        report_path = f"test_report_{timestamp}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Rapport sauvegardé: {report_path}")
        
        # Afficher le résumé
        print(f"\n🎯 Résumé des tests:")
        print(f"  - Tests réussis: {report['summary']['passed']}")
        print(f"  - Tests échoués: {report['summary']['failed']}")
        print(f"  - Taux de réussite: {report['summary']['success_rate']:.1f}%")
        
        return report
    
    def cleanup(self):
        """Nettoie l'environnement de test"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🧹 Nettoyage: {self.test_dir} supprimé")
    
    async def run_all_tests(self):
        """Exécute tous les tests"""
        print("🚀 Démarrage de la suite de tests multi-agents")
        print("="*60)
        
        try:
            # Préparation
            self.setup_test_environment()
            
            # Exécution des tests
            await self.test_orchestrator_scan()
            await self.test_individual_agents()
            await self.test_end_to_end_workflow()
            await self.test_mcp_communication()
            
            # Rapport final
            report = self.generate_test_report()
            
            return report
            
        except Exception as e:
            print(f"❌ Erreur critique durant les tests: {e}")
            return None
        finally:
            self.cleanup()

async def main():
    """Point d'entrée principal"""
    print("🧪 Multi-Agent System Test Suite")
    print("Validation complète du système multi-agents MCP")
    print("="*60)
    
    # Exécuter la suite de tests
    test_suite = MultiAgentTestSuite()
    report = await test_suite.run_all_tests()
    
    if report:
        if report["summary"]["success_rate"] >= 80:
            print("\n🎉 Tests globalement réussis!")
        else:
            print("\n⚠️ Des améliorations sont nécessaires.")
    else:
        print("\n❌ Échec critique des tests.")
    
    print("\n👋 Fin des tests")

if __name__ == "__main__":
    asyncio.run(main())
