"""
Agent Orchestrator MCP - Coordinateur principal du système
==========================================================

Agent principal qui :
- Scanne un répertoire et identifie tous les files
- Distribue les files aux agents spécialisés selon leur type :
  * Texte (.txt, .pdf, .md, .json, .csv) → Agent NLP
  * Images (.jpg, .jpeg, .png, .gif, .bmp) → Agent Vision
  * Audio (.mp3, .wav, .m4a, .ogg) → Agent Audio
- Collecte tous les résultats via l'Agent File Manager
- Coordonne la sécurisation via l'Agent Security

Communication Agent-to-Agent via MCP Server.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import mimetypes

# Imports MCP officiels
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
from mcp.types import TextContent
from pydantic import BaseModel, Field

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/orchestrator.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────
# Modèles de données pour la communication inter-agents
# ──────────────────────────────────────────────────────────────────────────

class FileInfo(BaseModel):
    """Information sur un fichier à traiter"""
    file_path: str
    file_type: str  # 'text', 'image', 'audio'
    mime_type: str
    size: int
    extension: str

class AgentTask(BaseModel):
    """Tâche assignée à un agent spécialisé"""
    agent_type: str  # 'nlp', 'vision', 'audio'
    files: List[FileInfo]
    task_id: str
    priority: int = 1

class ProcessingResult(BaseModel):
    """Résultat standardisé de traitement (format unifié)"""
    file_path: str
    summary: str
    warning: bool
    agent_type: str
    processing_time: float
    metadata: Dict[str, Any] = {}

class OrchestrationReport(BaseModel):
    """Rapport complet d'orchestration"""
    session_id: str
    start_time: str
    end_time: str
    directory_scanned: str
    total_files: int
    files_by_type: Dict[str, int]
    results: List[ProcessingResult]
    files_with_warnings: List[str]
    security_actions: List[Dict[str, Any]] = []

# ──────────────────────────────────────────────────────────────────────────
# Classe principale de l'Orchestrator
# ──────────────────────────────────────────────────────────────────────────

