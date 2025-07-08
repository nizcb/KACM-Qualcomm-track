"""
🧠 Agent NLP MCP Réel avec Ollama/Llama 3.2:1b
===============================================

Agent NLP intelligent utilisant vraiment Ollama/Llama pour l'analyse de texte,
la détection PII et l'analyse sémantique avancée.
"""

import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
import PyPDF2
from dataclasses import dataclass

# Ajout du répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from mcp.server.fastmcp import FastMCP
    from pydantic import BaseModel
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP non disponible pour Agent NLP")
    MCP_AVAILABLE = False

from config import Config

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOGS_DIR / "agent_nlp.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PIIDetection(BaseModel):
    """Détection d'information personnelle"""
    type: str
    value: str
    confidence: float
    context: str

class NLPAnalysisResult(BaseModel):
    """Résultat d'analyse NLP"""
    file_path: str
    summary: str
    warning: bool
    word_count: int
    language: str
    sentiment: str
    pii_detected: List[PIIDetection]
    topics: List[str]
    processing_time: float
    metadata: Dict[str, Any]

class RealNLPAgent:
    """Agent NLP réel avec Ollama/Llama 3.2:1b"""
    
    def __init__(self):
        self.agent_name = "nlp"
        self.ollama_host = Config.OLLAMA_HOST
        self.ollama_model = Config.OLLAMA_MODEL
        self.supported_extensions = Config.TEXT_EXTENSIONS
        
        # Patterns PII avancés
        self.pii_patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone_fr": re.compile(r'(?:\+33|0)[1-9](?:[0-9]{8})'),
            "phone_intl": re.compile(r'\+\d{1,3}[-.\s]?\d{1,14}'),
            "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            "ssn_fr": re.compile(r'\b[12]\d{2}(0[1-9]|1[0-2])\d{2}\d{3}\d{3}\d{2}\b'),
            "iban": re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}[A-Z0-9]{1,23}\b'),
            "ip_address": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        }
        
        logger.info(f"🧠 Agent NLP MCP Réel initialisé avec Ollama: {self.ollama_host}")
    
    async def check_ollama_health(self) -> bool:
        """Vérifier si Ollama est disponible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_host}/api/tags")
                return response.status_code == 200
        except:
            return False
    
    async def call_ollama(self, prompt: str) -> Optional[str]:
        """Appel à Ollama/Llama pour analyse intelligente"""
        try:
            if not await self.check_ollama_health():
                logger.warning("⚠️ Ollama non disponible, analyse basique")
                return None
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                }
                
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', '').strip()
                else:
                    logger.error(f"❌ Erreur Ollama HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur appel Ollama: {e}")
            return None
    
    def read_file_content(self, file_path: str) -> str:
        """Lire le contenu d'un fichier selon son type"""
        try:
            path_obj = Path(file_path)
            extension = path_obj.suffix.lower()
            
            if extension == '.pdf':
                return self.read_pdf(file_path)
            elif extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                # Fichiers texte classiques
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"❌ Erreur lecture fichier {file_path}: {e}")
            return f"Erreur lecture: {e}"
    
    def read_pdf(self, file_path: str) -> str:
        """Extraire le texte d'un PDF"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"❌ Erreur lecture PDF {file_path}: {e}")
            return f"Erreur lecture PDF: {e}"
    
    def detect_pii_basic(self, content: str) -> List[PIIDetection]:
        """Détection PII basique avec regex"""
        pii_found = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.finditer(content)
            for match in matches:
                # Extraire le contexte autour de la détection
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 20)
                context = content[start:end].replace('\n', ' ').strip()
                
                pii_found.append(PIIDetection(
                    type=pii_type,
                    value=match.group(),
                    confidence=0.8,  # Confiance regex
                    context=context
                ))
        
        return pii_found
    
    async def detect_pii_ai(self, content: str) -> List[PIIDetection]:
        """Détection PII avancée avec Ollama/Llama"""
        prompt = f"""Analyse ce texte et détecte les informations personnelles (PII):

