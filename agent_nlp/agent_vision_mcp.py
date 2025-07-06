#!/usr/bin/env python3
"""
Agent Vision MCP avec capacités IA complètes - Version Agent Autonome
====================================================================

Agent Vision autonome MCP qui peut :
- Analyser des images et détecter les PII visuelles avec intelligence contextuelle
- OCR multilangue (EasyOCR) avec préprocessing avancé
- Détection PII textuelle et visuelle (cartes bancaires, documents d'identité, contenu NSFW)
- Résumé intelligent avec LLama-3 local via LangChain
- Raisonner sur les tâches à accomplir (ReAct pattern)
- Exposer toutes ses capacités via le protocole MCP officiel

Utilise Ollama/Llama + LangChain pour l'IA, EasyOCR pour l'OCR, avec fallback intelligent.
"""

import asyncio
import json
import logging
import os
import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import time
import threading
import tempfile
import concurrent.futures

# Suppression des avertissements
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Imports MCP officiels
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
from mcp.server.fastmcp import Image as MCPImage
from mcp.types import TextContent
from pydantic import BaseModel, Field

# Imports vision
import cv2
import numpy as np
import requests
from PIL import Image
from io import BytesIO

# Fix PIL/Pillow ANTIALIAS pour nouvelles versions
try:
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
        print("✅ Fix PIL ANTIALIAS appliqué")
except AttributeError:
    pass

# EasyOCR pour OCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    print("✅ EasyOCR disponible")
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️ EasyOCR non disponible")

# LangChain imports pour l'IA
try:
    from langchain_community.llms import Ollama
    from langchain.tools import tool
    LANGCHAIN_AVAILABLE = True
    print("✅ LangChain disponible")
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain non disponible")

# Import ONNX pour détection NSFW
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
    print("✅ ONNX Runtime disponible")
except ImportError:
    ONNX_AVAILABLE = False
    ort = None
    print("⚠️ ONNX Runtime non disponible")

# Configuration du logging avec support Unicode pour Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/vision_agent.log', encoding='utf-8')
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
            temperature=0.3  # Plus déterministe pour l'analyse d'images
        )
        # Test de connexion
        test_response = llm.invoke("Test vision")
        logger.info("✅ Ollama/Llama Vision connecté avec succès")
        print("✅ Agent Vision IA Ollama/Llama prêt")
    except Exception as e:
        logger.warning(f"⚠️ Connexion Ollama échouée: {e}")
        print(f"⚠️ Connexion Ollama échouée: {e}")
        llm = None

# Regex patterns pour la détection PII dans le texte OCR
PII_REGEXES: Dict[str, re.Pattern] = {
    "EMAIL": re.compile(r"[\w\.\-]+@[\w\.-]+\.[a-z]{2,}", re.I),
    "PHONE": re.compile(r"\+?\d{1,3}[\s\-]?\d[\d\s\-]{8,}\d", re.I),
    "CARD": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
    "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b"),
    "SSN": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"),
}



# Configuration du logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class VisionArgs(BaseModel):
    """Arguments pour l'analyse de document visuel"""
    path: str
    image_bytes: Optional[bytes] = None

class VisionResponse(BaseModel):
    """Réponse simplifiée de l'agent Vision - 3 attributs seulement"""
    filepath: str
    summary: str
    warning: bool  # True = contient des informations sensibles

