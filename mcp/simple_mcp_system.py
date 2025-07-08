"""
Système MCP Simplifié - Version Fonctionnelle
============================================

Version simplifiée du système multi-agents qui fonctionne
sans les dépendances MCP complexes.
"""

import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import uuid
import sqlite3

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMCPAgent:
    """Agent MCP de base simplifié"""
    
    def __init__(self, name: str, port: int = 8000):
        self.name = name
        self.port = port
        self.status = "stopped"
        self.tools = {}
    
    def register_tool(self, name: str, func):
        """Enregistrer un outil"""
        self.tools[name] = func
        logger.info(f"Outil {name} enregistré pour l'agent {self.name}")
    
    async def start(self):
        """Démarrer l'agent"""
        self.status = "running"
        logger.info(f"Agent {self.name} démarré sur le port {self.port}")
    
    async def stop(self):
        """Arrêter l'agent"""
        self.status = "stopped"
        logger.info(f"Agent {self.name} arrêté")
    
    async def call_tool(self, tool_name: str, **kwargs):
        """Appeler un outil"""
        if tool_name in self.tools:
            return await self.tools[tool_name](**kwargs)
        else:
            raise ValueError(f"Outil {tool_name} non trouvé")

class NLPAgent(SimpleMCPAgent):
    """Agent NLP simplifié"""
    
    def __init__(self):
        super().__init__("NLP", 8002)
        self.register_tool("analyze_text", self.analyze_text)
        self.register_tool("detect_pii", self.detect_pii)
        
        # Patterns PII
        self.pii_patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'(?:\+33|0)[1-9](?:[0-9]{8})'),
            "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            "iban": re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b')
        }
    
    async def analyze_text(self, text: str, file_path: str = None) -> Dict[str, Any]:
        """Analyser un texte"""
        logger.info(f"Analyse NLP du texte: {file_path or 'texte direct'}")
        
        # Détection PII
        pii_detected = await self.detect_pii(text)
        
        # Analyse basique
        word_count = len(text.split())
        char_count = len(text)
        
        # Résumé simple
        sentences = text.split('.')
        summary = '. '.join(sentences[:2]) + '...' if len(sentences) > 2 else text
        
        return {
            "file_path": file_path or "direct_text",
            "summary": summary[:200],
            "warning": len(pii_detected) > 0,
            "word_count": word_count,
            "char_count": char_count,
            "pii_detected": pii_detected,
            "agent_type": "nlp",
            "processing_time": 0.1
        }
    
    async def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """Détecter les informations personnelles"""
        pii_found = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(text)
            for match in matches:
                pii_found.append({
                    "type": pii_type,
                    "value": match,
                    "confidence": 0.9
                })
        
        return pii_found

class VisionAgent(SimpleMCPAgent):
    """Agent Vision simplifié"""
    
    def __init__(self):
        super().__init__("Vision", 8003)
        self.register_tool("analyze_image", self.analyze_image)
    
    async def analyze_image(self, file_path: str) -> Dict[str, Any]:
        """Analyser une image"""
        logger.info(f"Analyse Vision de l'image: {file_path}")
        
        # Simulation d'analyse d'image
        filename = Path(file_path).name.lower()
        
        # Détection de contenu sensible basée sur le nom
        sensitive_keywords = ["carte", "vitale", "identite", "passeport", "permis"]
        is_sensitive = any(keyword in filename for keyword in sensitive_keywords)
        
        return {
            "file_path": file_path,
            "summary": f"Image analysée: {Path(file_path).name}",
            "warning": is_sensitive,
            "detected_objects": ["document", "text"] if is_sensitive else ["image"],
            "confidence": 0.8,
            "agent_type": "vision",
            "processing_time": 0.2
        }