TEXTE À ANALYSER:
{content[:1000]}...

Réponds UNIQUEMENT en JSON avec cette structure:
{{"pii": [{{"type": "email|phone|name|address|id", "value": "valeur_détectée", "confidence": 0.0-1.0}}]}}

Détecte: emails, téléphones, noms complets, adresses, identifiants, numéros de sécurité sociale, cartes bancaires."""
        
        try:
            response = await self.call_ollama(prompt)
            if response:
                # Parser la réponse JSON
                try:
                    data = json.loads(response)
                    pii_list = []
                    for item in data.get('pii', []):
                        pii_list.append(PIIDetection(
                            type=item.get('type', 'unknown'),
                            value=item.get('value', ''),
                            confidence=float(item.get('confidence', 0.5)),
                            context=f"Détecté par IA: {item.get('value', '')}"
                        ))
                    return pii_list
                except json.JSONDecodeError:
                    logger.warning("⚠️ Réponse Ollama non-JSON, utilisation détection basique")
                    return []
            return []
        except Exception as e:
            logger.error(f"❌ Erreur détection PII IA: {e}")
            return []
    
    async def analyze_semantics_ai(self, content: str) -> Dict[str, Any]:
        """Analyse sémantique avec Ollama/Llama"""
        prompt = f"""Analyse sémantique de ce texte:

TEXTE:
{content[:800]}...

Réponds en JSON avec:
{{"summary": "résumé_en_2_phrases", "sentiment": "positive|negative|neutral", "language": "fr|en|...", "topics": ["topic1", "topic2"], "is_sensitive": true/false}}"""
        
        try:
            response = await self.call_ollama(prompt)
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.error(f"❌ Erreur analyse sémantique: {e}")
        
        # Fallback basique
        words = content.split()
        return {
            "summary": ' '.join(words[:30]) + '...' if len(words) > 30 else content,
            "sentiment": "neutral",
            "language": "fr",
            "topics": ["document"],
            "is_sensitive": False
        }
    
    async def analyze_file(self, file_path: str, file_type: str = None, mime_type: str = None, size: int = None) -> NLPAnalysisResult:
        """Analyser un fichier texte avec l'IA"""
        start_time = datetime.now()
        logger.info(f"🧠 Analyse NLP démarrée: {Path(file_path).name}")
        
        try:
            # 1. Lire le contenu
            content = self.read_file_content(file_path)
            if content.startswith("Erreur"):
                raise Exception(content)
            
            word_count = len(content.split())
            
            # 2. Détection PII (basique + IA)
            pii_basic = self.detect_pii_basic(content)
            pii_ai = await self.detect_pii_ai(content)
            
            # Combiner les détections (éviter les doublons)
            all_pii = pii_basic + pii_ai
            unique_pii = []
            seen_values = set()
            for pii in all_pii:
                if pii.value not in seen_values:
                    unique_pii.append(pii)
                    seen_values.add(pii.value)
            
            # 3. Analyse sémantique avec IA
            semantics = await self.analyze_semantics_ai(content)
            
            # 4. Déterminer si le fichier est sensible
            has_pii = len(unique_pii) > 0
            is_sensitive_ai = semantics.get('is_sensitive', False)
            warning = has_pii or is_sensitive_ai
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = NLPAnalysisResult(
                file_path=file_path,
                summary=semantics.get('summary', 'Document analysé'),
                warning=warning,
                word_count=word_count,
                language=semantics.get('language', 'fr'),
                sentiment=semantics.get('sentiment', 'neutral'),
                pii_detected=unique_pii,
                topics=semantics.get('topics', ['document']),
                processing_time=processing_time,
                metadata={
                    'file_size': size or 0,
                    'mime_type': mime_type or 'text/plain',
                    'pii_count': len(unique_pii),
                    'analysis_method': 'ai_enhanced' if await self.check_ollama_health() else 'basic'
                }
            )
            
            logger.info(f"✅ NLP terminé: {Path(file_path).name} - {len(unique_pii)} PII détectés - Warning: {warning}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse NLP {file_path}: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return NLPAnalysisResult(
                file_path=file_path,
                summary=f"Erreur d'analyse: {e}",
                warning=False,
                word_count=0,
                language="unknown",
                sentiment="neutral",
                pii_detected=[],
                topics=["error"],
                processing_time=processing_time,
                metadata={'error': str(e)}
            )

