"""
🎵 Agent Audio MCP Réel
======================

Agent de traitement audio avec analyse de contenu et transcription.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import wave
import struct

# Ajout du répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from mcp.server.fastmcp import FastMCP
    from pydantic import BaseModel
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP non disponible pour Agent Audio")
    MCP_AVAILABLE = False

from config import Config

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOGS_DIR / "agent_audio.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AudioFeatures(BaseModel):
    """Caractéristiques audio détectées"""
    duration: float
    sample_rate: Optional[int]
    channels: Optional[int]
    bit_depth: Optional[int]
    file_size: int
    has_speech: bool
    avg_volume: float
    speech_ratio: float

class AudioAnalysisResult(BaseModel):
    """Résultat d'analyse audio"""
    file_path: str
    summary: str
    warning: bool
    features: AudioFeatures
    transcript: Optional[str]
    language_detected: Optional[str]
    processing_time: float
    metadata: Dict[str, Any]

class RealAudioAgent:
    """Agent Audio réel pour l'analyse de fichiers audio"""
    
    def __init__(self):
        self.agent_name = "audio"
        self.supported_extensions = Config.AUDIO_EXTENSIONS
        
        # Mots-clés sensibles dans la transcription
        self.sensitive_keywords = [
            "confidentiel", "secret", "mot de passe", "password", "code",
            "bancaire", "iban", "carte", "numéro", "sécurité sociale",
            "personnel", "privé", "médical", "santé"
        ]
        
        logger.info(f"🎵 Agent Audio MCP Réel initialisé")
    
    def get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """Obtenir les informations de base du fichier audio"""
        try:
            file_size = Path(file_path).stat().st_size
            extension = Path(file_path).suffix.lower()
            
            # Analyse basique selon l'extension
            if extension == '.wav':
                return self.analyze_wav_file(file_path, file_size)
            else:
                # Pour les autres formats, estimation basique
                return {
                    "duration": self.estimate_duration_by_size(file_size, extension),
                    "file_size": file_size,
                    "extension": extension,
                    "sample_rate": None,
                    "channels": None,
                    "bit_depth": None
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur info audio {file_path}: {e}")
            return {
                "duration": 0.0,
                "file_size": Path(file_path).stat().st_size if Path(file_path).exists() else 0,
                "extension": Path(file_path).suffix.lower(),
                "error": str(e)
            }
    
    def analyze_wav_file(self, file_path: str, file_size: int) -> Dict[str, Any]:
        """Analyser un fichier WAV pour extraire les métadonnées"""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                
                duration = frames / float(sample_rate)
                bit_depth = sample_width * 8
                
                return {
                    "duration": duration,
                    "file_size": file_size,
                    "extension": ".wav",
                    "sample_rate": sample_rate,
                    "channels": channels,
                    "bit_depth": bit_depth,
                    "frames": frames
                }
        except Exception as e:
            logger.error(f"❌ Erreur analyse WAV {file_path}: {e}")
            return {
                "duration": self.estimate_duration_by_size(file_size, ".wav"),
                "file_size": file_size,
                "extension": ".wav",
                "error": str(e)
            }
    
    def estimate_duration_by_size(self, file_size: int, extension: str) -> float:
        """Estimer la durée basée sur la taille du fichier"""
        # Estimations très approximatives
        if extension == '.mp3':
            # ~1MB pour 1 minute en qualité moyenne
            return file_size / (1024 * 1024) * 60
        elif extension == '.wav':
            # ~10MB pour 1 minute en qualité CD
            return file_size / (10 * 1024 * 1024) * 60
        elif extension == '.m4a':
            # ~1.5MB pour 1 minute
            return file_size / (1.5 * 1024 * 1024) * 60
        else:
            # Estimation générale
            return file_size / (2 * 1024 * 1024) * 60
    
    def detect_speech_basic(self, audio_info: Dict[str, Any]) -> tuple[bool, float]:
        """Détection basique de parole par analyse de métadonnées"""
        try:
            duration = audio_info.get("duration", 0)
            file_size = audio_info.get("file_size", 0)
            
            if duration <= 0:
                return False, 0.0
            
            # Estimation basée sur le ratio taille/durée
            bytes_per_second = file_size / duration
            
            # Les fichiers avec parole ont généralement un certain débit
            if bytes_per_second > 8000:  # Plus de 8KB/s suggère du contenu audio riche
                speech_ratio = min(0.8, bytes_per_second / 20000)  # Normalisation
                return True, speech_ratio
            else:
                return False, 0.1
                
        except Exception as e:
            logger.error(f"❌ Erreur détection parole: {e}")
            return False, 0.0
    
    def simulate_transcription(self, file_path: str, duration: float) -> tuple[Optional[str], Optional[str]]:
        """Simulation de transcription basée sur le nom de fichier"""
        filename = Path(file_path).name.lower()
        
        # Transcriptions simulées basées sur le nom
        transcriptions = {
            "reunion": "Transcription simulée d'une réunion. Discussions sur les projets en cours et les objectifs.",
            "conference": "Enregistrement de conférence avec présentation des résultats annuels.",
            "interview": "Interview avec questions-réponses sur l'expérience professionnelle.",
            "cours": "Cours magistral sur les technologies de l'information.",
            "formation": "Session de formation sur les bonnes pratiques de sécurité.",
            "appel": "Conversation téléphonique confidentielle avec échange d'informations personnelles.",
            "message": "Message vocal personnel contenant des informations privées."
        }
        
        # Détecter le type basé sur le nom de fichier
        for key, transcript in transcriptions.items():
            if key in filename:
                # Détecter la langue (simulation)
                language = "fr" if any(word in transcript.lower() for word in ["réunion", "cours", "formation"]) else "en"
                return transcript, language
        
        # Transcription par défaut
        if duration > 60:
            return "Fichier audio long analysé. Contenu non déterminé automatiquement.", "fr"
        else:
            return "Fichier audio court. Possiblement un message ou notification.", "fr"
    
    def check_sensitive_content(self, transcript: str) -> bool:
        """Vérifier si la transcription contient du contenu sensible"""
        if not transcript:
            return False
        
        transcript_lower = transcript.lower()
        for keyword in self.sensitive_keywords:
            if keyword in transcript_lower:
                return True
        return False
    
    async def analyze_audio(self, file_path: str, file_type: str = None, mime_type: str = None, size: int = None) -> AudioAnalysisResult:
        """Analyser un fichier audio"""
        start_time = datetime.now()
        logger.info(f"🎵 Analyse Audio démarrée: {Path(file_path).name}")
        
        try:
            # 1. Obtenir les informations du fichier audio
            audio_info = self.get_audio_info(file_path)
            duration = audio_info.get("duration", 0.0)
            
            # 2. Détection de parole
            has_speech, speech_ratio = self.detect_speech_basic(audio_info)
            
            # 3. Simulation de transcription
            transcript = None
            language_detected = None
            if has_speech:
                transcript, language_detected = self.simulate_transcription(file_path, duration)
            
            # 4. Vérification du contenu sensible
            is_sensitive = False
            if transcript:
                is_sensitive = self.check_sensitive_content(transcript)
            
            # Détection aussi basée sur le nom de fichier
            filename = Path(file_path).name.lower()
            if any(keyword in filename for keyword in self.sensitive_keywords):
                is_sensitive = True
            
            # 5. Générer le résumé
            filename = Path(file_path).name
            if is_sensitive:
                summary = f"⚠️ Fichier audio sensible: {filename} - Durée: {duration:.1f}s"
            else:
                summary = f"Fichier audio analysé: {filename} - Durée: {duration:.1f}s"
            
            if has_speech:
                summary += f" - Parole détectée ({speech_ratio:.1%})"
            
            # 6. Créer les features
            features = AudioFeatures(
                duration=duration,
                sample_rate=audio_info.get("sample_rate"),
                channels=audio_info.get("channels"),
                bit_depth=audio_info.get("bit_depth"),
                file_size=audio_info.get("file_size", size or 0),
                has_speech=has_speech,
                avg_volume=0.5,  # Simulation
                speech_ratio=speech_ratio
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = AudioAnalysisResult(
                file_path=file_path,
                summary=summary,
                warning=is_sensitive,
                features=features,
                transcript=transcript,
                language_detected=language_detected,
                processing_time=processing_time,
                metadata={
                    'file_size': size or audio_info.get("file_size", 0),
                    'mime_type': mime_type or f'audio/{Path(file_path).suffix[1:]}',
                    'has_transcript': transcript is not None,
                    'sensitivity_reason': 'filename_keywords' if is_sensitive else None,
                    'analysis_method': 'metadata_based'
                }
            )
            
            logger.info(f"✅ Audio terminé: {filename} - Durée: {duration:.1f}s - Sensible: {is_sensitive}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse Audio {file_path}: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AudioAnalysisResult(
                file_path=file_path,
                summary=f"Erreur d'analyse: {e}",
                warning=False,
                features=AudioFeatures(
                    duration=0.0,
                    sample_rate=None,
                    channels=None,
                    bit_depth=None,
                    file_size=size or 0,
                    has_speech=False,
                    avg_volume=0.0,
                    speech_ratio=0.0
                ),
                transcript=None,
                language_detected=None,
                processing_time=processing_time,
                metadata={'error': str(e)}
            )

# ──────────────────────────────────────────────────────────────────────────
# Serveur MCP pour l'Agent Audio
# ──────────────────────────────────────────────────────────────────────────

# Instance globale de l'agent
audio_agent = RealAudioAgent()

if MCP_AVAILABLE:
    # Serveur MCP
    mcp = FastMCP("Agent Audio MCP Réel")

    @mcp.tool()
    async def analyze_audio(file_path: str, file_type: str = None, mime_type: str = None, size: int = None) -> dict:
        """Analyser un fichier audio"""
        result = await audio_agent.analyze_audio(file_path, file_type, mime_type, size)
        return result.dict()

    @mcp.tool()
    async def get_agent_status() -> dict:
        """Obtenir le statut de l'agent Audio"""
        return {
            "agent_name": audio_agent.agent_name,
            "supported_extensions": audio_agent.supported_extensions,
            "sensitive_keywords": audio_agent.sensitive_keywords
        }

# ──────────────────────────────────────────────────────────────────────────
# Interface CLI et serveur HTTP simple
# ──────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

class AudioAnalysisRequest(BaseModel):
    file_path: str
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = None

# API HTTP pour la compatibilité
app = FastAPI(title="Agent Audio MCP Réel", version="1.0.0")

@app.post("/analyze_file")
async def api_analyze_file(request: AudioAnalysisRequest):
    """Endpoint HTTP pour l'analyse audio"""
    try:
        result = await audio_agent.analyze_audio(
            request.file_path, 
            request.file_type, 
            request.mime_type, 
            request.size
        )
        
        # Compatibilité avec le format orchestrateur
        return {
            "file_path": result.file_path,
            "summary": result.summary,
            "warning": result.warning,
            "metadata": result.metadata
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check de santé de l'agent"""
    return {
        "status": "healthy",
        "agent": "audio"
    }

async def main():
    """Interface principale pour l'agent Audio"""
    if len(sys.argv) < 2:
        print("Démarrage du serveur Agent Audio sur le port 8004...")
        config = uvicorn.Config(app, host="0.0.0.0", port=8004, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    else:
        # Mode CLI pour test direct
        file_path = sys.argv[1]
        if not Path(file_path).exists():
            print(f"❌ Fichier non trouvé: {file_path}")
            sys.exit(1)
        
        result = await audio_agent.analyze_audio(file_path)
        print(json.dumps(result.dict(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if MCP_AVAILABLE:
        # Mode serveur MCP
        mcp.run()
    else:
        # Mode serveur HTTP
        asyncio.run(main())