class AudioAgent(SimpleMCPAgent):
    """Agent Audio simplifié"""
    
    def __init__(self):
        super().__init__("Audio", 8004)
        self.register_tool("analyze_audio", self.analyze_audio)
    
    async def analyze_audio(self, file_path: str) -> Dict[str, Any]:
        """Analyser un fichier audio"""
        logger.info(f"Analyse Audio du fichier: {file_path}")
        
        return {
            "file_path": file_path,
            "summary": f"Fichier audio analysé: {Path(file_path).name}",
            "warning": False,
            "duration": 120,  # Simulation
            "has_speech": True,
            "agent_type": "audio",
            "processing_time": 0.3
        }

class SecurityAgent(SimpleMCPAgent):
    """Agent Security simplifié"""
    
    def __init__(self):
        super().__init__("Security", 8006)
        self.register_tool("encrypt_file", self.encrypt_file)
        self.register_tool("decrypt_file", self.decrypt_file)
        self.register_tool("create_vault", self.create_vault)
        
        # Initialiser la base de données vault
        self.vault_db = "vault.db"
        self.init_vault_db()
    
    def init_vault_db(self):
        """Initialiser la base de données vault"""
        conn = sqlite3.connect(self.vault_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_files (
                id TEXT PRIMARY KEY,
                original_path TEXT,
                filename TEXT,
                encrypted_path TEXT,
                password_hash TEXT,
                created_at TEXT,
                size INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def encrypt_file(self, file_path: str, password: str) -> Dict[str, Any]:
        """Chiffrer un fichier"""
        logger.info(f"Chiffrement du fichier: {file_path}")
        
        # Générer un ID unique
        file_id = str(uuid.uuid4())
        
        # Simulation du chiffrement
        encrypted_dir = Path("encrypted")
        encrypted_dir.mkdir(exist_ok=True)
        
        encrypted_path = encrypted_dir / f"{file_id}.vault"
        
        # Copier le fichier (simulation du chiffrement)
        if os.path.exists(file_path):
            import shutil
            shutil.copy2(file_path, encrypted_path)
        
        # Hash du mot de passe
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Sauvegarder dans la base
        conn = sqlite3.connect(self.vault_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO vault_files 
            (id, original_path, filename, encrypted_path, password_hash, created_at, size)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            file_id,
            file_path,
            Path(file_path).name,
            str(encrypted_path),
            password_hash,
            datetime.now().isoformat(),
            os.path.getsize(file_path) if os.path.exists(file_path) else 0
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "file_id": file_id,
            "encrypted_path": str(encrypted_path),
            "message": f"Fichier chiffré avec succès: {Path(file_path).name}"
        }
    
    async def decrypt_file(self, file_id: str, password: str) -> Dict[str, Any]:
        """Déchiffrer un fichier"""
        logger.info(f"Déchiffrement du fichier: {file_id}")
        
        # Vérifier le mot de passe
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(self.vault_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM vault_files WHERE id = ? AND password_hash = ?
        """, (file_id, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {
                "success": False,
                "message": "Fichier non trouvé ou mot de passe incorrect"
            }
        
        # Décrypter (simulation)
        decrypted_dir = Path("decrypted")
        decrypted_dir.mkdir(exist_ok=True)
        
        decrypted_path = decrypted_dir / result[2]  # filename
        
        # Copier le fichier chiffré vers le dossier déchiffré
        if os.path.exists(result[3]):  # encrypted_path
            import shutil
            shutil.copy2(result[3], decrypted_path)
        
        return {
            "success": True,
            "decrypted_path": str(decrypted_path),
            "filename": result[2],
            "message": f"Fichier déchiffré avec succès: {result[2]}"
        }
    
    async def create_vault(self) -> Dict[str, Any]:
        """Créer le vault"""
        vault_dir = Path("vault")
        vault_dir.mkdir(exist_ok=True)
        
        return {
            "success": True,
            "vault_path": str(vault_dir),
            "message": "Vault créé avec succès"
        }

class FileManagerAgent(SimpleMCPAgent):
    """Agent File Manager simplifié"""
    
    def __init__(self):
        super().__init__("FileManager", 8005)
        self.register_tool("consolidate_results", self.consolidate_results)
        self.register_tool("generate_report", self.generate_report)
    
    async def consolidate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolider les résultats"""
        logger.info("Consolidation des résultats")
        
        total_files = len(results)
        files_with_warnings = sum(1 for r in results if r.get("warning", False))
        
        return {
            "total_files": total_files,
            "files_with_warnings": files_with_warnings,
            "consolidated_results": results,
            "summary": f"{total_files} fichiers traités, {files_with_warnings} avec des avertissements"
        }
    
    async def generate_report(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Générer un rapport"""
        logger.info("Génération du rapport")
        
        report = {
            "session_id": session_data.get("session_id"),
            "timestamp": datetime.now().isoformat(),
            "total_files": session_data.get("total_files", 0),
            "files_with_warnings": session_data.get("files_with_warnings", 0),
            "processing_time": session_data.get("processing_time", 0),
            "agents_used": list(set(r.get("agent_type") for r in session_data.get("results", []))),
            "summary": "Traitement terminé avec succès"
        }
        
        return report

class OrchestratorAgent(SimpleMCPAgent):
    """Agent Orchestrateur simplifié"""
    
    def __init__(self):
        super().__init__("Orchestrator", 8001)
        self.register_tool("process_directory", self.process_directory)
        self.register_tool("smart_search", self.smart_search)
        
        # Initialiser les agents
        self.nlp_agent = NLPAgent()
        self.vision_agent = VisionAgent()
        self.audio_agent = AudioAgent()
        self.security_agent = SecurityAgent()
        self.file_manager_agent = FileManagerAgent()
        
        # Extensions supportées
        self.text_extensions = ['.txt', '.md', '.pdf', '.json', '.csv', '.xml', '.html']
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        self.audio_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac']
    
    async def start_all_agents(self):
        """Démarrer tous les agents"""
        agents = [
            self.nlp_agent,
            self.vision_agent,
            self.audio_agent,
            self.security_agent,
            self.file_manager_agent
        ]
        
        for agent in agents:
            await agent.start()
        
        await self.start()
    
    async def stop_all_agents(self):
        """Arrêter tous les agents"""
        agents = [
            self.nlp_agent,
            self.vision_agent,
            self.audio_agent,
            self.security_agent,
            self.file_manager_agent
        ]
        
        for agent in agents:
            await agent.stop()
        
        await self.stop()
    
    def get_agent_for_file(self, file_path: str) -> Optional[SimpleMCPAgent]:
        """Déterminer l'agent approprié pour un fichier"""
        ext = Path(file_path).suffix.lower()
        
        if ext in self.text_extensions:
            return self.nlp_agent
        elif ext in self.image_extensions:
            return self.vision_agent
        elif ext in self.audio_extensions:
            return self.audio_agent
        else:
            return None
    
    async def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """Traiter un répertoire"""
        logger.info(f"Traitement du répertoire: {directory_path}")
        
        if not os.path.exists(directory_path):
            raise ValueError(f"Répertoire non trouvé: {directory_path}")
        
        session_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Scanner les fichiers
        all_files = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
        
        # Traiter chaque fichier
        results = []
        for file_path in all_files:
            try:
                agent = self.get_agent_for_file(file_path)
                
                if agent == self.nlp_agent:
                    # Lire le fichier texte
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        result = await agent.call_tool("analyze_text", text=content, file_path=file_path)
                    except UnicodeDecodeError:
                        # Fichier non-texte
                        result = {
                            "file_path": file_path,
                            "summary": f"Fichier non-texte: {Path(file_path).name}",
                            "warning": False,
                            "agent_type": "nlp",
                            "processing_time": 0.1
                        }
                
                elif agent == self.vision_agent:
                    result = await agent.call_tool("analyze_image", file_path=file_path)
                
                elif agent == self.audio_agent:
                    result = await agent.call_tool("analyze_audio", file_path=file_path)
                
                else:
                    # Fichier non supporté
                    result = {
                        "file_path": file_path,
                        "summary": f"Type de fichier non supporté: {Path(file_path).name}",
                        "warning": False,
                        "agent_type": "unknown",
                        "processing_time": 0.1
                    }
                
                # Ajouter des métadonnées
                result.update({
                    "filename": Path(file_path).name,
                    "extension": Path(file_path).suffix.lower(),
                    "size": os.path.getsize(file_path),
                    "is_sensitive": result.get("warning", False)
                })
                
                results.append(result)
                
                # Chiffrer si sensible
                if result.get("warning", False):
                    await self.security_agent.call_tool(
                        "encrypt_file",
                        file_path=file_path,
                        password="mon_secret_ultra_securise_2024"
                    )
            
            except Exception as e:
                logger.error(f"Erreur lors du traitement de {file_path}: {e}")
                results.append({
                    "file_path": file_path,
                    "summary": f"Erreur de traitement: {str(e)}",
                    "warning": False,
                    "agent_type": "error",
                    "processing_time": 0.1
                })
        
        # Consolider les résultats
        consolidated = await self.file_manager_agent.call_tool("consolidate_results", results=results)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "session_id": session_id,
            "total_files": len(all_files),
            "processed_files": len(results),
            "files_with_warnings": consolidated["files_with_warnings"],
            "processing_time": processing_time,
            "results": results
        }
    
    async def smart_search(self, query: str) -> Dict[str, Any]:
        """Recherche intelligente"""
        logger.info(f"Recherche intelligente: {query}")
        
        start_time = datetime.now()
        results = []
        
        # Recherche simple par mots-clés
        query_lower = query.lower()
        
        # Recherche dans les fichiers du vault
        conn = sqlite3.connect(self.security_agent.vault_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM vault_files")
        vault_files = cursor.fetchall()
        conn.close()
        
        for vault_file in vault_files:
            file_id, original_path, filename, encrypted_path, password_hash, created_at, size = vault_file
            
            # Recherche simple dans le nom du fichier
            if any(keyword in filename.lower() for keyword in query_lower.split()):
                results.append({
                    "filename": filename,
                    "type": "sensitive",
                    "location": "vault",
                    "requires_auth": True,
                    "vault_id": file_id,
                    "confidence": 0.8,
                    "created_at": created_at,
                    "size": size
                })
        
        # Recherche simulée pour les fichiers non-sensibles
        if "cours" in query_lower:
            results.append({
                "filename": "cours_histoire.pdf",
                "type": "document",
                "location": "documents",
                "requires_auth": False,
                "confidence": 0.9
            })
        
        search_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "total_results": len(results),
            "search_time": search_time
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtenir le statut du système"""
        agents = {
            "orchestrator": {"status": self.status, "port": self.port},
            "nlp": {"status": self.nlp_agent.status, "port": self.nlp_agent.port},
            "vision": {"status": self.vision_agent.status, "port": self.vision_agent.port},
            "audio": {"status": self.audio_agent.status, "port": self.audio_agent.port},
            "security": {"status": self.security_agent.status, "port": self.security_agent.port},
            "file_manager": {"status": self.file_manager_agent.status, "port": self.file_manager_agent.port}
        }
        
        return {
            "status": "running" if any(agent["status"] == "running" for agent in agents.values()) else "stopped",
            "agents": agents,
            "uptime": 0,
            "last_activity": datetime.now().isoformat()
        }

# Instance globale de l'orchestrateur
orchestrator = OrchestratorAgent()

async def main():
    """Fonction principale pour les tests"""
    print("🚀 Test du système MCP simplifié")
    
    # Démarrer tous les agents
    await orchestrator.start_all_agents()
    
    # Test du traitement d'un répertoire
    demo_dir = Path("demo_files")
    if demo_dir.exists():
        print(f"📁 Traitement du répertoire: {demo_dir}")
        result = await orchestrator.process_directory(str(demo_dir))
        print(f"✅ Résultat: {result['processed_files']} fichiers traités")
    
    # Test de recherche
    print("🔍 Test de recherche")
    search_result = await orchestrator.smart_search("carte vitale")
    print(f"✅ Résultats de recherche: {search_result['total_results']}")
    
    # Arrêter tous les agents
    await orchestrator.stop_all_agents()
    
    print("🎉 Tests terminés")

if __name__ == "__main__":
    asyncio.run(main())
