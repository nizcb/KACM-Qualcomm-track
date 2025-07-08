"""
🎯 Agent Orchestrateur MCP Réel
===============================

Orchestrateur principal qui coordonne tous les agents du système multi-agents.
Utilise vraiment le protocole MCP pour la communication inter-agents.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import mimetypes
import httpx
from dataclasses import dataclass

# Ajout du répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from mcp.server.fastmcp import FastMCP
    from pydantic import BaseModel
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP non disponible, mode dégradé")
    MCP_AVAILABLE = False

from config import Config

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOGS_DIR / "orchestrator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """Information sur un fichier à traiter"""
    file_path: str
    file_type: str
    mime_type: str
    size: int
    extension: str

@dataclass
class ProcessingResult:
    """Résultat du traitement d'un fichier"""
    file_path: str
    summary: str
    warning: bool
    agent_type: str
    processing_time: float
    metadata: Optional[Dict[str, Any]] = None
    pii_detected: Optional[List[Dict[str, Any]]] = None

class OrchestrationReport(BaseModel):
    """Rapport d'orchestration complet"""
    session_id: str
    directory_scanned: str
    total_files: int
    processed_files: int
    files_with_warnings: int
    processing_errors: int
    processing_time: float
    results: List[Dict[str, Any]]
    files_by_type: Dict[str, int]
    agent_stats: Dict[str, int]

