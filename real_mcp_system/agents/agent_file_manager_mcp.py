"""
📁 Agent File Manager MCP Réel
=============================

Agent de consolidation et gestion des résultats d'analyse.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import sqlite3
from dataclasses import dataclass

# Ajout du répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from mcp.server.fastmcp import FastMCP
    from pydantic import BaseModel
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP non disponible pour Agent File Manager")
    MCP_AVAILABLE = False

from config import Config

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOGS_DIR / "agent_file_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConsolidationReport(BaseModel):
    """Rapport de consolidation"""
    session_id: str
    total_files: int
    files_by_agent: Dict[str, int]
    files_with_warnings: int
    processing_summary: Dict[str, Any]
    recommendations: List[str]
    created_at: str

class RealFileManagerAgent:
    """Agent File Manager réel pour la consolidation des résultats"""
    
    def __init__(self):
        self.agent_name = "file_manager"
        self.db_path = Config.LOGS_DIR / "file_analysis.db"
        self.init_database()
        
        logger.info(f"📁 Agent File Manager MCP Réel initialisé")
    
    def init_database(self):
        """Initialiser la base de données SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des sessions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        created_at TEXT,
                        directory_path TEXT,
                        total_files INTEGER,
                        files_processed INTEGER,
                        files_with_warnings INTEGER,
                        processing_time REAL
                    )
                ''')
                
                # Table des résultats de fichiers
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS file_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        file_path TEXT,
                        agent_type TEXT,
                        summary TEXT,
                        warning BOOLEAN,
                        processing_time REAL,
                        metadata TEXT,
                        created_at TEXT,
                        FOREIGN KEY (session_id) REFERENCES sessions (id)
                    )
                ''')
                
                # Table des PII détectées
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pii_detections (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        file_path TEXT,
                        pii_type TEXT,
                        pii_value TEXT,
                        confidence REAL,
                        context TEXT,
                        created_at TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("✅ Base de données initialisée")
                
        except Exception as e:
            logger.error(f"❌ Erreur initialisation DB: {e}")
    
    def save_session(self, session_data: Dict[str, Any]):
        """Sauvegarder une session en base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO sessions 
                    (id, created_at, directory_path, total_files, files_processed, files_with_warnings, processing_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_data.get('session_id'),
                    datetime.now().isoformat(),
                    session_data.get('directory_path', ''),
                    session_data.get('total_files', 0),
                    session_data.get('files_processed', 0),
                    session_data.get('files_with_warnings', 0),
                    session_data.get('processing_time', 0.0)
                ))
                
                conn.commit()
                logger.info(f"✅ Session sauvegardée: {session_data.get('session_id')}")
                
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde session: {e}")
    
    def save_file_result(self, session_id: str, result: Dict[str, Any]):
        """Sauvegarder un résultat de fichier"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO file_results 
                    (session_id, file_path, agent_type, summary, warning, processing_time, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    result.get('file_path'),
                    result.get('agent_type'),
                    result.get('summary'),
                    result.get('warning', False),
                    result.get('processing_time', 0.0),
                    json.dumps(result.get('metadata', {})),
                    datetime.now().isoformat()
                ))
                
                # Sauvegarder les PII détectées
                pii_list = result.get('pii_detected', [])
                for pii in pii_list:
                    cursor.execute('''
                        INSERT INTO pii_detections 
                        (session_id, file_path, pii_type, pii_value, confidence, context, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session_id,
                        result.get('file_path'),
                        pii.get('type'),
                        pii.get('value'),
                        pii.get('confidence', 0.0),
                        pii.get('context', ''),
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde résultat: {e}")
    
    def generate_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Générer des recommandations basées sur les résultats"""
        recommendations = []
        
        # Compter les types de warnings
        warning_files = [r for r in results if r.get('warning', False)]
        pii_files = [r for r in results if r.get('pii_detected') and len(r['pii_detected']) > 0]
        
        if warning_files:
            recommendations.append(f"🔒 {len(warning_files)} fichier(s) sensible(s) détecté(s) - Envisager le chiffrement")
        
        if pii_files:
            recommendations.append(f"⚠️ {len(pii_files)} fichier(s) avec données personnelles - Vérifier la conformité RGPD")
        
        # Recommandations par agent
        agents_used = set(r.get('agent_type') for r in results)
        if 'nlp' in agents_used:
            recommendations.append("📝 Agent NLP utilisé - Analyse textuelle complète effectuée")
        if 'vision' in agents_used:
            recommendations.append("👁️ Agent Vision utilisé - Documents visuels analysés")
        if 'audio' in agents_used:
            recommendations.append("🎵 Agent Audio utilisé - Contenu vocal analysé")
        
        # Recommandations de sécurité
        if len(warning_files) > len(results) * 0.3:  # Plus de 30% de fichiers sensibles
            recommendations.append("🚨 Proportion élevée de fichiers sensibles - Audit de sécurité recommandé")
        
        return recommendations
    
    def generate_processing_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Générer un résumé du traitement"""
        if not results:
            return {}
        
        total_processing_time = sum(r.get('processing_time', 0) for r in results)
        avg_processing_time = total_processing_time / len(results)
        
        # Compter par agent
        agent_counts = {}
        for result in results:
            agent = result.get('agent_type', 'unknown')
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        # PII par type
        pii_types = {}
        for result in results:
            for pii in result.get('pii_detected', []):
                pii_type = pii.get('type', 'unknown')
                pii_types[pii_type] = pii_types.get(pii_type, 0) + 1
        
        return {
            'total_processing_time': total_processing_time,
            'average_processing_time': avg_processing_time,
            'agent_distribution': agent_counts,
            'pii_types_found': pii_types,
            'files_with_errors': len([r for r in results if 'error' in r.get('metadata', {})]),
            'largest_file': max((r.get('metadata', {}).get('file_size', 0) for r in results), default=0),
            'fastest_processing': min((r.get('processing_time', float('inf')) for r in results), default=0.0),
            'slowest_processing': max((r.get('processing_time', 0) for r in results), default=0.0)
        }
    
    async def consolidate_results(self, session_id: str, results: List[Dict[str, Any]]) -> ConsolidationReport:
        """Consolider les résultats de tous les agents"""
        logger.info(f"📁 Consolidation démarrée - Session: {session_id} - {len(results)} résultats")
        
        try:
            # 1. Sauvegarder les résultats en base
            for result in results:
                self.save_file_result(session_id, result)
            
            # 2. Générer les statistiques
            files_by_agent = {}
            files_with_warnings = 0
            
            for result in results:
                agent_type = result.get('agent_type', 'unknown')
                files_by_agent[agent_type] = files_by_agent.get(agent_type, 0) + 1
                
                if result.get('warning', False):
                    files_with_warnings += 1
            
            # 3. Générer le résumé du traitement
            processing_summary = self.generate_processing_summary(results)
            
            # 4. Générer les recommandations
            recommendations = self.generate_recommendations(results)
            
            # 5. Créer le rapport de consolidation
            report = ConsolidationReport(
                session_id=session_id,
                total_files=len(results),
                files_by_agent=files_by_agent,
                files_with_warnings=files_with_warnings,
                processing_summary=processing_summary,
                recommendations=recommendations,
                created_at=datetime.now().isoformat()
            )
            
            # 6. Sauvegarder le rapport
            report_path = Config.LOGS_DIR / f"consolidation_report_{session_id}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report.dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Consolidation terminée: {len(results)} fichiers, {files_with_warnings} warnings")
            logger.info(f"📄 Rapport sauvegardé: {report_path}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur consolidation: {e}")
            raise
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtenir l'historique des sessions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM sessions 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                columns = [description[0] for description in cursor.description]
                sessions = []
                
                for row in cursor.fetchall():
                    session_dict = dict(zip(columns, row))
                    sessions.append(session_dict)
                
                return sessions
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération historique: {e}")
            return []
    
    def get_pii_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques des PII détectées"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # PII par type
                cursor.execute('''
                    SELECT pii_type, COUNT(*) as count 
                    FROM pii_detections 
                    GROUP BY pii_type 
                    ORDER BY count DESC
                ''')
                
                pii_by_type = dict(cursor.fetchall())
                
                # PII par session
                cursor.execute('''
                    SELECT session_id, COUNT(*) as count 
                    FROM pii_detections 
                    GROUP BY session_id 
                    ORDER BY count DESC 
                    LIMIT 5
                ''')
                
                pii_by_session = dict(cursor.fetchall())
                
                return {
                    "pii_by_type": pii_by_type,
                    "top_sessions_with_pii": pii_by_session,
                    "total_pii_detected": sum(pii_by_type.values())
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur statistiques PII: {e}")
            return {}

# ──────────────────────────────────────────────────────────────────────────
# Serveur MCP pour l'Agent File Manager
# ──────────────────────────────────────────────────────────────────────────

# Instance globale de l'agent
file_manager_agent = RealFileManagerAgent()

if MCP_AVAILABLE:
    # Serveur MCP
    mcp = FastMCP("Agent File Manager MCP Réel")

    @mcp.tool()
    async def consolidate_results(session_id: str, results: List[Dict[str, Any]]) -> dict:
        """Consolider les résultats de tous les agents"""
        report = await file_manager_agent.consolidate_results(session_id, results)
        return report.dict()

    @mcp.tool()
    async def get_session_history(limit: int = 10) -> dict:
        """Obtenir l'historique des sessions"""
        history = file_manager_agent.get_session_history(limit)
        return {"sessions": history}

    @mcp.tool()
    async def get_pii_statistics() -> dict:
        """Obtenir les statistiques des PII détectées"""
        stats = file_manager_agent.get_pii_statistics()
        return stats

    @mcp.tool()
    async def get_agent_status() -> dict:
        """Obtenir le statut de l'agent File Manager"""
        return {
            "agent_name": file_manager_agent.agent_name,
            "database_path": str(file_manager_agent.db_path),
            "database_exists": file_manager_agent.db_path.exists()
        }

# ──────────────────────────────────────────────────────────────────────────
# Interface CLI et serveur HTTP simple
# ──────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

class ConsolidationRequest(BaseModel):
    session_id: str
    results: List[Dict[str, Any]]

# API HTTP pour la compatibilité
app = FastAPI(title="Agent File Manager MCP Réel", version="1.0.0")

@app.post("/consolidate_results")
async def api_consolidate_results(request: ConsolidationRequest):
    """Endpoint HTTP pour la consolidation"""
    try:
        report = await file_manager_agent.consolidate_results(
            request.session_id, 
            request.results
        )
        return report.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session_history")
async def api_session_history(limit: int = 10):
    """Obtenir l'historique des sessions"""
    history = file_manager_agent.get_session_history(limit)
    return {"sessions": history}

@app.get("/pii_statistics")
async def api_pii_statistics():
    """Obtenir les statistiques PII"""
    stats = file_manager_agent.get_pii_statistics()
    return stats

@app.get("/health")
async def health_check():
    """Check de santé de l'agent"""
    return {
        "status": "healthy",
        "agent": "file_manager",
        "database_ready": file_manager_agent.db_path.exists()
    }

async def main():
    """Interface principale pour l'agent File Manager"""
    print("Démarrage du serveur Agent File Manager sur le port 8005...")
    config = uvicorn.Config(app, host="0.0.0.0", port=8005, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    if MCP_AVAILABLE:
        # Mode serveur MCP
        mcp.run()
    else:
        # Mode serveur HTTP
        asyncio.run(main())