class NSFWDetector:
    """
    Détecteur NSFW embarqué utilisant un modèle ONNX local
    Chargement paresseux pour optimiser la mémoire
    """
    
    def __init__(self, model_path: str = "ai_models/nsfw/nsfw_model.onnx"):
        self.model_path = Path(model_path).resolve()  # Cross-platform path handling
        self.session = None
        self.input_name = None
        self.output_name = None
        self.lock = threading.Lock()
        
    def _load_model(self) -> bool:
        """Charge le modèle ONNX (chargement paresseux)"""
        if not ONNX_AVAILABLE:
            logger.warning("ONNX Runtime non disponible - utilisation fallback détection NSFW")
            return False
            
        if not self.model_path.exists():
            logger.warning(f"Modèle NSFW non trouvé: {self.model_path}")
            return False
            
        try:
            # Configuration session ONNX optimisée pour CPU/NPU
            providers = ['CPUExecutionProvider']
            
            # Essayer d'utiliser le NPU Qualcomm si disponible
            if hasattr(ort, 'get_available_providers'):
                available_providers = ort.get_available_providers()
                if 'QNNExecutionProvider' in available_providers:
                    providers.insert(0, 'QNNExecutionProvider')
                    logger.info("🚀 NPU Qualcomm détecté pour NSFW")
                    
            self.session = ort.InferenceSession(
                str(self.model_path),
                providers=providers
            )
            
            # Récupérer les noms d'entrée/sortie
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            
            logger.info(f"✅ Modèle NSFW chargé: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle NSFW: {e}")
            return False
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Préprocessing standard pour modèles NSFW
        Redimensionne à 224x224 et normalise
        """
        # Redimensionner à 224x224 (taille standard)
        resized = cv2.resize(image, (224, 224))
        
        # Convertir BGR -> RGB
        rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normaliser [0-255] -> [0-1]
        normalized = rgb_image.astype(np.float32) / 255.0
        
        # Format batch: (1, 3, 224, 224) pour ONNX
        preprocessed = np.transpose(normalized, (2, 0, 1))  # HWC -> CHW
        preprocessed = np.expand_dims(preprocessed, axis=0)  # Add batch dimension
        
        return preprocessed
    
    async def predict_nsfw_score(self, image: np.ndarray) -> float:
        """
        Prédit le score NSFW d'une image (0.0 = safe, 1.0 = NSFW)
        Exécution asynchrone pour ne pas bloquer le thread principal
        """
        def _run_inference():
            with self.lock:
                # Chargement paresseux du modèle
                if self.session is None:
                    if not self._load_model():
                        return 0.0  # Fallback: considérer comme safe
                
                try:
                    # Préprocessing
                    input_data = self._preprocess_image(image)
                    
                    # Inférence ONNX
                    outputs = self.session.run(
                        [self.output_name],
                        {self.input_name: input_data}
                    )
                    
                    # Le modèle retourne généralement [safe_score, nsfw_score]
                    predictions = outputs[0][0]
                    
                    # Si format [safe, nsfw], prendre nsfw_score
                    if len(predictions) >= 2:
                        nsfw_score = float(predictions[1])
                    else:
                        # Si un seul score, c'est probablement le score NSFW
                        nsfw_score = float(predictions[0])
                    
                    return max(0.0, min(1.0, nsfw_score))  # Clamp [0, 1]
                    
                except Exception as e:
                    logger.error(f"❌ Erreur inférence NSFW: {e}")
                    return 0.0
        
        # Exécuter en arrière-plan pour ne pas bloquer l'async
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_inference)
            return future.result(timeout=5.0)  # Timeout 5s max

# Instance globale du détecteur NSFW
nsfw_detector = NSFWDetector()

def diagnose_system_dependencies():
    """
    Diagnostic cross-platform des dépendances système
    Vérifie les installations et guide l'utilisateur
    """
    import platform
    import shutil
    import sys
    from pathlib import Path
    
    system = platform.system()
    architecture = platform.machine()
    python_version = sys.version
    
    print(f"\n🔍 DIAGNOSTIC SYSTÈME - VisionAgent Cross-Platform")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🖥️  OS: {system} ({architecture})")
    print(f"🐍 Python: {python_version}")
    
    # Détection environnement
    if 'conda' in sys.executable.lower():
        env_type = "Conda/Anaconda"
        env_path = Path(sys.executable).parent.parent
    elif hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        env_type = "Virtual Environment"
        env_path = Path(sys.prefix)
    else:
        env_type = "Système Global"
        env_path = Path(sys.prefix)
    
    print(f"📦 Environnement: {env_type}")
    print(f"📁 Chemin: {env_path}")
    
    # Vérification des dépendances Python
    print(f"\n📚 DÉPENDANCES PYTHON:")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    required_packages = {
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'easyocr': 'easyocr',
        'numpy': 'numpy',
        'requests': 'requests',
        'pydantic': 'pydantic'
    }
    
    missing_packages = []
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MANQUANT")
            missing_packages.append(package)
    
    # Instructions d'installation pour les packages manquants
    if missing_packages:
        print(f"\n🛠️  INSTRUCTIONS D'INSTALLATION:")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📦 Packages Python manquants:")
        if env_type.startswith("Conda"):
            print(f"   conda install {' '.join(missing_packages)}")
        else:
            print(f"   pip install {' '.join(missing_packages)}")
    else:
        print(f"\n✅ SYSTÈME PRÊT - Toutes les dépendances sont installées !")
    
    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return len(missing_packages) == 0

class VisionAgent:
    """Agent Vision pour analyse de documents visuels avec LLM intelligent"""
    
    def __init__(self):
        """Initialise l'agent avec les modèles nécessaires"""
        self.ocr_reader = None
        self.llm_url = "http://localhost:11434/v1/chat/completions"  # Ollama local
        
        logger.info("Agent Vision initialisé - Mode LLM intelligent")
    
    def test_llm_connection(self) -> bool:
        """Test rapide de connectivité LLM"""
        try:
            test_payload = {
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            response = requests.post(self.llm_url, json=test_payload, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ LLM connecté: {self.llm_url}")
                return True
            else:
                logger.warning(f"❌ LLM erreur {response.status_code}: {self.llm_url}")
                return False
        except Exception as e:
            logger.warning(f"❌ LLM inaccessible: {e}")
            return False
    
    def test_llm_vision_capability(self) -> bool:
        """Test si le LLM peut analyser les images directement (multimodal)"""
        try:
            # Créer une petite image de test encodée en base64
            import base64
            test_image = np.zeros((50, 50, 3), dtype=np.uint8)
            test_image.fill(255)  # Image blanche simple
            cv2.putText(test_image, "TEST", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            # Encoder en base64
            _, buffer = cv2.imencode('.jpg', test_image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Test avec format OpenAI vision
            vision_payload = {
                "messages": [
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": "What do you see in this image? Answer in one word only."},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ],
                "max_tokens": 10
            }
            
            response = requests.post(self.llm_url, json=vision_payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['choices'][0]['message']['content'].strip().lower()
                
                # Vérifier si la réponse contient du texte relatif à l'image
                if any(word in response_text for word in ['test', 'text', 'word', 'image', 'see']):
                    logger.info("🎯 LLM Vision DÉTECTÉ: Le modèle peut analyser les images directement!")
                    return True
                else:
                    logger.info(f"📝 LLM Vision partiel: réponse='{response_text}' (non concluant)")
                    return False
            else:
                logger.info(f"❌ LLM Vision test échoué: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.info(f"📝 LLM Vision non disponible: {e}")
            return False
    
    def _init_ocr(self):
        """Initialise EasyOCR de manière lazy avec cache global"""
        if self.ocr_reader is None:
            try:
                # Utiliser le cache global pour éviter les réinitialisations
                self.ocr_reader = get_global_ocr_reader()
                logger.info("OCR global réutilisé pour cette instance")
                
            except Exception as e:
                logger.error(f"Erreur initialisation EasyOCR: {e}")
                logger.error("Vérifiez que torch et torchvision sont installés correctement")
                self.ocr_reader = None
                raise
    
    def _load_image(self, path: str, bytes_data: Optional[bytes] = None) -> Optional[np.ndarray]:
        """Charge une image depuis un chemin ou des bytes"""
        try:
            if bytes_data:
                # Charger depuis bytes
                image = Image.open(BytesIO(bytes_data))
                return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                # Charger depuis fichier avec gestion cross-platform des chemins
                file_path = Path(path).resolve()
                if not file_path.exists():
                    logger.error(f"Fichier non trouvé: {file_path}")
                    return None
                
                # Solution robuste pour caractères spéciaux et tous OS
                # Utiliser PIL puis convertir en OpenCV
                try:
                    # Méthode 1: Utiliser PIL pour compatibilité cross-platform
                    pil_image = Image.open(str(file_path))  # Conversion explicite en string
                    # Convertir PIL en array numpy puis en format OpenCV (BGR)
                    if pil_image.mode == 'RGBA':
                        # Convertir RGBA en RGB puis BGR
                        pil_image = pil_image.convert('RGB')
                    elif pil_image.mode == 'L':
                        # Image en niveaux de gris
                        return np.array(pil_image)
                    
                    # Convertir RGB en BGR pour OpenCV
                    image_array = np.array(pil_image)
                    if len(image_array.shape) == 3:
                        return cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                    else:
                        return image_array
                        
                except Exception as pil_error:
                    logger.warning(f"Échec chargement PIL: {pil_error}, tentative OpenCV...")
                    
                    # Méthode 2: Fallback avec cv2.imdecode pour tous OS
                    try:
                        # Lire le fichier en bytes puis décoder (cross-platform)
                        with open(file_path, 'rb') as f:
                            file_bytes = f.read()
                        
                        # Convertir bytes en array numpy
                        nparr = np.frombuffer(file_bytes, np.uint8)
                        
                        # Décoder l'image
                        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if image is not None:
                            return image
                        else:
                            logger.error(f"Impossible de décoder l'image: {file_path}")
                            return None
                            
                    except Exception as decode_error:
                        logger.error(f"Échec décodage OpenCV: {decode_error}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erreur chargement image: {e}")
            return None
    
    def _extract_text_ocr(self, image: np.ndarray) -> str:
        """Extrait le texte d'une image avec OCR ultra-robuste et multi-stratégies"""
        try:
            self._init_ocr()
            
            # Vérifier que l'image est valide
            if image is None:
                logger.error("Image None passée à l'OCR")
                return ""
            
            logger.info(f"🔍 OCR Ultra-robuste: Début extraction sur image {image.shape}")
            
            # === STRATÉGIE MULTI-PRÉPROCESSING ===
            processed_images = []
            
            # 1. Image originale convertie en RGB
            if len(image.shape) == 2:
                rgb_original = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif len(image.shape) == 3 and image.shape[2] == 3:
                rgb_original = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            elif len(image.shape) == 3 and image.shape[2] == 4:
                rgb_original = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            else:
                logger.error(f"Format d'image non supporté: {image.shape}")
                return ""
            
            processed_images.append(("Original", rgb_original))
            
            # 2. Amélioration du contraste adaptatif
            gray = cv2.cvtColor(rgb_original, cv2.COLOR_RGB2GRAY)
            
            # Égalisation d'histogramme CLAHE (plus doux que equalizeHist)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced_gray = clahe.apply(gray)
            enhanced_rgb = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2RGB)
            processed_images.append(("CLAHE Enhanced", enhanced_rgb))
            
            # 3. Débruitage avec préservation des détails
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            denoised_rgb = cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)
            processed_images.append(("Denoised", denoised_rgb))
            
            # 4. Morphologie pour améliorer la lisibilité du texte
            kernel = np.ones((1,1), np.uint8)
            morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            morph_rgb = cv2.cvtColor(morph, cv2.COLOR_GRAY2RGB)
            processed_images.append(("Morphology", morph_rgb))
            
            # 5. Binarisation adaptative pour texte faible contraste
            adaptive_thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            binary_rgb = cv2.cvtColor(adaptive_thresh, cv2.COLOR_GRAY2RGB)
            processed_images.append(("Adaptive Binary", binary_rgb))
            
            # 6. Si image très sombre/claire, ajustement gamma
            mean_brightness = np.mean(gray)
            if mean_brightness < 80 or mean_brightness > 180:
                gamma = 1.5 if mean_brightness < 80 else 0.7
                gamma_corrected = np.array(255 * (gray / 255) ** gamma, dtype='uint8')
                gamma_rgb = cv2.cvtColor(gamma_corrected, cv2.COLOR_GRAY2RGB)
                processed_images.append(("Gamma {:.1f}".format(gamma), gamma_rgb))
                logger.info(f"📊 Correction gamma {gamma:.1f} appliquée (luminosité: {mean_brightness:.1f})")
            
            # === EXTRACTION OCR MULTI-STRATÉGIES ===
            all_results = []
            confidence_threshold = 0.2  # Très permissif pour capturer plus de texte
            
            for strategy_name, processed_img in processed_images:
                try:
                    logger.debug(f"🔍 Tentative OCR: {strategy_name}")
                    
                    # EasyOCR avec paramètres optimaux pour extraction maximale
                    results = self.ocr_reader.readtext(
                        processed_img,
                        detail=1,           # Retourner bbox + confidence
                        paragraph=False,    # Traiter chaque ligne séparément
                        width_ths=0.7,      # Seuil largeur plus permissif
                        height_ths=0.7,     # Seuil hauteur plus permissif
                        decoder='greedy',   # Décodage greedy plus rapide
                        beamWidth=5,        # Largeur du faisceau pour plus de précision
                        batch_size=1        # Traitement par lot
                    )
                    
                    # Traiter chaque résultat
                    for result in results:
                        if len(result) >= 3:
                            bbox, text, confidence = result[0], result[1], result[2]
                            
                            # Filtrage intelligent du texte
                            clean_text = text.strip()
                            if len(clean_text) >= 1 and confidence > confidence_threshold:
                                # Nettoyer les caractères parasites mais garder la ponctuation
                                clean_text = re.sub(r'[^\w\s\.,;:!?\-()/@#€$%&+=*]', ' ', clean_text)
                                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                                
                                if clean_text:
                                    all_results.append({
                                        'text': clean_text,
                                        'confidence': confidence,
                                        'strategy': strategy_name,
                                        'bbox': bbox
                                    })
                                    logger.debug(f"✅ {strategy_name}: '{clean_text}' (conf: {confidence:.3f})")
                    
                    # Si cette stratégie a donné beaucoup de résultats, on peut s'arrêter
                    if len([r for r in all_results if r['strategy'] == strategy_name]) > 10:
                        logger.info(f"🎯 Stratégie {strategy_name} très productive, priorité donnée")
                        break
                        
                except Exception as strategy_error:
                    logger.warning(f"❌ Stratégie {strategy_name} échouée: {strategy_error}")
                    continue
            
            # === DÉDUPLICATION ET ASSEMBLAGE INTELLIGENT ===
            if not all_results:
                logger.warning("❌ Aucun texte extrait avec toutes les stratégies")
                return ""
            
            # Trier par confiance et position (top -> bottom, left -> right)
            def sort_key(r):
                bbox = r['bbox']
                # Calculer centre du rectangle
                center_y = (bbox[0][1] + bbox[2][1]) / 2
                center_x = (bbox[0][0] + bbox[2][0]) / 2
                # Priorité: confiance élevée + position lecture naturelle
                return (-r['confidence'], center_y, center_x)
            
            all_results.sort(key=sort_key)
            
            # Déduplication basée sur similarité de texte
            unique_texts = []
            seen_texts = set()
            
            for result in all_results:
                text = result['text']
                text_normalized = re.sub(r'\s+', ' ', text.lower().strip())
                
                # Éviter les doublons exacts
                if text_normalized not in seen_texts and len(text_normalized) > 0:
                    unique_texts.append(text)
                    seen_texts.add(text_normalized)
                    
                    # Limiter pour éviter les textes trop longs
                    if len(unique_texts) > 100:  # Maximum 100 segments
                        break
            
            # Assemblage final avec espacement intelligent
            final_text = " ".join(unique_texts)
            
            # Nettoyage final
            final_text = re.sub(r'\s+', ' ', final_text).strip()
            
            # Métriques de performance
            total_extractions = len(all_results)
            unique_extractions = len(unique_texts)
            best_strategy = max(set(r['strategy'] for r in all_results), 
                              key=lambda s: len([r for r in all_results if r['strategy'] == s]))
            avg_confidence = sum(r['confidence'] for r in all_results) / len(all_results)
            
            logger.info(f"📊 OCR Ultra-robuste terminé:")
            logger.info(f"   • {total_extractions} extractions totales")
            logger.info(f"   • {unique_extractions} segments uniques")
            logger.info(f"   • {len(final_text)} caractères finaux")
            logger.info(f"   • Meilleure stratégie: {best_strategy}")
            logger.info(f"   • Confiance moyenne: {avg_confidence:.3f}")
            
            if len(final_text) == 0:
                logger.warning("⚠️ Texte final vide après traitement")
            else:
                logger.info(f"✅ Extraction réussie: '{final_text[:100]}{'...' if len(final_text) > 100 else ''}'")
            
            return final_text
            
        except Exception as e:
            logger.error(f"❌ Erreur OCR ultra-robuste: {e}")
            logger.error(f"Type image: {type(image)}, Shape: {getattr(image, 'shape', 'N/A')}")
            
            # Fallback ultime: OCR simple sur image originale
            try:
                logger.info("🔄 Fallback OCR simple...")
                if len(image.shape) == 3:
                    simple_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    simple_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                
                simple_results = self.ocr_reader.readtext(simple_rgb, detail=0)  # Texte seul
                return " ".join(simple_results) if simple_results else ""
                
            except Exception as fallback_error:
                logger.error(f"❌ Fallback OCR ultime échoué: {fallback_error}")
                return ""
    
    async def _analyze_with_llm(self, text: str, image_context: str = "") -> tuple[str, bool]:
        """
        Analyse complète avec LLM pour résumé ET détection de contenu sensible
        Retourne (summary, warning)
        """
        try:
            # Prompt INTELLIGENT qui enseigne le raisonnement sans donner les réponses
            print("🔍 Analyse LLM en cours de :", text)
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Tu es un EXPERT EN SÉCURITÉ DOCUMENTAIRE. Ta mission est d'analyser du texte OCR et détecter intelligemment les informations sensibles.

=== PRINCIPE DE RAISONNEMENT ===
Utilise ton intelligence pour identifier ce qui pourrait compromettre la vie privée, la sécurité financière, ou contenir du contenu inapproprié.

=== MÉTHODOLOGIE D'ANALYSE ===

🧠 RAISONNEMENT FINANCIER:
• Cherche des patterns de CARTES DE PAIEMENT (peu importe la marque/société)
• Séquences numériques longues qui ressemblent à des comptes/cartes
• Codes de sécurité, dates d'expiration associées
• Coordonnées bancaires de toute nature

🧠 RAISONNEMENT IDENTITÉ:
• Documents officiels d'identification personnelle
• Numéros gouvernementaux, administratifs, légaux
• Informations qui permettent d'identifier précisément une personne

🧠 RAISONNEMENT CONTACT:
• Moyens de communication personnels directs
• Coordonnées permettant de joindre quelqu'un
• Adresses physiques ou numériques privées

🧠 RAISONNEMENT MÉDICAL:
• Informations de santé personnelles
• Relations patient-médecin
• Données médicales confidentielles

🧠 RAISONNEMENT PROFESSIONNEL:
• Informations salariales ou financières personnelles
• Données marquées comme confidentielles/privées
• Secrets professionnels ou commerciaux

🧠 RAISONNEMENT CONTENU INAPPROPRIÉ:
• Contenu à caractère sexuel explicite
• Nudité ou semi-nudité
• Matériel pour adultes

=== APPROCHE INTELLIGENTE ===
• ANALYSE le contexte général du document
• RÉFLÉCHIS à l'impact potentiel si ces informations étaient exposées
• ÉVALUE si un individu pourrait être lésé par la divulgation
• CONSIDÈRE les aspects légaux et éthiques

=== RÈGLES DE PRUDENCE ===
• En cas de DOUTE → penche vers WARNING=TRUE (mieux prévenir)
• Informations publiques normales → WARNING=FALSE

=== RENFORCEMENT DU RAISONNEMENT ===
• Tu dois exercer un jugement rigoureux et nuancé, mais **ne jamais ignorer** les signaux faibles de sensibilité.
• Si tu détectes un document officiel identifiable (ex: passeport, carte d’identité, permis ....), même partiellement, **le warning doit être true**.
• Si tu détectes un nom + un identifiant personnel ou unique (ex: numéro, date, signature, email), considère cela comme **potentiellement sensible**.
• Même si les informations sont courtes, réfléchis au **contexte implicite** : à quoi sert ce document ? À qui pourrait-il nuire s’il était exposé ?
• Tu n’agis pas comme une règle fixe, mais comme un expert prudent qui **sait reconnaître un risque même subtil**.


=== QUALITÉ DU RÉSUMÉ ===
• Décris INTELLIGEMMENT le type de document
• Mentionne les éléments principaux sans les répéter exactement
• Si sensible: explique POURQUOI c'est préoccupant
• Reste factuel et professionnel

RÉPONDRE UNIQUEMENT EN JSON VALIDE:
{{"summary": "Résumé intelligent et contextuel du document", "warning": true/false}}

<|eot_id|><|start_header_id|>user<|end_header_id|>"""

            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,  # Très déterministe pour sécurité
                "max_tokens": 15000,   # Plus de tokens pour JSON complet sans troncature
                "top_p": 0.9,        # Focus sur tokens probables
                "frequency_penalty": 0.1,  # Éviter répétitions
                "stream": False,
                # Pas de stop token - on laisse le LLM finir le JSON
            }
            
            # Tentative connexion LLM local avec timeout réduit
            logger.info(f"🔗 Tentative connexion LLM: {self.llm_url}")
            response = requests.post(self.llm_url, json=payload, timeout=120)  # 2 minutes max
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result['choices'][0]['message']['content'].strip()
                
                # Parser la réponse JSON du LLM avec robustesse
                try:
                    print(f"🔍 Réponse LLM brute: '{llm_response[:200]}...'")
                    
                    # Nettoyer la réponse (enlever markdown si présent)
                    clean_response = llm_response.strip()
                    
                    # Extraire JSON entre { et } si présent dans du texte
                    import re
                    json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
                    if json_match:
                        clean_response = json_match.group(0)
                        print(f"🔧 JSON extrait: '{clean_response}'")
                    
                    # Nettoyer markdown
                    if "```json" in clean_response:
                        clean_response = clean_response.split("```json")[1].split("```")[0]
                    elif "```" in clean_response:
                        clean_response = clean_response.split("```")[1].split("```")[0]
                    
                    # Parser JSON directement - simple et efficace
                    llm_analysis = json.loads(clean_response.strip())
                    
                    summary = llm_analysis.get("summary", "Document analysé par LLM")
                    warning = llm_analysis.get("warning", False)
                    
                    print(f"✅ LLM JSON parsé: summary={len(summary)} chars, warning={warning}")
                    
                    logger.info(f"✅ LLM analyse: résumé={len(summary)} chars, warning={warning}")
                    return summary, warning
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Échec parsing JSON: {e}")
                    print(f"📄 Réponse complète: '{llm_response}'")
                    logger.warning(f"Erreur parsing JSON LLM: {e}")
                    logger.warning(f"Réponse brute: {llm_response[:200]}...")
                    return self._fallback_analysis(text, image_context)
                
            else:
                print(f"❌ LLM erreur HTTP {response.status_code}")
                logger.warning(f"LLM local indisponible (status: {response.status_code})")
                return self._fallback_analysis(text, image_context)
                
        except requests.exceptions.ConnectionError:
            print(f"❌ LLM non accessible (connexion)")
            logger.warning("🚫 LLM local non accessible - utilisation du fallback")
            logger.warning(f"   URL testée: {self.llm_url}")
            logger.warning("   Vérifiez que LM Studio (ou équivalent) est démarré")
            return self._fallback_analysis(text, image_context)
        except Exception as e:
            print(f"❌ Erreur LLM: {e}")
            logger.error(f"Erreur analyse LLM: {e}")
            return self._fallback_analysis(text, image_context)
    
    def _fallback_analysis(self, text: str, image_context: str = "") -> tuple[str, bool]:
        """
        Analyse de fallback simple mais efficace
        Retourne (summary, warning)
        """
        # Détection rapide de contenu sensible par mots-clés
        sensitive_keywords = [
            # Financier - ULTRA PRIORITÉ
            "carte bancaire", "carte de crédit", "carte bleue", "visa", "mastercard", 
            "american express", "amex", "iban", "bic", "rib", "compte", "banque",
            "crédit", "débit", "cvv", "cryptogramme",
            # Personnel
            "@", "email", "téléphone", "portable", "adresse", "domicile",
            # Officiel
            "passeport", "permis", "cni", "carte d'identité", "sécurité sociale", "identité", "naissance",
            # Médical
            "médical", "santé", "docteur", "patient", "ordonnance",
            # Professionnel sensible
            "salaire", "rémunération", "confidentiel", "privé", "personnel"
        ]
        
        text_lower = text.lower()
        warning = any(keyword in text_lower for keyword in sensitive_keywords)
        
        # Détection patterns numériques suspects
        if re.search(r'\b\d{16}\b', text):  # 16 chiffres = carte bancaire
            warning = True
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):  # Email
            warning = True
        if re.search(r'\b(?:\+33|0)[1-9](?:[0-9]{8})\b', text):  # Téléphone français
            warning = True
        
        # Génération résumé simple
        if not text.strip():
            if "NSFW" in image_context:
                summary = "Document visuel contenant du contenu potentiellement sensible. Aucun texte détecté."
                warning = True
            else:
                summary = "Document visuel sans texte détectable. Image analysée avec succès."
        else:
            # Résumé basique intelligent
            if len(text) > 100:
                first_sentences = '. '.join(text.split('.')[:2]) + '.'
                summary = f"Document contenant du texte analysé. {first_sentences[:150]}..."
            else:
                summary = f"Document court analysé: {text[:100]}..."
            
            if warning:
                summary += " Attention: informations sensibles détectées."
        
        logger.info(f"📋 Fallback analyse: warning={warning}")
        return summary, warning
    
    async def _detect_visual_pii(self, image: np.ndarray, cached_text: str = "") -> List[str]:
        """
        Détection visuelle simple - garde juste NSFW
        Le LLM s'occupe du reste !
        """
        visual_pii = []
        
        try:
            # Juste la détection NSFW rapide
            is_nsfw = await self._detect_nsfw_content_fast(image)
            if is_nsfw:
                visual_pii.append("NSFW_CONTENT")
                logger.warning("🚨 Contenu NSFW détecté")
            
        except Exception as e:
            logger.error(f"❌ Erreur détection visuelle: {e}")
        
        return visual_pii
    
    async def _detect_nsfw_content_fast(self, image: np.ndarray) -> bool:
        """
        Utilise le NSFWDetector ONNX développé - BIEN MEILLEUR que l'analyse couleur !
        Retourne True si score NSFW > 0.6
        """
        try:
            # Utiliser le détecteur ONNX sophistiqué déjà développé
            nsfw_score = await nsfw_detector.predict_nsfw_score(image)
            
            # Seuil de détection (0.6 = assez strict)
            nsfw_threshold = 0.6
            is_nsfw = nsfw_score > nsfw_threshold
            
            logger.info(f"🔍 NSFW ONNX: score={nsfw_score:.3f} (seuil: {nsfw_threshold}) → {'⚠️ NSFW' if is_nsfw else '✅ Safe'}")
            
            return is_nsfw
            
        except Exception as e:
            logger.warning(f"❌ Erreur NSFWDetector ONNX: {e}")
            logger.info("🔄 Fallback: détection couleur basique")
            
            # Fallback simple si le modèle ONNX échoue
            return await self._detect_nsfw_fallback_color(image)
    
    async def _detect_nsfw_fallback_color(self, image: np.ndarray) -> bool:
        """
        Fallback basique par couleur si le modèle ONNX échoue
        """
        try:
            # CORRECTION: Gérer les images en niveaux de gris
            if len(image.shape) == 2:
                # Image déjà en niveaux de gris, convertir en BGR d'abord
                bgr_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif len(image.shape) == 3 and image.shape[2] == 3:
                # Image BGR standard
                bgr_image = image
            else:
                logger.warning(f"Format d'image non supporté pour NSFW fallback: {image.shape}")
                return False
            
            # Conversion en HSV pour détection de peau
            hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
            
            # Plages de couleurs pour tons chair
            skin_ranges = [
                ([0, 48, 80], [20, 255, 255]),      # Teint clair
                ([0, 50, 50], [15, 200, 200]),      # Teint moyen  
            ]
            
            total_skin_pixels = 0
            total_pixels = image.shape[0] * image.shape[1]
            
            for lower, upper in skin_ranges:
                lower_skin = np.array(lower, dtype=np.uint8)
                upper_skin = np.array(upper, dtype=np.uint8)
                
                skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
                skin_pixels = np.sum(skin_mask > 0)
                total_skin_pixels += skin_pixels
            
            # Éviter le double comptage
            total_skin_pixels = min(total_skin_pixels, total_pixels)
            skin_ratio = total_skin_pixels / total_pixels
            
            # Seuil fallback
            fallback_threshold = 0.75
            is_nsfw_fallback = skin_ratio > fallback_threshold
            
            logger.debug(f"🔍 NSFW Fallback: {skin_ratio:.2%} (seuil: {fallback_threshold:.0%}) → {'⚠️ NSFW' if is_nsfw_fallback else '✅ Safe'}")
            
            return is_nsfw_fallback
            
        except Exception as e:
            logger.error(f"❌ Erreur détection NSFW fallback: {e}")
            return False
    

    
    async def analyze_document(self, args: VisionArgs) -> VisionResponse:
        """
        Pipeline INTELLIGENT d'analyse d'image avec détection automatique des capacités
        
        FLUX ADAPTATIF:
        1. Test des capacités Vision du LLM 
        2a. Si LLM Vision → Analyse directe complète
        2b. Si LLM texte seulement → OCR + Analyse textuelle
        3. Retour JSON unifié: filepath, summary, warning
        """
        start_time = time.time()
        print(f"\n🚀 === DÉBUT ANALYSE VISION AGENT INTELLIGENT ===")
        print(f"📂 Fichier: {args.path}")
        logger.info(f"🔍 Début analyse adaptative: {args.path}")
        
        try:
            # === 1. CHARGEMENT IMAGE ===
            print(f"\n📸 ÉTAPE 1: Chargement de l'image")
            image = self._load_image(args.path, args.image_bytes)
            if image is None:
                print(f"❌ ÉCHEC: Impossible de charger l'image")
                return VisionResponse(
                    filepath=args.path,
                    summary="Impossible de charger l'image - format non supporté ou fichier corrompu",
                    warning=False
                )
            
            print(f"✅ SUCCÈS: Image chargée - Dimensions: {image.shape}")
            logger.info(f"📸 Image chargée: {image.shape}")
            
            # === 2. DÉTECTION DES CAPACITÉS LLM ===
            print(f"\n🧠 ÉTAPE 2: Détection des capacités du modèle")
            
            # Test connectivité basique
            if not self.test_llm_connection():
                print(f"❌ LLM non connecté - Mode fallback complet")
                summary, warning = self._fallback_analysis("", f"Image {image.shape}")
                processing_time = time.time() - start_time
                
                result = VisionResponse(
                    filepath=args.path,
                    summary=summary,
                    warning=warning
                )
                
                print(f"\n🎯 === RÉSULTAT FALLBACK ===")
                print(f"📁 Filepath: {result.filepath}")
                print(f"📄 Summary: {result.summary}")
                print(f"⚠️ Warning: {result.warning}")
                print(f"⌚ Temps: {processing_time:.2f}s")
                return result
            
            # Test capacités Vision
            print(f"🔍 Test des capacités Vision du LLM...")
            has_vision = self.test_llm_vision_capability()
            
            if has_vision:
                # === FLUX A: LLM VISION DIRECT ===
                print(f"✅ LLM VISION DÉTECTÉ: Analyse directe complète!")
                print(f"🎯 Mode: Vision LLM (optimal)")
                
                try:
                    summary, warning = await self._analyze_image_with_vision_llm(image, args.path)
                    print(f"✅ ANALYSE VISION LLM RÉUSSIE")
                    
                    processing_time = time.time() - start_time
                    result = VisionResponse(
                        filepath=args.path,
                        summary=summary,
                        warning=warning
                    )
                    
                    print(f"\n🎯 === RÉSULTAT VISION LLM ===")
                    print(f"📁 Filepath: {result.filepath}")
                    print(f"📄 Summary: {result.summary}")
                    print(f"⚠️ Warning: {result.warning}")
                    print(f"⌚ Temps: {processing_time:.2f}s")
                    print(f"🏁 === FIN ANALYSE VISION ===\n")
                    
                    logger.info(f"🎯 Vision LLM terminé en {processing_time:.2f}s")
                    return result
                    
                except Exception as vision_error:
                    print(f"❌ Vision LLM échoué: {vision_error}")
                    print(f"🔄 Fallback vers OCR classique...")
                    logger.warning(f"Vision LLM échec, fallback OCR: {vision_error}")
                    # Continuer vers flux OCR
            
            else:
                print(f"📝 LLM TEXTE SEULEMENT: Mode OCR classique")
                print(f"🎯 Mode: OCR + LLM textuel")
            
            # === FLUX B: OCR CLASSIQUE + LLM TEXTUEL ===
            print(f"\n📝 ÉTAPE 3: Extraction OCR du texte")
            extracted_text = self._extract_text_ocr(image)
            text_length = len(extracted_text)
            print(f"✅ SUCCÈS: OCR terminé - {text_length} caractères extraits")
            if text_length > 0:
                print(f"📋 Aperçu texte: '{extracted_text[:100]}{'...' if len(extracted_text) > 100 else ''}'")
            else:
                print(f"⚠️ Aucun texte détecté dans l'image")
            logger.info(f"📝 OCR: {text_length} caractères extraits")
            
            # === CONTEXTE VISUEL ===
            print(f"\n🖼️ ÉTAPE 4: Préparation du contexte visuel")
            image_context = f"Image {image.shape[1]}x{image.shape[0]} pixels"
            if text_length == 0:
                image_context += ", aucun texte détecté"
            else:
                image_context += f", {text_length} caractères de texte"
            
            # Détection NSFW
            try:
                is_nsfw = await self._detect_nsfw_content_fast(image)
                if is_nsfw:
                    image_context += ", contenu NSFW potentiel détecté"
                    print(f"⚠️ Détection NSFW: Potentiel contenu sensible")
                else:
                    print(f"✅ Détection NSFW: Contenu sûr")
            except:
                print(f"⚠️ Détection NSFW: Échec (pas critique)")
                pass
            
            print(f"📊 Contexte final: {image_context}")
            
            # === ANALYSE LLM TEXTUEL ===
            print(f"\n🧠 ÉTAPE 5: Analyse LLM textuelle")
            
            if text_length > 0:
                print(f"📝 Analyse du texte extrait...")
                summary, warning = await self._analyze_with_llm(extracted_text, image_context)
                print(f"✅ ANALYSE LLM TEXTUEL RÉUSSIE")
            else:
                print(f"📝 Pas de texte → Analyse fallback")
                summary, warning = self._fallback_analysis(extracted_text, image_context)
                print(f"⚠️ ANALYSE FALLBACK UTILISÉE")
            
            # === RÉSULTAT FINAL ===
            processing_time = time.time() - start_time
            result = VisionResponse(
                filepath=args.path,
                summary=summary,
                warning=warning
            )
            
            print(f"\n🎯 === RÉSULTAT FINAL OCR+LLM ===")
            print(f"📁 Filepath: {result.filepath}")
            print(f"📄 Summary: {result.summary}")
            print(f"⚠️ Warning: {result.warning}")
            print(f"⌚ Temps: {processing_time:.2f}s")
            print(f"🏁 === FIN ANALYSE ===\n")
            
            logger.info(f"📊 OCR+LLM terminé en {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Erreur analyse: {str(e)}"
            print(f"\n❌ ERREUR CRITIQUE: {error_msg}")
            print(f"⌚ Temps avant erreur: {processing_time:.2f}s")
            logger.error(f"❌ {error_msg} (après {processing_time:.2f}s)")
            
            return VisionResponse(
                filepath=args.path,
                summary=error_msg,
                warning=False
            )
    
    async def _analyze_image_with_vision_llm(self, image: np.ndarray, file_path: str) -> Tuple[str, bool]:
        """
        Analyse directe d'image avec LLM Vision (multimodal)
        Retourne (summary, warning)
        """
        try:
            import base64
            
            # Encoder l'image en base64
            _, buffer = cv2.imencode('.jpg', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Prompt pour analyse vision directe
            vision_payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analysez cette image et déterminez si elle contient des informations sensibles ou privées.

TYPES D'INFORMATIONS SENSIBLES À DÉTECTER:
- Documents d'identité (passeports, cartes d'identité, permis de conduire)
- Informations bancaires (cartes de crédit, chèques, relevés bancaires)
- Informations médicales (ordonnances, résultats médicaux)
- Informations personnelles (adresses, numéros de téléphone visibles)
- Contenu inapproprié ou NSFW

RÉPONDEZ UNIQUEMENT EN JSON:
{
  "summary": "Description courte de ce qui est visible dans l'image",
  "warning": true/false
}

Si warning=true, expliquez brièvement pourquoi dans le summary."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            response = requests.post(self.llm_url, json=vision_payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result['choices'][0]['message']['content'].strip()
                
                # Parser le JSON
                try:
                    import re
                    json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                    if json_match:
                        llm_analysis = json.loads(json_match.group(0))
                        summary = llm_analysis.get("summary", "Image analysée par Vision LLM")
                        warning = llm_analysis.get("warning", False)
                        
                        logger.info(f"✅ Vision LLM: {summary[:50]}... warning={warning}")
                        return summary, warning
                    else:
                        logger.warning("JSON non trouvé dans la réponse Vision LLM")
                        return self._fallback_analysis("", f"Vision LLM: {llm_response[:100]}")
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Erreur parsing JSON Vision LLM: {e}")
                    return self._fallback_analysis("", f"Vision LLM: {llm_response[:100]}")
            else:
                logger.warning(f"Vision LLM erreur HTTP {response.status_code}")
                return self._fallback_analysis("", "Vision LLM non disponible")
                
        except Exception as e:
            logger.error(f"Erreur Vision LLM: {e}")
            return self._fallback_analysis("", "Erreur Vision LLM")

# === AGENT ET TOOL CORAL ===

class Agent:
    """Classe Agent pour compatibilité avec Coral"""
    def __init__(self, name: str, description: str, tools: List):
        self.name = name
        self.description = description
        self.tools = tools

# Instance globale de l'agent
vision_agent_instance = VisionAgent()

# Cache global pour EasyOCR (partagé entre toutes les instances)
_global_ocr_reader = None

def get_global_ocr_reader():
    """Récupère l'instance OCR globale (singleton)"""
    global _global_ocr_reader
    if _global_ocr_reader is None:
        logger.info("Initialisation EasyOCR globale...")
        import warnings
        warnings.filterwarnings("ignore", category=FutureWarning)
        
        _global_ocr_reader = easyocr.Reader(
            ['fr', 'en'], 
            gpu=False,
            verbose=False,
            download_enabled=True
        )
        logger.info("EasyOCR global initialisé")
    
    return _global_ocr_reader

# Agent Coral
vision_agent = Agent(
    name="vision",
    description="Agent d'analyse de fichiers images avec détection PII avancée - 100% offline",
    tools=["analyze_document"]
)

# Tool function pour Coral (entrée principale)
async def analyze_document(args: VisionArgs) -> VisionResponse:
    """
    Tool Coral pour analyser une image avec LLM intelligent
    
    Args:
        args.path: Chemin vers le fichier image
        args.image_bytes: Données binaires optionnelles (fallback)
    
    Returns:
        VisionResponse: JSON simple avec filepath, summary, warning
    """
    return await vision_agent_instance.analyze_document(args)

# === TESTS ET DÉMONSTRATION ===

if __name__ == "__main__":
    # === DIAGNOSTIC SYSTÈME AUTOMATIQUE AU DÉMARRAGE ===
    print("🔧 Vérification des dépendances système...")
    system_ready = diagnose_system_dependencies()
    
    if not system_ready:
        print("\n⚠️ ATTENTION: Des dépendances manquent. Veuillez les installer avant de continuer.")
        print("L'agent peut fonctionner partiellement, mais certaines fonctionnalités pourraient échouer.\n")
    else:
        print("\n🎉 Système optimal détecté ! Agent Vision prêt à fonctionner.\n")
    
    async def test_vision_llm():
        """
        Test de l'agent Vision avec LLM intelligent
        """
        print("🤖 Test Agent Vision LLM - 3 attributs JSON")
        print("=" * 45)
        
        # === TEST 1: DOCUMENT AVEC CONTENU SENSIBLE ===
        print("\n📋 Test 1: Document potentiellement sensible")
        
        # Créer image test avec du texte sensible
        test_image = np.zeros((300, 400, 3), dtype=np.uint8)
        test_image.fill(255)  # Fond blanc
        
        # Ajouter du texte sensible simulé
        cv2.putText(test_image, "CARTE BANCAIRE", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(test_image, "4532 1234 5678 9012", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(test_image, "john.doe@email.com", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(test_image, "06 12 34 56 78", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Utiliser Path pour cross-platform
        test_file = Path("test_sensitive.jpg")
        cv2.imwrite(str(test_file), test_image)
        
        if test_file.exists():
            args = VisionArgs(path=str(test_file.resolve()))
            result = await analyze_document(args)
            
            print(f"📁 Filepath: {result.filepath}")
            print(f"📄 Summary: {result.summary}")
            print(f"⚠️  Warning: {result.warning}")
            print(f"🎯 JSON: {result.dict()}")
        else:
            print("❌ Impossible de créer l'image de test")
        
        # === TEST 2: DOCUMENT NORMAL ===
        print("\n📋 Test 2: Document normal (pas sensible)")
        
        normal_image = np.zeros((200, 300, 3), dtype=np.uint8)
        normal_image.fill(240)  # Fond gris clair
        cv2.putText(normal_image, "FACTURE NORMALE", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(normal_image, "Produit: Livre", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(normal_image, "Prix: 15.99 EUR", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(normal_image, "Date: 01/01/2025", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Utiliser Path pour cross-platform
        normal_file = Path("test_normal.jpg")
        cv2.imwrite(str(normal_file), normal_image)
        
        if normal_file.exists():
            args = VisionArgs(path=str(normal_file.resolve()))
            result = await analyze_document(args)
            
            print(f"📁 Filepath: {result.filepath}")
            print(f"� Summary: {result.summary}")
            print(f"⚠️  Warning: {result.warning}")
            print(f"🎯 JSON: {result.dict()}")
        
        # === TEST 3: IMAGE SANS TEXTE ===
        print("\n📋 Test 3: Image sans texte")
        
        empty_image = np.random.randint(0, 255, (150, 200, 3), dtype=np.uint8)
        
        # Utiliser Path pour cross-platform
        empty_file = Path("test_empty.jpg")
        cv2.imwrite(str(empty_file), empty_image)
        
        if empty_file.exists():
            args = VisionArgs(path=str(empty_file.resolve()))
            result = await analyze_document(args)
            
            print(f"� Filepath: {result.filepath}")
            print(f"📄 Summary: {result.summary}")
            print(f"⚠️  Warning: {result.warning}")
            print(f"🎯 JSON: {result.dict()}")
        
        print(f"\n🎯 Test terminé ! LLM fait toute l'intelligence 🧠")
    
    # Lancer les tests
    asyncio.run(test_vision_llm())