class RealMCPOrchestrator:
    """Orchestrateur MCP réel pour coordonner les agents"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.supported_extensions = {
            'text': Config.TEXT_EXTENSIONS,
            'image': Config.IMAGE_EXTENSIONS,
            'audio': Config.AUDIO_EXTENSIONS
        }
        
        # Endpoints des agents spécialisés (communication MCP réelle)
        self.agent_endpoints = {
            'nlp': Config.get_agent_endpoint('nlp'),
            'vision': Config.get_agent_endpoint('vision'),
            'audio': Config.get_agent_endpoint('audio'),
            'file_manager': Config.get_agent_endpoint('file_manager'),
            'security': Config.get_agent_endpoint('security')
        }
        
        # Statistiques de session
        self.stats = {
            'files_scanned': 0,
            'files_processed': 0,
            'files_with_warnings': 0,
            'processing_errors': 0
        }
        
        logger.info(f"🎯 Agent Orchestrateur MCP RÉEL initialisé - Session: {self.session_id}")
    
    def classify_file(self, file_path: str) -> Optional[FileInfo]:
        """Classifier un fichier selon son type"""
        try:
            path_obj = Path(file_path)
            
            if not path_obj.exists() or not path_obj.is_file():
                return None
                
            extension = path_obj.suffix.lower()
            file_size = path_obj.stat().st_size
            
            # Déterminer le type de fichier
            file_type = None
            for category, extensions in self.supported_extensions.items():
                if extension in extensions:
                    file_type = category
                    break
            
            if file_type is None:
                logger.debug(f"⚠️ Type de fichier non supporté: {extension}")
                return None
            
            # Déterminer le MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = f"application/{file_type}"
            
            return FileInfo(
                file_path=str(path_obj.resolve()),
                file_type=file_type,
                mime_type=mime_type,
                size=file_size,
                extension=extension
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur classification fichier {file_path}: {e}")
            return None
    
    def scan_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, List[FileInfo]]:
        """Scanner un répertoire et classifier les fichiers"""
        logger.info(f"🔍 Scan du répertoire: {directory_path}")
        
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Répertoire non trouvé: {directory_path}")
        
        files_by_agent = {'nlp': [], 'vision': [], 'audio': []}
        
        # Pattern de recherche
        pattern = "**/*" if recursive else "*"
        
        # Scanner tous les fichiers
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                self.stats['files_scanned'] += 1
                
                file_info = self.classify_file(str(file_path))
                if file_info:
                    # Mapper le type de fichier vers l'agent approprié
                    agent_type = 'nlp' if file_info.file_type == 'text' else file_info.file_type
                    if agent_type == 'image':
                        agent_type = 'vision'
                    
                    files_by_agent[agent_type].append(file_info)
                    logger.debug(f"📁 {file_info.extension} → Agent {agent_type}: {file_path.name}")
        
        # Statistiques du scan
        total_classified = sum(len(files) for files in files_by_agent.values())
        logger.info(f"📊 Scan terminé:")
        logger.info(f"   • {self.stats['files_scanned']} fichiers scannés")
        logger.info(f"   • {total_classified} fichiers classifiés")
        logger.info(f"   • NLP: {len(files_by_agent['nlp'])} fichiers")
        logger.info(f"   • Vision: {len(files_by_agent['vision'])} fichiers")
        logger.info(f"   • Audio: {len(files_by_agent['audio'])} fichiers")
        
        return files_by_agent
    
    async def call_agent_mcp(self, agent_type: str, endpoint: str, file_info: FileInfo) -> Optional[ProcessingResult]:
        """Appel MCP réel vers un agent spécialisé"""
        try:
            async with httpx.AsyncClient(timeout=Config.AGENT_RESPONSE_TIMEOUT) as client:
                start_time = datetime.now()
                
                # Appel MCP standardisé
                payload = {
                    "file_path": file_info.file_path,
                    "file_type": file_info.file_type,
                    "mime_type": file_info.mime_type,
                    "size": file_info.size
                }
                
                response = await client.post(
                    f"{endpoint}/analyze_file",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    return ProcessingResult(
                        file_path=result_data.get('file_path', file_info.file_path),
                        summary=result_data.get('summary', 'Traité par agent MCP'),
                        warning=result_data.get('warning', False),
                        agent_type=agent_type,
                        processing_time=processing_time,
                        metadata=result_data.get('metadata', {}),
                        pii_detected=result_data.get('pii_detected', [])
                    )
                else:
                    logger.error(f"❌ Erreur HTTP {response.status_code} pour {agent_type}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"⏰ Timeout lors de l'appel à l'agent {agent_type}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'appel MCP à {agent_type}: {e}")
            return None
    
    async def dispatch_to_agents(self, files_by_agent: Dict[str, List[FileInfo]]) -> List[ProcessingResult]:
        """Dispatcher les fichiers vers les agents appropriés en parallèle"""
        all_results = []
        tasks = []
        
        # Créer les tâches pour chaque agent
        for agent_type, files in files_by_agent.items():
            if files and agent_type in self.agent_endpoints:
                endpoint = self.agent_endpoints[agent_type]
                logger.info(f"📋 Agent {agent_type}: {len(files)} fichier(s) → {endpoint}")
                
                for file_info in files:
                    task = self.call_agent_mcp(agent_type, endpoint, file_info)
                    tasks.append(task)
        
        # Exécuter toutes les tâches en parallèle
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, ProcessingResult):
                    all_results.append(result)
                    self.stats['files_processed'] += 1
                    
                    if result.warning:
                        self.stats['files_with_warnings'] += 1
                        
                    logger.info(f"✅ {result.agent_type.upper()}: {Path(result.file_path).name} - Warning: {result.warning}")
                    
                elif isinstance(result, Exception):
                    logger.error(f"❌ Erreur dans un agent: {result}")
                    self.stats['processing_errors'] += 1
                else:
                    self.stats['processing_errors'] += 1
        
        return all_results
    
    async def send_to_file_manager(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """Envoyer les résultats au File Manager pour consolidation"""
        try:
            if 'file_manager' not in self.agent_endpoints:
                logger.warning("⚠️ Agent File Manager non configuré")
                return {'status': 'skipped', 'reason': 'Agent non configuré'}
            
            async with httpx.AsyncClient(timeout=Config.AGENT_RESPONSE_TIMEOUT) as client:
                payload = {
                    "session_id": self.session_id,
                    "results": [
                        {
                            "file_path": r.file_path,
                            "summary": r.summary,
                            "warning": r.warning,
                            "agent_type": r.agent_type,
                            "processing_time": r.processing_time,
                            "metadata": r.metadata or {},
                            "pii_detected": r.pii_detected or []
                        }
                        for r in results
                    ]
                }
                
                response = await client.post(
                    f"{self.agent_endpoints['file_manager']}/consolidate_results",
                    json=payload
                )
                
                if response.status_code == 200:
                    logger.info("✅ File Manager: Résultats consolidés")
                    return response.json()
                else:
                    logger.error(f"❌ File Manager erreur HTTP {response.status_code}")
                    return {'status': 'error', 'code': response.status_code}
                    
        except Exception as e:
            logger.error(f"❌ Erreur File Manager: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def send_to_security(self, warning_results: List[ProcessingResult]) -> List[Dict[str, Any]]:
        """Envoyer les fichiers avec warnings au Security Agent"""
        if not warning_results:
            return []
        
        try:
            if 'security' not in self.agent_endpoints:
                logger.warning("⚠️ Agent Security non configuré")
                return []
            
            async with httpx.AsyncClient(timeout=Config.AGENT_RESPONSE_TIMEOUT) as client:
                payload = {
                    "session_id": self.session_id,
                    "sensitive_files": [
                        {
                            "file_path": r.file_path,
                            "warning_reason": r.summary,
                            "pii_detected": r.pii_detected or [],
                            "agent_type": r.agent_type
                        }
                        for r in warning_results
                    ]
                }
                
                response = await client.post(
                    f"{self.agent_endpoints['security']}/secure_files",
                    json=payload
                )
                
                if response.status_code == 200:
                    security_actions = response.json().get('actions', [])
                    logger.info(f"✅ Security Agent: {len(security_actions)} actions effectuées")
                    return security_actions
                else:
                    logger.error(f"❌ Security Agent erreur HTTP {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Erreur Security Agent: {e}")
            return []
    
    async def orchestrate_directory(self, directory_path: str, recursive: bool = True) -> OrchestrationReport:
        """Orchestrer l'analyse complète d'un répertoire avec les vrais agents MCP"""
        start_time = datetime.now()
        logger.info(f"🚀 Démarrage orchestration MCP RÉELLE: {directory_path}")
        
        try:
            # 1. Scanner et classifier les fichiers
            files_by_agent = self.scan_directory(directory_path, recursive)
            
            # 2. Dispatcher vers les agents spécialisés en parallèle
            all_results = await self.dispatch_to_agents(files_by_agent)
            
            # 3. Envoyer au File Manager pour consolidation
            file_manager_report = await self.send_to_file_manager(all_results)
            
            # 4. Traiter les fichiers avec warnings via Security Agent
            warning_results = [r for r in all_results if r.warning]
            security_actions = await self.send_to_security(warning_results)
            
            # 5. Générer le rapport final
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            agent_stats = {}
            for result in all_results:
                agent_stats[result.agent_type] = agent_stats.get(result.agent_type, 0) + 1
            
            report = OrchestrationReport(
                session_id=self.session_id,
                directory_scanned=directory_path,
                total_files=self.stats['files_scanned'],
                processed_files=self.stats['files_processed'],
                files_with_warnings=self.stats['files_with_warnings'],
                processing_errors=self.stats['processing_errors'],
                processing_time=processing_time,
                results=[
                    {
                        "file_path": r.file_path,
                        "summary": r.summary,
                        "warning": r.warning,
                        "agent_type": r.agent_type,
                        "processing_time": r.processing_time,
                        "pii_detected": r.pii_detected or []
                    }
                    for r in all_results
                ],
                files_by_type={
                    agent: len(files) for agent, files in files_by_agent.items()
                },
                agent_stats=agent_stats
            )
            
            # Sauvegarder le rapport
            self.save_report(report)
            
            logger.info(f"✅ Orchestration terminée en {processing_time:.2f}s")
            logger.info(f"📊 Résultats: {len(all_results)} fichiers traités, {len(warning_results)} warnings, {len(security_actions)} actions sécurité")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'orchestration: {e}")
            raise
    
    def save_report(self, report: OrchestrationReport):
        """Sauvegarder le rapport d'orchestration"""
        try:
            report_path = Config.LOGS_DIR / f"orchestration_report_{report.session_id}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report.dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"📄 Rapport sauvegardé: {report_path}")
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde rapport: {e}")