# ──────────────────────────────────────────────────────────────────────────
# Serveur MCP pour l'Agent NLP
# ──────────────────────────────────────────────────────────────────────────

# Instance globale de l'agent
nlp_agent = RealNLPAgent()

if MCP_AVAILABLE:
    # Serveur MCP
    mcp = FastMCP("Agent NLP MCP Réel")

    @mcp.tool()
    async def analyze_file(file_path: str, file_type: str = None, mime_type: str = None, size: int = None) -> dict:
        """Analyser un fichier texte avec l'IA Ollama/Llama"""
        result = await nlp_agent.analyze_file(file_path, file_type, mime_type, size)
        return result.dict()

    @mcp.tool()
    async def detect_pii_in_text(text: str) -> dict:
        """Détecter les PII dans un texte"""
        pii_basic = nlp_agent.detect_pii_basic(text)
        pii_ai = await nlp_agent.detect_pii_ai(text)
        
        all_pii = pii_basic + pii_ai
        unique_pii = []
        seen_values = set()
        for pii in all_pii:
            if pii.value not in seen_values:
                unique_pii.append(pii)
                seen_values.add(pii.value)
        
        return {
            "pii_detected": [pii.dict() for pii in unique_pii],
            "total_count": len(unique_pii)
        }

    @mcp.tool() 
    async def summarize_text(text: str) -> dict:
        """Résumer un texte avec l'IA"""
        semantics = await nlp_agent.analyze_semantics_ai(text)
        return semantics

    @mcp.tool()
    async def get_agent_status() -> dict:
        """Obtenir le statut de l'agent NLP"""
        ollama_available = await nlp_agent.check_ollama_health()
        return {
            "agent_name": nlp_agent.agent_name,
            "ollama_available": ollama_available,
            "ollama_host": nlp_agent.ollama_host,
            "ollama_model": nlp_agent.ollama_model,
            "supported_extensions": nlp_agent.supported_extensions
        }

# ──────────────────────────────────────────────────────────────────────────
# Interface CLI et serveur HTTP simple
# ──────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

class FileAnalysisRequest(BaseModel):
    file_path: str
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = None

# API HTTP pour la compatibilité
app = FastAPI(title="Agent NLP MCP Réel", version="1.0.0")

@app.post("/analyze_file")
async def api_analyze_file(request: FileAnalysisRequest):
    """Endpoint HTTP pour l'analyse de fichiers"""
    try:
        result = await nlp_agent.analyze_file(
            request.file_path, 
            request.file_type, 
            request.mime_type, 
            request.size
        )
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check de santé de l'agent"""
    ollama_available = await nlp_agent.check_ollama_health()
    return {
        "status": "healthy",
        "agent": "nlp",
        "ollama_available": ollama_available
    }

async def main():
    """Interface principale pour l'agent NLP"""
    if len(sys.argv) < 2:
        print("Démarrage du serveur Agent NLP sur le port 8002...")
        config = uvicorn.Config(app, host="0.0.0.0", port=8002, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    else:
        # Mode CLI pour test direct
        file_path = sys.argv[1]
        if not Path(file_path).exists():
            print(f"❌ Fichier non trouvé: {file_path}")
            sys.exit(1)
        
        result = await nlp_agent.analyze_file(file_path)
        print(json.dumps(result.dict(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if MCP_AVAILABLE:
        # Mode serveur MCP
        mcp.run()
    else:
        # Mode serveur HTTP
        asyncio.run(main())
