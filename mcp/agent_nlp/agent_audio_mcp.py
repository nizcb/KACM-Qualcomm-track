"""
Agent Audio MCP avec capacités IA complètes - Version Agent Autonome
===================================================================

Agent Audio autonome MCP qui peut :
- Analyser des fichiers audio et détecter les PII vocales avec intelligence contextuelle
- Transcription speech-to-text avec Whisper local
- Détection PII textuelle dans les transcriptions (email, téléphone, noms, adresses)
- Résumé intelligent avec LLama-3 local via LangChain
- Exposer toutes ses capacités via le protocole MCP officiel

Utilise Ollama/Llama + LangChain pour l'IA, Whisper pour la transcription, avec fallback intelligent.
Format de sortie standardisé: {filepath, summary, warning}
"""

import asyncio
import json
import logging
import os
import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
import time

# Suppression des avertissements
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Imports MCP officiels
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
from mcp.types import TextContent
from pydantic import BaseModel, Field

# LangChain imports pour l'IA
try:
    from langchain_community.llms import Ollama
    from langchain.tools import tool
    LANGCHAIN_AVAILABLE = True
    print("✅ LangChain disponible")
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain non disponible")

# Whisper pour la transcription
try:
    import whisper
    WHISPER_AVAILABLE = True
    print("✅ Whisper disponible")
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ Whisper non disponible")

# numpy pour les calculs
try:
    import numpy as np
    NUMPY_AVAILABLE = True
    print("✅ NumPy disponible")
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ NumPy non disponible")

# Configuration du logging avec support Unicode pour Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/audio_agent.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Configuration Ollama/LLama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.2:latest")

# Initialisation du LLM
llm = None
if LANGCHAIN_AVAILABLE:
    try:
        llm = Ollama(
            model=LLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.3  # Plus déterministe pour l'analyse audio
        )
        # Test de connexion
        test_response = llm.invoke("Test audio")
        logger.info("✅ Ollama/Llama Audio connecté avec succès")
        print("✅ Agent Audio IA Ollama/Llama prêt")
    except Exception as e:
        logger.warning(f"⚠️ Connexion Ollama échouée: {e}")
        print(f"⚠️ Connexion Ollama échouée: {e}")
        llm = None

# Regex patterns pour la détection PII dans les transcriptions
PII_REGEXES: Dict[str, re.Pattern] = {
    "EMAIL": re.compile(r"[\w\.\-]+@[\w\.-]+\.[a-z]{2,}", re.I),
    "PHONE": re.compile(r"\+?\d{1,3}[\s\-]?\d[\d\s\-]{8,}\d", re.I),
    "CARD": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
    "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b"),
    "SSN": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"),
}

# ──────────────────────────────────────────────────────────────────────────
# Modèles de données
# ──────────────────────────────────────────────────────────────────────────

class AudioArgs(BaseModel):
    """Arguments pour l'analyse audio"""
    path: str
    audio_bytes: Optional[bytes] = None

class AudioResponse(BaseModel):
    """Réponse standardisée de l'agent Audio (format unifié avec NLP/Vision)"""
    filepath: str
    summary: str
    warning: bool  # True = contient des informations sensibles

# ──────────────────────────────────────────────────────────────────────────
# Fonctions principales d'analyse audio
# ──────────────────────────────────────────────────────────────────────────

def detect_pii_in_text(text: str) -> List[str]:
    """
    Détecte les PII dans le texte transcrit
    
    Args:
        text: Texte à analyser
        
    Returns:
        Liste des types de PII détectés
    """
    pii_detected = []
    
    for pii_type, pattern in PII_REGEXES.items():
        matches = pattern.findall(text)
        if matches:
            pii_detected.append(pii_type)
            logger.warning(f"⚠️ PII détecté dans la transcription: {pii_type} ({len(matches)} occurrences)")
    
    # Détection de mots-clés sensibles spécifiques à l'audio
    sensitive_keywords = [
        "mot de passe", "password", "code secret", "pin", "carte bancaire",
        "numéro de carte", "compte en banque", "sécurité sociale", "insee",
        "date de naissance", "né le", "née le", "adresse", "je habite",
        "téléphone", "portable", "email", "mail", "skype", "whatsapp"
    ]
    
    text_lower = text.lower()
    for keyword in sensitive_keywords:
        if keyword in text_lower:
            pii_detected.append("SENSITIVE_KEYWORD")
            logger.warning(f"⚠️ Mot-clé sensible détecté: {keyword}")
            break
    
    return pii_detected