# ──────────────────────────────────────────────────────────────────────────
# Serveur MCP pour l'exposition des outils
# ──────────────────────────────────────────────────────────────────────────

# Instance globale de l'orchestrator
orchestrator = RealMCPOrchestrator()

if MCP_AVAILABLE:
    # Serveur MCP
    mcp = FastMCP("Agent Orchestrateur MCP Réel")

    @mcp.tool()
    async def orchestrate_directory(directory_path: str, recursive: bool = True) -> dict:
        """Orchestrer l'analyse complète d'un répertoire avec tous les agents MCP"""
        report = await orchestrator.orchestrate_directory(directory_path, recursive)
        return report.dict()

    @mcp.tool()
    async def get_supported_extensions() -> dict:
        """Obtenir les extensions de fichiers supportées"""
        return orchestrator.supported_extensions

    @mcp.tool()
    async def get_session_stats() -> dict:
        """Obtenir les statistiques de la session courante"""
        return {
            "session_id": orchestrator.session_id,
            "stats": orchestrator.stats,
            "agent_endpoints": orchestrator.agent_endpoints
        }

# ──────────────────────────────────────────────────────────────────────────
# Interface CLI principale
# ──────────────────────────────────────────────────────────────────────────

async def main():
    """Interface principale pour l'orchestrateur"""
    if len(sys.argv) < 2:
        print("Usage: python agent_orchestrator_mcp.py <directory_path>")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    
    if not Path(directory_path).exists():
        print(f"❌ Répertoire non trouvé: {directory_path}")
        sys.exit(1)
    
    try:
        # Démarrer l'orchestration
        report = await orchestrator.orchestrate_directory(directory_path)
        
        # Afficher les résultats
        print(f"\n📊 Rapport d'Orchestration - Session {report.session_id}")
        print(f"📁 Répertoire: {report.directory_scanned}")
        print(f"📈 Fichiers scannés: {report.total_files}")
        print(f"✅ Fichiers traités: {report.processed_files}")
        print(f"⚠️ Fichiers avec warnings: {report.files_with_warnings}")
        print(f"❌ Erreurs de traitement: {report.processing_errors}")
        print(f"⏱️ Temps de traitement: {report.processing_time:.2f}s")
        print(f"🤖 Agents utilisés: {', '.join(report.agent_stats.keys())}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Interruption par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        logger.error(f"Erreur main: {e}")

if __name__ == "__main__":
    if MCP_AVAILABLE:
        # Mode serveur MCP
        mcp.run()
    else:
        # Mode CLI direct
        asyncio.run(main())
