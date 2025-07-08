"""
👁️ Agent Vision MCP Réel
========================

Agent de traitement d'images avec reconnaissance de documents sensibles.
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
from PIL import Image, ImageStat
import base64

# Ajout du répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from mcp.server.fastmcp import FastMCP
    from pydantic import BaseModel
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP non disponible pour Agent Vision")
    MCP_AVAILABLE = False

from config import Config

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOGS_DIR / "agent_vision.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DetectedObject(BaseModel):
    """Objet détecté dans l'image"""
    type: str
    confidence: float
    description: str

class VisionAnalysisResult(BaseModel):
    """Résultat d'analyse d'image"""
    file_path: str
    summary: str
    warning: bool
    detected_objects: List[DetectedObject]
    is_sensitive_document: bool
    image_properties: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any]

class RealVisionAgent:
    """Agent Vision réel pour l'analyse d'images"""
    
    def __init__(self):
        self.agent_name = "vision"
        self.supported_extensions = Config.IMAGE_EXTENSIONS
        
        # Mots-clés de documents sensibles
        self.sensitive_keywords = [
            "carte", "vitale", "identite", "passeport", "permis", "conduire",
            "national", "cni", "secu", "social", "bancaire", "credit",
            "medical", "ordonnance", "facture", "document", "officiel"
        ]
        
        # Patterns visuels basiques pour la détection
        self.document_indicators = {
            "carte_vitale": ["vert", "carte", "vitale", "secu"],
            "carte_identite": ["cni", "republique", "francaise", "identite"],
            "passeport": ["passeport", "passport", "republic"],
            "permis_conduire": ["permis", "conduire", "prefecture"],
            "document_bancaire": ["iban", "rib", "banque", "compte"]
        }
        
        logger.info(f"👁️ Agent Vision MCP Réel initialisé")
    
    def analyze_image_properties(self, image_path: str) -> Dict[str, Any]:
        """Analyser les propriétés de base de l'image"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
                format_img = img.format
                
                # Statistiques de couleur
                if mode in ['RGB', 'RGBA']:
                    stat = ImageStat.Stat(img)
                    avg_colors = stat.mean
                else:
                    avg_colors = [0, 0, 0]
                
                return {
                    "width": width,
                    "height": height,
                    "mode": mode,
                    "format": format_img,
                    "aspect_ratio": round(width / height, 2),
                    "total_pixels": width * height,
                    "average_colors": avg_colors[:3]  # RGB seulement
                }
        except Exception as e:
            logger.error(f"❌ Erreur analyse propriétés image {image_path}: {e}")
            return {"error": str(e)}
    
    def detect_sensitive_document_by_filename(self, file_path: str) -> tuple[bool, str, float]:
        """Détection basée sur le nom de fichier"""
        filename = Path(file_path).name.lower()
        
        for doc_type, keywords in self.document_indicators.items():
            for keyword in keywords:
                if keyword in filename:
                    return True, doc_type, 0.8
        
        # Vérification générale
        for keyword in self.sensitive_keywords:
            if keyword in filename:
                return True, "document_sensible", 0.6
        
        return False, "document_normal", 0.1
    
    def detect_document_by_colors(self, properties: Dict[str, Any]) -> tuple[bool, str, float]:
        """Détection basique par analyse des couleurs"""
        try:
            avg_colors = properties.get("average_colors", [0, 0, 0])
            r, g, b = avg_colors[0], avg_colors[1], avg_colors[2]
            
            # Carte vitale (dominante verte)
            if g > r * 1.2 and g > b * 1.2 and g > 100:
                return True, "carte_vitale_possible", 0.7
            
            # Document officiel (beaucoup de blanc/bleu)
            if r > 200 and g > 200 and b > 200:  # Blanc dominant
                return True, "document_officiel_possible", 0.5
            
            # Carte d'identité (couleurs spécifiques)
            if abs(r - 150) < 30 and abs(g - 150) < 30 and abs(b - 200) < 30:
                return True, "carte_identite_possible", 0.6
            
            return False, "image_normale", 0.2
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse couleurs: {e}")
            return False, "analyse_impossible", 0.0
    
    def detect_document_by_aspect_ratio(self, properties: Dict[str, Any]) -> tuple[bool, str, float]:
        """Détection par ratio d'aspect (format carte, A4, etc.)"""
        try:
            aspect_ratio = properties.get("aspect_ratio", 1.0)
            
            # Format carte de crédit/vitale (1.586)
            if 1.5 <= aspect_ratio <= 1.7:
                return True, "format_carte", 0.6
            
            # Format A4 ou document (1.414)
            if 1.3 <= aspect_ratio <= 1.5:
                return True, "format_document", 0.5
            
            # Format passeport/carré
            if 0.8 <= aspect_ratio <= 1.2:
                return True, "format_passeport", 0.4
            
            return False, "format_non_document", 0.1
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse ratio: {e}")
            return False, "analyse_impossible", 0.0
    
    async def analyze_image(self, file_path: str, file_type: str = None, mime_type: str = None, size: int = None) -> VisionAnalysisResult:
        """Analyser une image pour détecter des documents sensibles"""
        start_time = datetime.now()
        logger.info(f"👁️ Analyse Vision démarrée: {Path(file_path).name}")
        
        try:
            # 1. Analyser les propriétés de l'image
            properties = self.analyze_image_properties(file_path)
            
            if "error" in properties:
                raise Exception(f"Impossible d'analyser l'image: {properties['error']}")
            
            # 2. Détections multiples
            detections = []
            is_sensitive = False
            max_confidence = 0.0
            
            # Détection par nom de fichier
            sens_filename, type_filename, conf_filename = self.detect_sensitive_document_by_filename(file_path)
            if sens_filename:
                is_sensitive = True
                max_confidence = max(max_confidence, conf_filename)
                detections.append(DetectedObject(
                    type=type_filename,
                    confidence=conf_filename,
                    description=f"Détecté par nom de fichier: {type_filename}"
                ))
            
            # Détection par couleurs
            sens_colors, type_colors, conf_colors = self.detect_document_by_colors(properties)
            if sens_colors:
                is_sensitive = True
                max_confidence = max(max_confidence, conf_colors)
                detections.append(DetectedObject(
                    type=type_colors,
                    confidence=conf_colors,
                    description=f"Détecté par analyse couleur: {type_colors}"
                ))
            
            # Détection par ratio
            sens_ratio, type_ratio, conf_ratio = self.detect_document_by_aspect_ratio(properties)
            if sens_ratio:
                is_sensitive = True
                max_confidence = max(max_confidence, conf_ratio)
                detections.append(DetectedObject(
                    type=type_ratio,
                    confidence=conf_ratio,
                    description=f"Détecté par format: {type_ratio}"
                ))
            
            # Si aucune détection spécifique, ajouter une détection générale
            if not detections:
                detections.append(DetectedObject(
                    type="image_standard",
                    confidence=0.9,
                    description="Image analysée sans détection de document sensible"
                ))
            
            # 3. Générer le résumé
            filename = Path(file_path).name
            if is_sensitive:
                summary = f"⚠️ Document sensible détecté dans {filename} - Confiance: {max_confidence:.2f}"
            else:
                summary = f"Image standard analysée: {filename}"
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = VisionAnalysisResult(
                file_path=file_path,
                summary=summary,
                warning=is_sensitive,
                detected_objects=detections,
                is_sensitive_document=is_sensitive,
                image_properties=properties,
                processing_time=processing_time,
                metadata={
                    'file_size': size or 0,
                    'mime_type': mime_type or 'image/unknown',
                    'detection_methods': ['filename', 'colors', 'aspect_ratio'],
                    'max_confidence': max_confidence,
                    'total_detections': len(detections)
                }
            )
            
            logger.info(f"✅ Vision terminé: {filename} - Sensible: {is_sensitive} - Confiance: {max_confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse Vision {file_path}: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return VisionAnalysisResult(
                file_path=file_path,
                summary=f"Erreur d'analyse: {e}",
                warning=False,
                detected_objects=[],
                is_sensitive_document=False,
                image_properties={},
                processing_time=processing_time,
                metadata={'error': str(e)}
            )