def transcribe_audio_simple(file_path: str) -> str:
    """
    Transcription audio simple avec fallback
    
    Args:
        file_path: Chemin du fichier audio
        
    Returns:
        Texte transcrit
    """
    try:
        if not WHISPER_AVAILABLE:
            logger.warning("❌ Whisper non disponible")
            return ""
        
        # Charger Whisper (modèle base pour bon compromis vitesse/qualité)
        logger.info(f"🎙️ Chargement modèle Whisper...")
        model = whisper.load_model("base")
        
        logger.info(f"🎙️ Début transcription: {Path(file_path).name}")
        
        # Transcription
        result = model.transcribe(file_path, language="fr")
        text = result.get("text", "").strip()
        
        logger.info(f"✅ Transcription réussie: {len(text)} caractères")
        if text:
            logger.info(f"📝 Aperçu: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        
        return text
        
    except Exception as e:
        logger.error(f"❌ Erreur transcription: {e}")
        return ""

async def analyze_audio_with_ai(file_path: str, use_ai: bool = True) -> dict:
    """
    Analyse complète d'un fichier audio avec IA (format standardisé)
    
    Args:
        file_path: Chemin du fichier audio
        use_ai: Utiliser l'IA pour l'analyse (défaut: True)
        
    Returns:
        Dictionnaire avec filepath, summary, warning (format unifié)
    """
    try:
        logger.info(f"🎵 Début analyse audio: {file_path}")
        
        # Vérifier l'existence du fichier
        if not os.path.exists(file_path):
            return {
                'filepath': file_path,
                'summary': 'Fichier audio non trouvé',
                'warning': False
            }
        
        # Vérifier le format
        supported_formats = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.mp4']
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in supported_formats:
            return {
                'filepath': file_path,
                'summary': f'Format audio non supporté: {file_ext}',
                'warning': False
            }
        
        # Transcription
        transcription = transcribe_audio_simple(file_path)
        
        if not transcription:
            return {
                'filepath': str(Path(file_path).resolve()),
                'summary': 'Fichier audio analysé mais transcription vide ou impossible',
                'warning': False
            }
        
        # Détection PII
        pii_detected = detect_pii_in_text(transcription)
        warning = len(pii_detected) > 0
        
        # Analyse avec IA si disponible
        if use_ai and llm and LANGCHAIN_AVAILABLE:
            try:
                prompt = f"""Analyse ce contenu audio transcrit et détermine s'il contient des informations sensibles.

Transcription: "{transcription}"

PII détectés automatiquement: {', '.join(pii_detected) if pii_detected else 'Aucun'}

Fournis un résumé intelligent du contenu audio en français.
Si des informations sensibles sont présentes, mentionne-le clairement dans le résumé.
Sois concis mais informatif.

Résumé:"""

                ai_summary = llm.invoke(prompt)
                
                # Nettoyer la réponse
                summary = ai_summary.strip()
                if len(summary) > 300:
                    summary = summary[:300] + "..."
                
                logger.info(f"✅ Analyse IA audio terminée: {len(summary)} caractères")
                
            except Exception as e:
                logger.error(f"❌ Erreur analyse IA: {e}")
                summary = f"Transcription audio ({len(transcription)} caractères)"
                if warning:
                    summary += f" - Informations sensibles détectées: {', '.join(pii_detected)}"
        else:
            # Fallback sans IA
            summary = f"Transcription audio ({len(transcription)} caractères)"
            if len(transcription) > 100:
                summary += f": {transcription[:100]}..."
            else:
                summary += f": {transcription}"
                
            if warning:
                summary += f" - ATTENTION: Informations sensibles détectées: {', '.join(pii_detected)}"
        
        result = {
            'filepath': str(Path(file_path).resolve()),
            'summary': summary,
            'warning': warning
        }
        
        logger.info(f"🎯 Analyse audio terminée - Warning: {warning}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur analyse audio: {e}")
        return {
            'filepath': file_path,
            'summary': f'Erreur analyse audio: {str(e)}',
            'warning': False
        }

# ──────────────────────────────────────────────────────────────────────────
# Fonction principale pour l'orchestrator (compatible avec agent_nlp)
# ──────────────────────────────────────────────────────────────────────────

async def process_file_with_ai(file_path: str) -> dict:
    """
    Point d'entrée principal pour l'orchestrator - compatible avec agent_nlp
    
    Args:
        file_path: Chemin du fichier audio
        
    Returns:
        Dictionnaire avec file_path, summary, warning (format unifié)
    """
    result = await analyze_audio_with_ai(file_path, use_ai=True)
    
    # Assurer le format unifié (filepath → file_path pour compatibilité)
    return {
        'file_path': result['filepath'],
        'summary': result['summary'],
        'warning': result['warning']
    }

# ──────────────────────────────────────────────────────────────────────────
# Serveur MCP FastMCP
# ──────────────────────────────────────────────────────────────────────────

mcp = FastMCP("Agent Audio MCP")

@mcp.tool()
async def analyze_audio(args: AudioArgs) -> dict:
    """
    Analyse un fichier audio et détecte les informations sensibles
    
    Args:
        args: Arguments contenant le chemin du fichier audio
        
    Returns:
        Dictionnaire avec filepath, summary et warning
    """
    try:
        result = await analyze_audio_with_ai(args.path, use_ai=True)
        return result
    except Exception as e:
        logger.error(f"❌ Erreur tool analyze_audio: {e}")
        return {
            'filepath': args.path,
            'summary': f'Erreur analyse audio: {str(e)}',
            'warning': False
        }

@mcp.tool()
async def transcribe_audio_only(file_path: str) -> dict:
    """
    Transcrit uniquement un fichier audio sans analyse PII
    
    Args:
        file_path: Chemin du fichier audio
        
    Returns:
        Transcription du fichier audio
    """
    try:
        transcription = transcribe_audio_simple(file_path)
        return {
            'file_path': file_path,
            'transcription': transcription,
            'length': len(transcription)
        }
    except Exception as e:
        logger.error(f"❌ Erreur transcribe_audio_only: {e}")
        return {'error': str(e)}

@mcp.tool()
async def process_audio_file(file_path: str, use_ai: bool = True) -> dict:
    """
    Traite un fichier audio avec l'IA
    
    Args:
        file_path: Chemin du fichier audio
        use_ai: Utiliser l'IA pour l'analyse
        
    Returns:
        Résultat de l'analyse
    """
    try:
        result = await analyze_audio_with_ai(file_path, use_ai)
        return result
    except Exception as e:
        logger.error(f"❌ Erreur process_audio_file: {e}")
        return {'error': str(e)}

# ──────────────────────────────────────────────────────────────────────────
# Interface CLI
# ──────────────────────────────────────────────────────────────────────────

async def main():
    """Interface en ligne de commande"""
    if len(sys.argv) < 2:
        print("Agent Audio MCP - Analyse de fichiers audio avec IA")
        print("=" * 50)
        print("\nUsage:")
        print("  python agent_audio_mcp.py <audio_file>        # Analyse complète")
        print("  python agent_audio_mcp.py --server            # Lancer serveur MCP")
        print("\nFormats supportés:")
        print("  • .mp3, .wav, .m4a, .ogg, .flac, .aac, .mp4")
        print("\nExemples:")
        print("  python agent_audio_mcp.py ./audio/meeting.mp3")
        print("  python agent_audio_mcp.py ./recordings/call.wav")
        return
    
    if sys.argv[1] == "--server":
        print("🎵 Démarrage du serveur MCP Audio Agent...")
        await mcp.run()
        return
    
    # Analyse du fichier fourni
    audio_file = sys.argv[1]
    
    print(f"\n🎵 Agent Audio - Analyse de fichier")
    print(f"📁 Fichier: {audio_file}")
    print("=" * 50)
    
    result = await analyze_audio_with_ai(audio_file)
    
    print(f"\n🎯 === RÉSULTAT FINAL ===")
    print(f"📁 Filepath: {result['filepath']}")
    print(f"📄 Summary: {result['summary']}")
    print(f"⚠️ Warning: {result['warning']}")
    
    print(f"\n{'=' * 50}")
    print("✅ Analyse terminée")

if __name__ == "__main__":
    asyncio.run(main())