class AgentOrchestrator:
    """Agent Orchestrator - Coordinateur principal du système multi-agents"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.supported_extensions = {
            # Fichiers texte → Agent NLP
            'text': ['.txt', '.pdf', '.md', '.json', '.csv', '.xml', '.html', '.log', '.py', '.js', '.css'],
            # Fichiers image → Agent Vision  
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'],
            # Fichiers audio → Agent Audio
            'audio': ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.mp4']
        }
        
        # Endpoints des agents spécialisés (communication MCP)
        self.agent_endpoints = {
            'nlp': 'http://localhost:8001',
            'vision': 'http://localhost:8002', 
            'audio': 'http://localhost:8003',
            'file_manager': 'http://localhost:8004',
            'security': 'http://localhost:8005'
        }
        
        # Statistiques de session
        self.stats = {
            'files_scanned': 0,
            'files_processed': 0,
            'files_with_warnings': 0,
            'processing_errors': 0
        }
        
        logger.info(f"🎯 Agent Orchestrator initialisé - Session: {self.session_id}")
    
    def classify_file(self, file_path: str) -> Optional[FileInfo]:
        """
        Classifie un fichier selon son type et détermine l'agent approprié
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            FileInfo si le fichier est supporté, None sinon
        """
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
        """
        Scanne un répertoire et classifie tous les files par type
        
        Args:
            directory_path: Répertoire à scanner
            recursive: Scan récursif des sous-dossiers
            
        Returns:
            Dictionnaire des files classés par type d'agent
        """
        logger.info(f"🔍 Scan du répertoire: {directory_path} (récursif: {recursive})")
        
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Répertoire non trouvé: {directory_path}")
        
        files_by_agent = {'nlp': [], 'vision': [], 'audio': []}
        
        # Pattern de recherche
        pattern = "**/*" if recursive else "*"
        
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
        logger.info(f"   • {self.stats['files_scanned']} files scannés")
        logger.info(f"   • {total_classified} files classifiés")
        logger.info(f"   • NLP: {len(files_by_agent['nlp'])} files")
        logger.info(f"   • Vision: {len(files_by_agent['vision'])} files") 
        logger.info(f"   • Audio: {len(files_by_agent['audio'])} files")
        
        return files_by_agent
    
    async def dispatch_to_agent(self, agent_type: str, files: List[FileInfo]) -> List[ProcessingResult]:
        """
        Envoie les files à l'agent spécialisé correspondant
        
        Args:
            agent_type: Type d'agent ('nlp', 'vision', 'audio')
            files: Liste des files à traiter
            
        Returns:
            Liste des résultats de traitement
        """
        if not files:
            return []
        
        logger.info(f"📤 Dispatch vers Agent {agent_type.upper()}: {len(files)} files")
        
        results = []
        
        # Import dynamique de l'agent approprié selon le type
        try:
            if agent_type == 'nlp':
                # Utiliser l'agent NLP existant
                from agent_nlp_mcp import process_file_with_ai
                
                for file_info in files:
                    try:
                        start_time = datetime.now()
                        
                        # Appel de l'agent NLP (format attendu: dict avec file_path, summary, warning)
                        result_dict = await process_file_with_ai(file_info.file_path)
                        
                        processing_time = (datetime.now() - start_time).total_seconds()
                        
                        result = ProcessingResult(
                            file_path=result_dict.get('file_path', file_info.file_path),
                            summary=result_dict.get('summary', 'Traité par Agent NLP'),
                            warning=result_dict.get('warning', False),
                            agent_type='nlp',
                            processing_time=processing_time,
                            metadata={'file_size': file_info.size, 'mime_type': file_info.mime_type}
                        )
                        
                        results.append(result)
                        self.stats['files_processed'] += 1
                        
                        if result.warning:
                            self.stats['files_with_warnings'] += 1
                        
                        logger.info(f"✅ NLP: {Path(file_info.file_path).name} - Warning: {result.warning}")
                        
                    except Exception as e:
                        logger.error(f"❌ Erreur Agent NLP pour {file_info.file_path}: {e}")
                        self.stats['processing_errors'] += 1
            
            elif agent_type == 'vision':
                # Utiliser l'agent Vision (à adapter)
                from agent_vision_mcp import analyze_document, VisionArgs
                
                for file_info in files:
                    try:
                        start_time = datetime.now()
                        
                        # Appel de l'agent Vision
                        args = VisionArgs(path=file_info.file_path)
                        vision_result = await analyze_document(args)
                        
                        processing_time = (datetime.now() - start_time).total_seconds()
                        
                        result = ProcessingResult(
                            file_path=vision_result.filepath,
                            summary=vision_result.summary,
                            warning=vision_result.warning,
                            agent_type='vision',
                            processing_time=processing_time,
                            metadata={'file_size': file_info.size, 'mime_type': file_info.mime_type}
                        )
                        
                        results.append(result)
                        self.stats['files_processed'] += 1
                        
                        if result.warning:
                            self.stats['files_with_warnings'] += 1
                        
                        logger.info(f"✅ Vision: {Path(file_info.file_path).name} - Warning: {result.warning}")
                        
                    except Exception as e:
                        logger.error(f"❌ Erreur Agent Vision pour {file_info.file_path}: {e}")
                        self.stats['processing_errors'] += 1
            
            elif agent_type == 'audio':
                # Utiliser l'agent Audio (à créer)
                from agent_audio_mcp import analyze_audio, AudioArgs
                
                for file_info in files:
                    try:
                        start_time = datetime.now()
                        
                        # Appel de l'agent Audio
                        args = AudioArgs(path=file_info.file_path)
                        audio_result = await analyze_audio(args)
                        
                        processing_time = (datetime.now() - start_time).total_seconds()
                        
                        result = ProcessingResult(
                            file_path=audio_result.filepath,
                            summary=audio_result.summary,
                            warning=audio_result.warning,
                            agent_type='audio',
                            processing_time=processing_time,
                            metadata={'file_size': file_info.size, 'mime_type': file_info.mime_type}
                        )
                        
                        results.append(result)
                        self.stats['files_processed'] += 1
                        
                        if result.warning:
                            self.stats['files_with_warnings'] += 1
                        
                        logger.info(f"✅ Audio: {Path(file_info.file_path).name} - Warning: {result.warning}")
                        
                    except Exception as e:
                        logger.error(f"❌ Erreur Agent Audio pour {file_info.file_path}: {e}")
                        self.stats['processing_errors'] += 1
            
        except ImportError as e:
            logger.error(f"❌ Impossible d'importer l'agent {agent_type}: {e}")
            self.stats['processing_errors'] += len(files)
        
        logger.info(f"📥 Agent {agent_type.upper()} terminé: {len(results)} résultats")
        return results
    
    async def send_to_file_manager(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """
        Envoie tous les résultats à l'Agent File Manager pour consolidation
        
        Args:
            results: Liste de tous les résultats de traitement
            
        Returns:
            Rapport consolidé du File Manager
        """
        logger.info(f"📋 Envoi vers File Manager: {len(results)} résultats")
        
        try:
            # Import de l'agent File Manager
            from agent_file_manager_mcp import consolidate_results
            
            # Préparer les données pour le File Manager
            manager_input = {
                'session_id': self.session_id,
                'results': [result.dict() for result in results],
                'stats': self.stats
            }
            
            # Appel du File Manager
            consolidated_report = await consolidate_results(manager_input)
            
            logger.info("✅ File Manager: Consolidation terminée")
            return consolidated_report
            
        except ImportError as e:
            logger.error(f"❌ Agent File Manager non disponible: {e}")
            return {'error': f'File Manager non disponible: {e}'}
        except Exception as e:
            logger.error(f"❌ Erreur File Manager: {e}")
            return {'error': f'Erreur File Manager: {e}'}
    
    async def send_to_security(self, warning_files: List[ProcessingResult]) -> List[Dict[str, Any]]:
        """
        Envoie les files avec warnings à l'Agent Security pour sécurisation
        
        Args:
            warning_files: Liste des résultats avec warning=True
            
        Returns:
            Liste des actions de sécurisation effectuées
        """
        if not warning_files:
            logger.info("🔒 Aucun fichier nécessitant une sécurisation")
            return []
        
        logger.info(f"🔒 Envoi vers Security Agent: {len(warning_files)} files sensibles")
        
        try:
            # Import de l'agent Security
            from agent_security_mcp import secure_files
            
            # Préparer les données pour l'agent Security
            security_input = {
                'session_id': self.session_id,
                'sensitive_files': [result.dict() for result in warning_files]
            }
            
            # Appel de l'agent Security
            security_actions = await secure_files(security_input)
            
            logger.info(f"✅ Security Agent: {len(security_actions)} actions effectuées")
            return security_actions
            
        except ImportError as e:
            logger.error(f"❌ Agent Security non disponible: {e}")
            return [{'error': f'Security Agent non disponible: {e}'}]
        except Exception as e:
            logger.error(f"❌ Erreur Security Agent: {e}")
            return [{'error': f'Erreur Security Agent: {e}'}]
    
    async def orchestrate_directory(self, directory_path: str, recursive: bool = True) -> OrchestrationReport:
        """
        Orchestration complète d'un répertoire
        
        Args:
            directory_path: Répertoire à traiter
            recursive: Scan récursif
            
        Returns:
            Rapport complet d'orchestration
        """
        start_time = datetime.now()
        logger.info(f"🎯 === DÉBUT ORCHESTRATION ===")
        logger.info(f"📁 Répertoire: {directory_path}")
        logger.info(f"🔄 Session: {self.session_id}")
        
        try:
            # 1. Scanner et classifier les files
            files_by_agent = self.scan_directory(directory_path, recursive)
            
            # 2. Traitement en parallèle par les agents spécialisés
            all_results = []
            
            # Dispatching en parallèle vers les 3 agents
            tasks = []
            for agent_type, files in files_by_agent.items():
                if files:  # Seulement si des files sont présents
                    task = self.dispatch_to_agent(agent_type, files)
                    tasks.append(task)
            
            # Attendre tous les agents en parallèle
            if tasks:
                results_lists = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result_list in results_lists:
                    if isinstance(result_list, list):
                        all_results.extend(result_list)
                    else:
                        logger.error(f"❌ Erreur dans un agent: {result_list}")
            
            # 3. Envoyer à l'Agent File Manager
            file_manager_report = await self.send_to_file_manager(all_results)
            
            # 4. Identifier les files avec warning et les sécuriser
            warning_files = [r for r in all_results if r.warning]
            security_actions = await self.send_to_security(warning_files)
            
            # 5. Générer le rapport final
            end_time = datetime.now()
            
            # Compter les files par type
            files_by_type = {}
            for agent_type, files in files_by_agent.items():
                files_by_type[agent_type] = len(files)
            
            report = OrchestrationReport(
                session_id=self.session_id,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                directory_scanned=directory_path,
                total_files=self.stats['files_scanned'],
                files_by_type=files_by_type,
                results=all_results,
                files_with_warnings=[r.file_path for r in warning_files],
                security_actions=security_actions
            )
            
            # Sauvegarder le rapport
            self.save_orchestration_report(report)
            
            # Log final
            duration = (end_time - start_time).total_seconds()
            logger.info(f"🎯 === ORCHESTRATION TERMINÉE ===")
            logger.info(f"⏱️ Durée: {duration:.2f}s")
            logger.info(f"📁 Fichiers traités: {self.stats['files_processed']}/{self.stats['files_scanned']}")
            logger.info(f"⚠️ Fichiers sensibles: {self.stats['files_with_warnings']}")
            logger.info(f"❌ Erreurs: {self.stats['processing_errors']}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur critique d'orchestration: {e}")
            end_time = datetime.now()
            
            # Rapport d'erreur
            error_report = OrchestrationReport(
                session_id=self.session_id,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                directory_scanned=directory_path,
                total_files=0,
                files_by_type={},
                results=[],
                files_with_warnings=[],
                security_actions=[{'error': str(e)}]
            )
            
            return error_report
    
    def save_orchestration_report(self, report: OrchestrationReport):
        """Sauvegarde le rapport d'orchestration"""
        try:
            os.makedirs("results", exist_ok=True)
            
            filename = f"orchestration_report_{self.session_id}.json"
            filepath = os.path.join("results", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report.dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Rapport sauvegardé: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde rapport: {e}")

# ──────────────────────────────────────────────────────────────────────────
# FastMCP Server pour l'exposition des outils
# ──────────────────────────────────────────────────────────────────────────

# Instance globale de l'orchestrator
orchestrator = AgentOrchestrator()

# Serveur MCP
mcp = FastMCP("Agent Orchestrator")

@mcp.tool()
async def orchestrate_directory(directory_path: str, recursive: bool = True) -> dict:
    """
    Orchestre le traitement complet d'un répertoire via le système multi-agents
    
    Args:
        directory_path: Chemin du répertoire à traiter
        recursive: Scanner récursivement les sous-dossiers
        
    Returns:
        Rapport complet d'orchestration avec tous les résultats
    """
    try:
        report = await orchestrator.orchestrate_directory(directory_path, recursive)
        return report.dict()
    except Exception as e:
        logger.error(f"❌ Erreur tool orchestrate_directory: {e}")
        return {'error': str(e)}

@mcp.tool()
async def get_supported_extensions() -> dict:
    """
    Retourne la liste des extensions supportées par chaque agent
    
    Returns:
        Dictionnaire des extensions supportées par agent
    """
    return orchestrator.supported_extensions

@mcp.tool()
async def get_session_stats() -> dict:
    """
    Retourne les statistiques de la session courante
    
    Returns:
        Statistiques de traitement
    """
    return {
        'session_id': orchestrator.session_id,
        'stats': orchestrator.stats,
        'agent_endpoints': orchestrator.agent_endpoints
    }

# ──────────────────────────────────────────────────────────────────────────
# Interface CLI principale
# ──────────────────────────────────────────────────────────────────────────

async def main():
    """Interface en ligne de commande principale"""
    import sys
    
    if len(sys.argv) < 2:
        print("Agent Orchestrator - Système Multi-Agents MCP")
        print("=" * 50)
        print("\nUsage:")
        print("  python agent_orchestrator_mcp.py <directory>                # Traite un répertoire")
        print("  python agent_orchestrator_mcp.py <directory> --no-recursive # Scan non-récursif") 
        print("\nExemples:")
        print("  python agent_orchestrator_mcp.py ./documents")
        print("  python agent_orchestrator_mcp.py ./test_files --no-recursive")
        print("\nLe système dispatche automatiquement:")
        print("  📝 Fichiers texte (.txt, .pdf, .md...) → Agent NLP")
        print("  🖼️ Fichiers image (.jpg, .png...) → Agent Vision")
        print("  🎵 Fichiers audio (.mp3, .wav...) → Agent Audio")
        print("  📋 Consolidation → Agent File Manager")
        print("  🔒 Sécurisation → Agent Security")
        return
    
    directory = sys.argv[1]
    recursive = "--no-recursive" not in sys.argv
    
    print(f"\n🎯 Agent Orchestrator - Traitement Multi-Agents")
    print(f"📁 Répertoire: {directory}")
    print(f"🔄 Récursif: {recursive}")
    print("=" * 60)
    
    # Créer et lancer l'orchestration
    orchestrator_instance = AgentOrchestrator()
    report = await orchestrator_instance.orchestrate_directory(directory, recursive)
    
    # Afficher le résumé
    print(f"\n📊 === RÉSUMÉ FINAL ===")
    print(f"📁 Fichiers scannés: {report.total_files}")
    print(f"📝 NLP: {report.files_by_type.get('nlp', 0)} files")
    print(f"🖼️ Vision: {report.files_by_type.get('vision', 0)} files")
    print(f"🎵 Audio: {report.files_by_type.get('audio', 0)} files")
    print(f"⚠️ Fichiers sensibles: {len(report.files_with_warnings)}")
    print(f"🔒 Actions sécurité: {len(report.security_actions)}")
    
    if report.files_with_warnings:
        print(f"\n⚠️ Fichiers nécessitant attention:")
        for warning_file in report.files_with_warnings[:5]:  # Top 5
            print(f"   • {Path(warning_file).name}")
        if len(report.files_with_warnings) > 5:
            print(f"   • ... et {len(report.files_with_warnings) - 5} autres")
    
    print(f"\n💾 Rapport complet: results/orchestration_report_{report.session_id}.json")

if __name__ == "__main__":
    asyncio.run(main())