# ──────────────────────────────────────────────────────────────────────────
# Serveur MCP pour l'Agent Vision
# ──────────────────────────────────────────────────────────────────────────

# Instance globale de l'agent
vision_agent = RealVisionAgent()

if MCP_AVAILABLE:
    # Serveur MCP
    mcp = FastMCP("Agent Vision MCP Réel")

    @mcp.tool()
    async def analyze_image(file_path: str, file_type: str = None, mime_type: str = None, size: int = None) -> dict:
        """Analyser une image pour détecter des documents sensibles"""
        result = await vision_agent.analyze_image(file_path, file_type, mime_type, size)
        return result.dict()

    @mcp.tool()
    async def get_agent_status() -> dict:
        """Obtenir le statut de l'agent Vision"""
        return {
            "agent_name": vision_agent.agent_name,
            "supported_extensions": vision_agent.supported_extensions,
            "sensitive_keywords": vision_agent.sensitive_keywords
        }

# ──────────────────────────────────────────────────────────────────────────
# Interface CLI et serveur HTTP simple
# ──────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

class ImageAnalysisRequest(BaseModel):
    file_path: str
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = None

# API HTTP pour la compatibilité
app = FastAPI(title="Agent Vision MCP Réel", version="1.0.0")

@app.post("/analyze_file")
async def api_analyze_file(request: ImageAnalysisRequest):
    """Endpoint HTTP pour l'analyse d'images"""
    try:
        result = await vision_agent.analyze_image(
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
        "agent": "vision"
    }

async def main():
    """Interface principale pour l'agent Vision"""
    if len(sys.argv) < 2:
        print("Démarrage du serveur Agent Vision sur le port 8003...")
        config = uvicorn.Config(app, host="0.0.0.0", port=8003, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    else:
        # Mode CLI pour test direct
        file_path = sys.argv[1]
        if not Path(file_path).exists():
            print(f"❌ Fichier non trouvé: {file_path}")
            sys.exit(1)
        
        result = await vision_agent.analyze_image(file_path)
        print(json.dumps(result.dict(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    if MCP_AVAILABLE:
        # Mode serveur MCP
        mcp.run()
    else:
        # Mode serveur HTTP
        asyncio.run(main())
