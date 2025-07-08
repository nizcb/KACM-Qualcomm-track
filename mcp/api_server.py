"""
API FastAPI pour le Système Multi-Agents
========================================

API centrale qui orchestre tous les agents et sert d'interface
entre l'application desktop et le système multi-agents.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import os
import json
import logging
from pathlib import Path
from datetime import datetime
import shutil
import uuid

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class ProcessDirectoryRequest(BaseModel):
    directory_path: str
    recursive: bool = True
    filters: Optional[List[str]] = None

class ProcessDirectoryResponse(BaseModel):
    success: bool
    session_id: str
    total_files: int
    processed_files: int
    files_with_warnings: int
    processing_time: float
    results: List[Dict[str, Any]]

class SmartSearchRequest(BaseModel):
    query: str
    search_type: str = "semantic"  # semantic, exact, fuzzy
    include_vault: bool = True

class SmartSearchResponse(BaseModel):
    success: bool
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    search_time: float

class FileActionRequest(BaseModel):
    file_path: str
    action: str  # "encrypt", "decrypt", "analyze", "open"
    password: Optional[str] = None

class FileActionResponse(BaseModel):
    success: bool
    action: str
    file_path: str
    result_path: Optional[str] = None
    message: str

class SystemStatus(BaseModel):
    status: str
    agents: Dict[str, Dict[str, Any]]
    uptime: float
    last_activity: str

# ============================================================================
# INTÉGRATION AVEC LE SYSTÈME MCP SIMPLIFIÉ
# ============================================================================

# Importer le système MCP simplifié
try:
    from simple_mcp_system import orchestrator
    MCP_AVAILABLE = True
    print("✅ Système MCP simplifié disponible")
except ImportError:
    MCP_AVAILABLE = False
    orchestrator = None
    print("❌ Système MCP simplifié non disponible")

# ============================================================================
# SIMULATEUR D'AGENTS (À REMPLACER PAR LA VRAIE INTÉGRATION)
# ============================================================================

class AgentSimulator:
    """Simulateur des agents pour les tests"""
    
    def __init__(self):
        self.agents = {
            "orchestrator": {"status": "stopped", "port": 8001},
            "nlp": {"status": "stopped", "port": 8002},
            "vision": {"status": "stopped", "port": 8003},
            "audio": {"status": "stopped", "port": 8004},
            "file_manager": {"status": "stopped", "port": 8005},
            "security": {"status": "stopped", "port": 8006}
        }
        self.processed_files = {}
        self.vault_files = {}
        self.system_start_time = None
    
    async def start_all_agents(self):
        """Démarrer tous les agents"""
        logger.info("Démarrage de tous les agents...")
        
        # Utiliser le système MCP simplifié si disponible
        if MCP_AVAILABLE:
            try:
                await orchestrator.start_all_agents()
                self.mcp_system_running = True
                logger.info("✅ Système MCP simplifié démarré")
            except Exception as e:
                logger.error(f"❌ Erreur lors du démarrage MCP: {e}")
                self.mcp_system_running = False
        
        # Fallback simulation
        for agent_name in self.agents:
            await asyncio.sleep(0.5)  # Simulation du démarrage
            self.agents[agent_name]["status"] = "running"
            logger.info(f"Agent {agent_name} démarré")
        
        self.system_start_time = datetime.now()
        logger.info("Tous les agents sont démarrés")
    
    async def stop_all_agents(self):
        """Arrêter tous les agents"""
        logger.info("Arrêt de tous les agents...")
        
        # Arrêter le système MCP simplifié si en cours
        if MCP_AVAILABLE and self.mcp_system_running:
            try:
                await orchestrator.stop_all_agents()
                self.mcp_system_running = False
                logger.info("✅ Système MCP simplifié arrêté")
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'arrêt MCP: {e}")
        
        for agent_name in self.agents:
            self.agents[agent_name]["status"] = "stopped"
            logger.info(f"Agent {agent_name} arrêté")
        
        logger.info("Tous les agents sont arrêtés")
    
    async def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """Traiter un répertoire"""
        logger.info(f"Traitement du répertoire: {directory_path}")
        
        # Utiliser le système MCP simplifié si disponible
        if MCP_AVAILABLE and self.mcp_system_running:
            try:
                return await orchestrator.process_directory(directory_path)
            except Exception as e:
                logger.error(f"❌ Erreur MCP lors du traitement: {e}")
                # Fallback vers la simulation
        
        # Simulation originale
        
        if not os.path.exists(directory_path):
            raise HTTPException(status_code=404, detail="Répertoire non trouvé")
        
        session_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Scan des fichiers
        files = []
        for root, dirs, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path)
        
        # Simulation du traitement
        results = []
        files_with_warnings = 0
        
        for file_path in files:
            await asyncio.sleep(0.1)  # Simulation du traitement
            
            # Analyse du fichier
            file_ext = Path(file_path).suffix.lower()
            is_sensitive = self._is_sensitive_file(file_path)
            
            result = {
                "file_path": file_path,
                "filename": Path(file_path).name,
                "extension": file_ext,
                "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                "is_sensitive": is_sensitive,
                "agent_type": self._get_agent_type(file_ext),
                "summary": f"Fichier {file_ext} analysé",
                "warning": is_sensitive,
                "processing_time": 0.1
            }
            
            results.append(result)
            
            if is_sensitive:
                files_with_warnings += 1
                # Simulation du chiffrement
                vault_id = str(uuid.uuid4())
                self.vault_files[vault_id] = {
                    "original_path": file_path,
                    "filename": Path(file_path).name,
                    "encrypted_at": datetime.now().isoformat(),
                    "size": result["size"]
                }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "session_id": session_id,
            "total_files": len(files),
            "processed_files": len(results),
            "files_with_warnings": files_with_warnings,
            "processing_time": processing_time,
            "results": results
        }
    
    def _is_sensitive_file(self, file_path: str) -> bool:
        """Déterminer si un fichier est sensible"""
        filename = Path(file_path).name.lower()
        sensitive_keywords = [
            "carte", "vitale", "passeport", "identite", "cni", "permis",
            "rib", "iban", "banque", "medical", "ordonnance", "confidentiel",
            "secret", "prive", "personnel"
        ]
        
        return any(keyword in filename for keyword in sensitive_keywords)
    
    def _get_agent_type(self, file_ext: str) -> str:
        """Déterminer le type d'agent pour un fichier"""
        if file_ext in ['.txt', '.pdf', '.md', '.json', '.csv', '.xml', '.html']:
            return "nlp"
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            return "vision"
        elif file_ext in ['.mp3', '.wav', '.m4a', '.ogg', '.flac']:
            return "audio"
        else:
            return "file_manager"
    
    async def smart_search(self, query: str) -> Dict[str, Any]:
        """Recherche intelligente"""
        logger.info(f"Recherche intelligente: {query}")
        
        # Utiliser le système MCP simplifié si disponible
        if MCP_AVAILABLE and self.mcp_system_running:
            try:
                return await orchestrator.smart_search(query)
            except Exception as e:
                logger.error(f"❌ Erreur MCP lors de la recherche: {e}")
                # Fallback vers la simulation
        
        # Simulation originale
        
        start_time = datetime.now()
        results = []
        
        # Simulation de recherche IA
        await asyncio.sleep(1)  # Simulation du temps de traitement IA
        
        # Recherche dans les fichiers traités
        for result in self.processed_files.values():
            if self._matches_query(query, result):
                results.append(result)
        
        # Recherche dans le vault
        for vault_id, vault_file in self.vault_files.items():
            if self._matches_query(query, vault_file):
                vault_result = vault_file.copy()
                vault_result["vault_id"] = vault_id
                vault_result["requires_auth"] = True
                vault_result["location"] = "vault"
                results.append(vault_result)
        
        # Simulation de résultats basés sur la requête
        if not results:
            if "carte vitale" in query.lower():
                results.append({
                    "filename": "scan_carte_vitale.pdf",
                    "type": "sensitive",
                    "location": "vault",
                    "requires_auth": True,
                    "vault_id": "sample_vault_id",
                    "confidence": 0.95
                })
            elif "cours" in query.lower():
                results.append({
                    "filename": "cours_histoire.pdf",
                    "type": "document",
                    "location": "documents",
                    "requires_auth": False,
                    "confidence": 0.85
                })
        
        search_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "total_results": len(results),
            "search_time": search_time
        }
    
    def _matches_query(self, query: str, file_info: Dict[str, Any]) -> bool:
        """Vérifier si un fichier correspond à la requête"""
        query_lower = query.lower()
        filename = file_info.get("filename", "").lower()
        
        # Recherche simple par mots-clés
        if "carte vitale" in query_lower and "vitale" in filename:
            return True
        if "cours" in query_lower and "cours" in filename:
            return True
        if "photo" in query_lower and "photo" in filename:
            return True
        
        return False
    
    async def decrypt_file(self, vault_id: str, password: str) -> Dict[str, Any]:
        """Déchiffrer un fichier du vault"""
        logger.info(f"Tentative de déchiffrement: {vault_id}")
        
        if vault_id not in self.vault_files:
            raise HTTPException(status_code=404, detail="Fichier non trouvé dans le vault")
        
        # Vérification du mot de passe
        if password != "mon_secret_ultra_securise_2024":
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")
        
        vault_file = self.vault_files[vault_id]
        
        # Simulation du déchiffrement
        await asyncio.sleep(1)
        
        # Créer un fichier temporaire déchiffré
        temp_dir = Path("temp_decrypted")
        temp_dir.mkdir(exist_ok=True)
        
        decrypted_path = temp_dir / vault_file["filename"]
        
        # Copier le fichier original vers le répertoire temporaire
        if os.path.exists(vault_file["original_path"]):
            shutil.copy2(vault_file["original_path"], str(decrypted_path))
        else:
            # Créer un fichier de démonstration
            with open(decrypted_path, 'w', encoding='utf-8') as f:
                f.write(f"Fichier déchiffré: {vault_file['filename']}\n")
                f.write(f"Contenu simulé pour la démonstration.\n")
                f.write(f"Déchiffré le: {datetime.now().isoformat()}\n")
        
        return {
            "success": True,
            "action": "decrypt",
            "file_path": str(decrypted_path),
            "result_path": str(decrypted_path),
            "message": f"Fichier déchiffré avec succès: {vault_file['filename']}"
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtenir le statut du système"""
        uptime = 0
        if self.system_start_time:
            uptime = (datetime.now() - self.system_start_time).total_seconds()
        
        return {
            "status": "running" if any(agent["status"] == "running" for agent in self.agents.values()) else "stopped",
            "agents": self.agents,
            "uptime": uptime,
            "last_activity": datetime.now().isoformat()
        }

# ============================================================================
# INITIALISATION DE L'API
# ============================================================================

app = FastAPI(
    title="Multi-Agent System API",
    description="API pour le système multi-agents KACM Qualcomm",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation du simulateur d'agents
agent_simulator = AgentSimulator()

# ============================================================================
# ENDPOINTS DE L'API
# ============================================================================

@app.get("/")
async def root():
    """Endpoint racine"""
    return {"message": "Multi-Agent System API", "version": "1.0.0"}

@app.post("/system/start")
async def start_system():
    """Démarrer le système multi-agents"""
    try:
        await agent_simulator.start_all_agents()
        return {"success": True, "message": "Système démarré avec succès"}
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/system/stop")
async def stop_system():
    """Arrêter le système multi-agents"""
    try:
        await agent_simulator.stop_all_agents()
        return {"success": True, "message": "Système arrêté avec succès"}
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/status")
async def get_system_status():
    """Obtenir le statut du système"""
    return agent_simulator.get_system_status()

@app.post("/process/directory", response_model=ProcessDirectoryResponse)
async def process_directory(request: ProcessDirectoryRequest):
    """Traiter un répertoire"""
    try:
        result = await agent_simulator.process_directory(request.directory_path)
        return ProcessDirectoryResponse(**result)
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/smart", response_model=SmartSearchResponse)
async def smart_search(request: SmartSearchRequest):
    """Recherche intelligente"""
    try:
        result = await agent_simulator.smart_search(request.query)
        return SmartSearchResponse(**result)
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/file/decrypt", response_model=FileActionResponse)
async def decrypt_file(request: FileActionRequest):
    """Déchiffrer un fichier"""
    try:
        if not request.password:
            raise HTTPException(status_code=400, detail="Mot de passe requis")
        
        # Extraire vault_id du file_path
        vault_id = request.file_path.replace("vault:", "")
        
        result = await agent_simulator.decrypt_file(vault_id, request.password)
        return FileActionResponse(**result)
    except Exception as e:
        logger.error(f"Erreur lors du déchiffrement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/file/download/{file_path:path}")
async def download_file(file_path: str):
    """Télécharger un fichier"""
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        return FileResponse(file_path, filename=Path(file_path).name)
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vault/list")
async def list_vault_files():
    """Lister les fichiers du vault"""
    return {
        "success": True,
        "files": agent_simulator.vault_files
    }

@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Démarrage de l'API Multi-Agent System")
    print("📡 URL: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
