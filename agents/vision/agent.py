#!/usr/bin/env python3
"""
Agent Vision pour Neurosort - Analyse de fichiers visuels avec détection PII avancée
Hackathon Qualcomm Edge-AI - 100% offline

Pipeline complet:
- OCR multilangue (EasyOCR)
- Détection PII textuelle (email, téléphone, carte bancaire, IBAN, SSN)
- Détection PII visuelle (cartes bancaires, documents d'identité, contenu NSFW)
- Résumé intelligent avec LLama-3 local
- Extraction de tags sémantiques pour indexation
"""

import asyncio
import cv2
import easyocr
import logging
import numpy as np
import re
import requests
from io import BytesIO
from pathlib import Path
from PIL import Image
from pydantic import BaseModel
from typing import List, Optional, Tuple
import json
import time
import threading

# Import ONNX pour détection NSFW
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    ort = None

# Import PDF support
try:
    import pdf2image
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    pdf2image = None

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
    bytes: Optional[bytes] = None
    extract_pages: Optional[List[int]] = None  # Pages spécifiques pour PDF

class PIISpan(BaseModel):
    """Position d'une entité PII détectée dans le texte"""
    start: int
    end: int
    label: str

class FileMeta(BaseModel):
    """Métadonnées complètes d'un fichier analysé"""
    path: str
    source: str = "vision"
    text: str = ""
    summary: str = ""
    tags: List[str] = []
    pii_detected: bool = False
    pii_types: List[str] = []
    pii_spans: List[PIISpan] = []
    status: str = "ok"
    pages_processed: int = 0  # Nombre de pages traitées (PDF)
    file_type: str = "image"  # "image" ou "pdf"

class NSFWDetector:
    """
    Détecteur NSFW embarqué utilisant un modèle ONNX local
    Chargement paresseux pour optimiser la mémoire
    """
    
    def __init__(self, model_path: str = "ai_models/nsfw/nsfw_model.onnx"):
        self.model_path = Path(model_path)
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

class VisionAgent:
    """Agent Vision pour analyse de documents visuels"""
    
    def __init__(self):
        """Initialise l'agent avec les modèles nécessaires"""
        self.ocr_reader = None
        self.nsfw_model = None
        self.llm_url = "http://localhost:1234/v1/chat/completions"  # LM Studio local
        
        # Patterns PII pour détection textuelle
        self.pii_patterns = {
            "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "PHONE": re.compile(r'\b(?:\+33|0)[1-9](?:[0-9]{8})\b'),
            "CARD_NUMBER": re.compile(r'\b(?:\d{4}[\s-]?){3}\d{4}\b'),
            "IBAN": re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}[A-Z0-9]{1,16}\b'),
            "SSN": re.compile(r'\b\d{13}\b'),  # Numéro de sécurité sociale français
        }
        
        logger.info("Agent Vision initialisé")
    
    def _init_ocr(self):
        """Initialise EasyOCR de manière lazy"""
        if self.ocr_reader is None:
            logger.info("Initialisation EasyOCR...")
            self.ocr_reader = easyocr.Reader(['fr', 'en'], gpu=False)
            logger.info("EasyOCR initialisé")
    
    def _load_image(self, path: str, bytes_data: Optional[bytes] = None) -> Optional[np.ndarray]:
        """Charge une image depuis un chemin ou des bytes"""
        try:
            if bytes_data:
                # Charger depuis bytes
                image = Image.open(BytesIO(bytes_data))
                return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                # Charger depuis fichier
                if not Path(path).exists():
                    logger.error(f"Fichier non trouvé: {path}")
                    return None
                return cv2.imread(path)
        except Exception as e:
            logger.error(f"Erreur chargement image: {e}")
            return None
    
    def _is_pdf(self, path: str) -> bool:
        """Vérifie si le fichier est un PDF"""
        return Path(path).suffix.lower() == '.pdf'
    
    def _convert_pdf_to_images(self, pdf_path: str, extract_pages: Optional[List[int]] = None) -> List[np.ndarray]:
        """
        Convertit un PDF en liste d'images
        
        Args:
            pdf_path: Chemin vers le PDF
            extract_pages: Pages spécifiques à extraire (1-indexé), None = toutes
            
        Returns:
            Liste des images (format OpenCV)
        """
        if not PDF_AVAILABLE:
            logger.error("❌ pdf2image non disponible - installez avec: pip install pdf2image")
            return []
        
        try:
            logger.info(f"📄 Conversion PDF en cours: {pdf_path}")
            
            # Paramètres de conversion optimisés
            conversion_params = {
                'dpi': 200,  # Balance qualité/vitesse
                'fmt': 'RGB',
                'thread_count': 2,
                'use_pdftocairo': True  # Meilleure qualité si disponible
            }
            
            # Extraire pages spécifiques ou toutes
            if extract_pages:
                # Convertir en index 0-based pour pdf2image
                first_page = min(extract_pages)
                last_page = max(extract_pages)
                conversion_params.update({
                    'first_page': first_page,
                    'last_page': last_page
                })
                logger.info(f"📄 Extraction pages {first_page}-{last_page}")
            
            # Conversion PDF → PIL Images
            pil_images = pdf2image.convert_from_path(pdf_path, **conversion_params)
            
            # Filtrer les pages si nécessaire
            if extract_pages and len(extract_pages) < len(pil_images):
                filtered_images = []
                for page_num in extract_pages:
                    page_index = page_num - 1  # Convertir en index 0-based
                    if 0 <= page_index < len(pil_images):
                        filtered_images.append(pil_images[page_index])
                pil_images = filtered_images
            
            # Convertir PIL → OpenCV
            opencv_images = []
            for i, pil_img in enumerate(pil_images):
                # PIL RGB → OpenCV BGR
                opencv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                opencv_images.append(opencv_img)
            
            logger.info(f"✅ PDF converti: {len(opencv_images)} pages")
            return opencv_images
            
        except Exception as e:
            logger.error(f"❌ Erreur conversion PDF: {e}")
            return []
    
    def _extract_text_ocr(self, image: np.ndarray) -> str:
        """Extrait le texte d'une image avec OCR"""
        try:
            self._init_ocr()
            
            # EasyOCR
            results = self.ocr_reader.readtext(image)
            
            # Concaténer tout le texte détecté
            text_parts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Seuil de confiance
                    text_parts.append(text)
            
            full_text = " ".join(text_parts)
            logger.info(f"OCR extrait {len(full_text)} caractères")
            return full_text
            
        except Exception as e:
            logger.error(f"Erreur OCR: {e}")
            return ""
    
    def _detect_text_pii(self, text: str) -> tuple[bool, List[str], List[PIISpan]]:
        """Détecte les PII dans le texte"""
        pii_detected = False
        pii_types = []
        pii_spans = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = list(pattern.finditer(text))
            if matches:
                pii_detected = True
                pii_types.append(pii_type)
                
                for match in matches:
                    pii_spans.append(PIISpan(
                        start=match.start(),
                        end=match.end(),
                        label=pii_type
                    ))
        
        return pii_detected, pii_types, pii_spans
    
    async def _detect_visual_pii(self, image: np.ndarray) -> List[str]:
        """
        Détecte les PII visuels avancés:
        - CARD_PHOTO: carte bancaire (logos + 16 chiffres)
        - ID_DOC: passeport/carte d'identité (MRZ)
        - NUDITY: contenu NSFW (modèle ONNX + fallback)
        """
        visual_pii = []
        
        try:
            # === 1. DÉTECTION CARTE BANCAIRE ===
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Recherche de contours rectangulaires (forme carte)
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Approximation polygonale
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Vérifier si c'est un rectangle de taille carte bancaire
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    area = cv2.contourArea(contour)
                    
                    # Ratio typique carte bancaire: 1.586 (ISO/IEC 7810 ID-1)
                    if 1.4 < aspect_ratio < 1.8 and area > 5000:
                        # Extraire la zone et chercher des patterns carte
                        roi = image[y:y+h, x:x+w] if y+h <= image.shape[0] and x+w <= image.shape[1] else None
                        
                        if roi is not None:
                            roi_text = self._extract_text_ocr(roi)
                            
                            # Recherche pattern carte (16 chiffres) + logos possibles
                            if (self.pii_patterns["CARD_NUMBER"].search(roi_text) or
                                re.search(r'VISA|MASTERCARD|AMERICAN EXPRESS', roi_text.upper())):
                                visual_pii.append("CARD_PHOTO")
                                logger.info("💳 Carte bancaire détectée dans l'image")
                                break
            
            # === 2. DÉTECTION DOCUMENT D'IDENTITÉ ===
            # Recherche de motifs MRZ (Machine Readable Zone)
            full_text = self._extract_text_ocr(image)
            
            # Pattern MRZ passeport français: P<FRA... (44 caractères)
            # Pattern MRZ carte ID: I<FRA... (30 caractères)
            mrz_patterns = [
                r'P<[A-Z]{3}[A-Z0-9<]{41}',  # Passeport
                r'I[A-Z]<[A-Z]{3}[A-Z0-9<]{27}',  # Carte ID
                r'[A-Z]{9}[0-9][A-Z]{3}[0-9]{7}[A-Z][0-9]{7}[A-Z0-9<]{14}[0-9]{2}'  # MRZ ligne 2
            ]
            
            for pattern in mrz_patterns:
                if re.search(pattern, full_text.replace(' ', '')):
                    visual_pii.append("ID_DOC")
                    logger.info("🆔 Document d'identité détecté (MRZ)")
                    break
            
            # === 3. DÉTECTION CONTENU NSFW ===
            is_nsfw = await self._detect_nsfw_content(image)
            if is_nsfw:
                visual_pii.append("NUDITY")
                logger.warning("🚨 Contenu NSFW détecté - classification confidentielle")
            
        except Exception as e:
            logger.error(f"❌ Erreur détection PII visuel: {e}")
        
        return visual_pii
    
    async def _detect_nsfw_content(self, image: np.ndarray) -> bool:
        """
        Détecte le contenu NSFW avec modèle ONNX embarqué
        Retourne True si score NSFW > 0.85
        Fallback intelligent si modèle indisponible
        """
        try:
            # === 1. TENTATIVE AVEC MODÈLE ONNX ===
            nsfw_score = await nsfw_detector.predict_nsfw_score(image)
            
            # Seuil strict: 85% comme demandé
            nsfw_threshold = 0.85
            is_nsfw = nsfw_score > nsfw_threshold
            
            logger.info(f"🔍 Score NSFW ONNX: {nsfw_score:.3f} (seuil: {nsfw_threshold:.2f}) → {'⚠️ NSFW' if is_nsfw else '✅ Safe'}")
            
            # Si le modèle a fonctionné, utiliser son résultat
            if nsfw_score > 0.001:  # Score non-null = modèle a fonctionné
                return is_nsfw
            
            # === 2. FALLBACK: DÉTECTION DE PEAU ===
            logger.info("🔄 Fallback: analyse des tons chair")
            
            # Conversion en HSV pour meilleure détection de peau
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Plages de couleurs pour tons chair (plus précises)
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
            
            # Seuil fallback plus conservateur (70% pour éviter faux positifs)
            fallback_threshold = 0.70
            is_nsfw_fallback = skin_ratio > fallback_threshold
            
            logger.info(f"🔍 Fallback tons chair: {skin_ratio:.2%} (seuil: {fallback_threshold:.0%}) → {'⚠️ NSFW' if is_nsfw_fallback else '✅ Safe'}")
            
            return is_nsfw_fallback
            
        except Exception as e:
            logger.error(f"❌ Erreur détection NSFW: {e}")
            return False  # En cas d'erreur, considérer comme safe
    
    async def _generate_summary(self, text: str, visual_context: str = "") -> str:
        """
        Génère un résumé intelligent avec LLama-3 local (4-7 phrases max)
        Fallback automatique si LLM indisponible
        """
        try:
            # Construire un prompt optimisé pour Llama-3
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Tu es un assistant qui analyse des documents. Génère un résumé concis en français, 4 à 7 phrases maximum, clair et professionnel.
<|eot_id|><|start_header_id|>user<|end_header_id|>

Document à analyser:
Texte OCR: {text[:800]}...
Contexte: {visual_context}

Résumé (4-7 phrases max):
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

            payload = {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 300,
                "stream": False
            }
            
            # Tentative connexion LLM local
            response = requests.post(self.llm_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                summary = result['choices'][0]['message']['content'].strip()
                
                # Nettoyer le résumé (enlever les tags potentiels)
                summary = re.sub(r'<\|.*?\|>', '', summary).strip()
                
                # Vérifier la longueur (max 7 phrases)
                sentences = summary.split('.')
                if len(sentences) > 7:
                    summary = '. '.join(sentences[:7]) + '.'
                
                logger.info("Résumé généré par LLM local")
                return summary
            else:
                logger.warning(f"LLM local indisponible (status: {response.status_code})")
                return self._fallback_summary(text, visual_context)
                
        except requests.exceptions.ConnectionError:
            logger.warning("LLM local non accessible - utilisation du fallback")
            return self._fallback_summary(text, visual_context)
        except Exception as e:
            logger.error(f"Erreur génération résumé LLM: {e}")
            return self._fallback_summary(text, visual_context)
    
    def _fallback_summary(self, text: str, visual_context: str = "") -> str:
        """
        Résumé de fallback intelligent sans LLM
        Génère 4-6 phrases structurées basées sur l'analyse du contenu
        """
        if not text.strip():
            if "PII détectés" in visual_context:
                return "Document visuel contenant des informations sensibles détectées. Aucun texte lisible extrait par OCR. Traitement avec précaution recommandé."
            return "Document visuel sans texte détectable par OCR. Format image analysé avec succès."
        
        # Analyse basique du contenu pour classification
        text_lower = text.lower()
        doc_type = "document"
        
        # Classification automatique
        if any(word in text_lower for word in ["facture", "invoice", "montant", "tva", "total"]):
            doc_type = "facture"
        elif any(word in text_lower for word in ["contrat", "accord", "conditions", "signature"]):
            doc_type = "contrat"
        elif any(word in text_lower for word in ["carte", "card", "visa", "mastercard"]):
            doc_type = "carte bancaire"
        elif any(word in text_lower for word in ["passeport", "passport", "identité", "identity"]):
            doc_type = "document d'identité"
        elif any(word in text_lower for word in ["certificat", "diplôme", "attestation"]):
            doc_type = "certificat"
        
        # Extraire des informations clés
        key_info = []
        
        # Recherche de montants
        amounts = re.findall(r'(\d+[,.]?\d*)\s*€?', text)
        if amounts:
            key_info.append(f"montant principal: {amounts[0]}€")
        
        # Recherche de dates
        dates = re.findall(r'\b(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})\b', text)
        if dates:
            key_info.append(f"date: {dates[0]}")
        
        # Recherche de noms (mots en majuscules)
        names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text)
        if names:
            key_info.append(f"nom: {names[0]}")
        
        # Construction du résumé structuré
        summary_parts = []
        
        # Phrase 1: Type et identification
        summary_parts.append(f"Document de type {doc_type} analysé avec succès.")
        
        # Phrase 2: Contenu principal
        if len(text) > 100:
            first_part = text[:150].split('.')[-2] if '.' in text[:150] else text[:100]
            summary_parts.append(f"Contenu principal: {first_part.strip()}.")
        
        # Phrase 3: Informations clés
        if key_info:
            summary_parts.append(f"Informations extraites: {', '.join(key_info)}.")
        
        # Phrase 4: Contexte visuel
        if visual_context and "PII détectés" in visual_context:
            summary_parts.append("Attention: informations sensibles détectées dans ce document.")
        
        # Phrase 5: Statut OCR
        if len(text) > 50:
            summary_parts.append(f"Extraction de texte réussie ({len(text)} caractères).")
        
        # Limiter à 6 phrases max
        final_summary = ' '.join(summary_parts[:6])
        
        logger.info("Résumé généré par fallback intelligent")
        return final_summary
    
    def _extract_tags(self, summary: str, pii_types: List[str], extracted_text: str = "") -> List[str]:
        """
        Extrait 3-8 tags sémantiques pertinents pour l'indexation et le File Manager
        Combine les PII détectés, l'analyse du résumé et du texte OCR
        """
        tags = set()
        
        # === 1. TAGS BASÉS SUR LES PII DÉTECTÉS ===
        pii_tag_mapping = {
            "CARD_NUMBER": "banque",
            "CARD_PHOTO": "banque", 
            "EMAIL": "contact",
            "PHONE": "contact",
            "IBAN": "banque",
            "SSN": "administratif",
            "ID_DOC": "identité",
            "NUDITY": "confidentiel"
        }
        
        for pii_type in pii_types:
            if pii_type in pii_tag_mapping:
                tags.add(pii_tag_mapping[pii_type])
        
        # === 2. TAGS SÉMANTIQUES DEPUIS LE RÉSUMÉ ===
        combined_text = f"{summary} {extracted_text}".lower()
        
        # Catégories documentaires
        document_keywords = {
            # Finances
            "banque": ["banque", "carte", "credit", "debit", "compte", "iban", "virement"],
            "facture": ["facture", "invoice", "montant", "tva", "total", "paiement", "due"],
            "assurance": ["assurance", "police", "sinistre", "garantie", "prime", "couverture"],
            
            # Administratif
            "administratif": ["administration", "officiel", "gouvernement", "mairie", "préfecture"],
            "contrat": ["contrat", "accord", "conditions", "clause", "signature", "engagement"],
            "certificat": ["certificat", "diplôme", "attestation", "qualification", "formation"],
            
            # Personnel
            "identité": ["identité", "passeport", "carte", "nationale", "permis", "conduire"],
            "santé": ["médical", "santé", "docteur", "hôpital", "ordonnance", "traitement"],
            "travail": ["emploi", "travail", "salaire", "contrat", "entreprise", "poste"],
            
            # Autres
            "voyage": ["voyage", "billet", "réservation", "hôtel", "vol", "transport"],
            "éducation": ["école", "université", "cours", "étudiant", "formation", "diplôme"],
            "loisirs": ["sport", "culture", "cinéma", "concert", "événement", "loisir"]
        }
        
        # Recherche de mots-clés avec scoring
        keyword_scores = {}
        for category, keywords in document_keywords.items():
            score = 0
            for keyword in keywords:
                # Compte pondéré: résumé x2, texte x1
                score += combined_text.count(keyword) * 2 if keyword in summary.lower() else 0
                score += combined_text.count(keyword) if keyword in extracted_text.lower() else 0
            
            if score > 0:
                keyword_scores[category] = score
        
        # Ajouter les catégories les mieux scorées
        sorted_categories = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        for category, score in sorted_categories[:4]:  # Max 4 tags sémantiques
            tags.add(category)
        
        # === 3. TAGS SPÉCIAUX SELON LE CONTENU ===
        # Confidentialité automatique si PII
        if pii_types:
            tags.add("confidentiel")
        
        # Tag urgent si mots-clés détectés
        urgent_keywords = ["urgent", "immediate", "expiration", "délai", "échéance"]
        if any(keyword in combined_text for keyword in urgent_keywords):
            tags.add("urgent")
        
        # Tag numérique si beaucoup de chiffres
        digit_ratio = sum(1 for c in extracted_text if c.isdigit()) / max(len(extracted_text), 1)
        if digit_ratio > 0.15:  # Plus de 15% de chiffres
            tags.add("numérique")
        
        # === 4. TAGS DE QUALITÉ OCR ===
        if len(extracted_text) > 200:
            tags.add("texte-riche")
        elif len(extracted_text) < 50 and extracted_text:
            tags.add("peu-texte")
        
        # === 5. LIMITATION ET PRIORITÉ ===
        # Priorité: confidentiel > PII > sémantiques > qualité
        priority_order = ["confidentiel", "banque", "identité", "facture", "contrat", 
                         "administratif", "santé", "urgent", "numérique", "texte-riche"]
        
        final_tags = []
        
        # Ajouter par ordre de priorité
        for priority_tag in priority_order:
            if priority_tag in tags and len(final_tags) < 8:
                final_tags.append(priority_tag)
        
        # Ajouter les autres tags restants
        for tag in tags:
            if tag not in final_tags and len(final_tags) < 8:
                final_tags.append(tag)
        
        # Minimum 3 tags, maximum 8
        if len(final_tags) < 3:
            # Ajouter des tags génériques si nécessaire
            generic_tags = ["document", "analysé", "traité"]
            for generic in generic_tags:
                if len(final_tags) < 3:
                    final_tags.append(generic)
        
        logger.info(f"Tags extraits: {final_tags}")
        return final_tags[:8]  # Maximum 8 tags
    
    async def analyze_document(self, args: VisionArgs) -> FileMeta:
        """
        Pipeline complet d'analyse de document visuel avec détection PII avancée
        Supporte maintenant les PDF (conversion automatique en images)
        
        Étapes:
        1. Détection format (image vs PDF)
        2. Chargement/Conversion (PDF → images)
        3. OCR multilangue sur toutes les pages
        4. Détection PII textuelle et visuelle combinées
        5. Génération résumé intelligent global
        6. Extraction tags sémantiques
        7. Construction FileMeta final
        
        Contrainte: ≤ 1500ms par page A4 300 DPI
        """
        start_time = time.time()
        logger.info(f"🔍 Début analyse document: {args.path}")
        
        try:
            # === 1. DÉTECTION FORMAT ET CHARGEMENT ===
            is_pdf = self._is_pdf(args.path)
            file_type = "pdf" if is_pdf else "image"
            images = []
            
            if is_pdf:
                # Traitement PDF
                logger.info("📄 Document PDF détecté - conversion en cours...")
                images = self._convert_pdf_to_images(args.path, args.extract_pages)
                
                if not images:
                    return FileMeta(
                        path=args.path,
                        status="error_pdf_conversion",
                        summary="Impossible de convertir le PDF - pdf2image requis ou PDF corrompu",
                        file_type="pdf"
                    )
            else:
                # Traitement image standard
                image = self._load_image(args.path, args.bytes)
                if image is None:
                    return FileMeta(
                        path=args.path,
                        status="error_load",
                        summary="Impossible de charger l'image - format non supporté ou fichier corrompu",
                        file_type="image"
                    )
                images = [image]
            
            pages_count = len(images)
            logger.info(f"📸 {pages_count} page(s) à analyser")
            
            # === 2. TRAITEMENT MULTI-PAGES ===
            all_extracted_text = []
            all_pii_types = []
            all_pii_spans = []
            pii_detected = False
            
            for page_num, image in enumerate(images, 1):
                logger.info(f"📄 Analyse page {page_num}/{pages_count}")
                
                # OCR par page
                page_text = self._extract_text_ocr(image)
                if page_text.strip():
                    all_extracted_text.append(f"Page {page_num}: {page_text}")
                
                # PII textuelle par page
                page_pii_detected, page_pii_types, page_pii_spans = self._detect_text_pii(page_text)
                if page_pii_detected:
                    pii_detected = True
                    all_pii_types.extend(page_pii_types)
                    
                    # Ajuster les positions pour le texte global
                    text_offset = sum(len(t) + 1 for t in all_extracted_text[:-1]) if all_extracted_text else 0
                    for span in page_pii_spans:
                        adjusted_span = PIISpan(
                            start=span.start + text_offset,
                            end=span.end + text_offset,
                            label=span.label
                        )
                        all_pii_spans.append(adjusted_span)
                
                # PII visuelle par page (cartes, ID, NSFW)
                visual_pii = await self._detect_visual_pii(image)
                if visual_pii:
                    pii_detected = True
                    all_pii_types.extend(visual_pii)
                    logger.info(f"👁️  Page {page_num} - PII visuels: {', '.join(visual_pii)}")
            
            # === 3. CONSOLIDATION RÉSULTATS ===
            # Texte global
            full_extracted_text = "\n".join(all_extracted_text)
            text_length = len(full_extracted_text)
            
            # PII globaux (dédoublonnés)
            unique_pii_types = list(set(all_pii_types))
            
            logger.info(f"📝 OCR total: {text_length} caractères sur {pages_count} page(s)")
            if pii_detected:
                logger.info(f"⚠️  PII détectés: {', '.join(unique_pii_types)}")
            
            # === 4. GÉNÉRATION RÉSUMÉ GLOBAL ===
            visual_context = f"{file_type.upper()} {pages_count} page(s)"
            if unique_pii_types:
                visual_context += f", PII détectés: {', '.join(unique_pii_types)}"
            if text_length == 0:
                visual_context += ", aucun texte OCR"
            
            summary = await self._generate_summary(full_extracted_text, visual_context)
            
            # === 5. EXTRACTION TAGS GLOBAUX ===
            tags = self._extract_tags(summary, unique_pii_types, full_extracted_text)
            
            # Ajouter tag PDF si applicable
            if is_pdf:
                if "pdf" not in tags:
                    tags.append("pdf")
                if pages_count > 1:
                    tags.append("multi-pages")
            
            # === 6. MÉTRIQUES DE PERFORMANCE ===
            processing_time = time.time() - start_time
            avg_time_per_page = processing_time / pages_count
            
            # Vérification contrainte de latence par page
            if avg_time_per_page > 1.5:
                logger.warning(f"⏰ Latence par page dépassée: {avg_time_per_page:.2f}s > 1.5s")
            else:
                logger.info(f"✅ Analyse terminée en {processing_time:.2f}s ({avg_time_per_page:.2f}s/page)")
            
            # === 7. CONSTRUCTION RÉSULTAT FINAL ===
            result = FileMeta(
                path=args.path,
                source="vision",
                text=full_extracted_text,
                summary=summary,
                tags=tags[:8],  # Limiter à 8 tags max
                pii_detected=pii_detected,
                pii_types=unique_pii_types,
                pii_spans=all_pii_spans,
                status="ok",
                pages_processed=pages_count,
                file_type=file_type
            )
            
            # Log résumé final
            logger.info(f"📊 Résultat {file_type.upper()}: {len(result.pii_types)} types PII, {len(result.tags)} tags, {pages_count} page(s)")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Erreur lors de l'analyse: {str(e)}"
            logger.error(f"❌ {error_msg} (après {processing_time:.2f}s)")
            
            return FileMeta(
                path=args.path,
                status="error_processing",
                summary=error_msg,
                tags=["erreur", "non-traité"],
                file_type=file_type if 'file_type' in locals() else "unknown"
            )

# === AGENT ET TOOL CORAL ===

class Agent:
    """Classe Agent pour compatibilité avec Coral"""
    def __init__(self, name: str, description: str, tools: List):
        self.name = name
        self.description = description
        self.tools = tools

# Instance globale de l'agent
vision_agent_instance = VisionAgent()

# Agent Coral
vision_agent = Agent(
    name="vision",
    description="Agent d'analyse de fichiers visuels avec détection PII avancée - 100% offline",
    tools=["analyze_document"]
)

# Tool function pour Coral (entrée principale)
async def analyze_document(args: VisionArgs) -> FileMeta:
    """
    Tool Coral pour analyser un document visuel
    
    Args:
        args.path: Chemin vers le fichier image
        args.bytes: Données binaires optionnelles (fallback)
    
    Returns:
        FileMeta: Métadonnées complètes avec texte, résumé, tags et PII détectés
    """
    return await vision_agent_instance.analyze_document(args)

# === TESTS ET DÉMONSTRATION ===

if __name__ == "__main__":
    async def test_vision_complete():
        """
        Test complet de l'agent Vision avec validation détection NSFW
        """
        print("🚀 Test complet Agent Vision Neurosort + NSFW")
        print("=" * 55)
        
        # === TEST 1: FACTURE AVEC PII ===
        print("\n📋 Test 1: Analyse facture avec PII")
        test_path = "test_facture.jpg"
        
        if Path(test_path).exists():
            args = VisionArgs(path=test_path)
            result = await analyze_document(args)
            
            print(f"✅ Statut: {result.status}")
            print(f"📝 Texte: {result.text[:100]}...")
            print(f"📄 Résumé: {result.summary[:150]}...")
            print(f"🏷️  Tags: {result.tags}")
            print(f"⚠️  PII détectés: {result.pii_detected}")
            print(f"🔍 Types PII: {result.pii_types}")
            print(f"📍 Spans PII: {len(result.pii_spans)} détectés")
        else:
            print("❌ Fichier facture test non trouvé")
        
        # === TEST PDF ===
        print("\n📋 Test PDF: Analyse document multi-pages")
        test_pdf = "test_document.pdf"
        
        if Path(test_pdf).exists():
            args_pdf = VisionArgs(path=test_pdf)
            result_pdf = await analyze_document(args_pdf)
            
            print(f"✅ Statut PDF: {result_pdf.status}")
            print(f"📄 Type: {result_pdf.file_type}")
            print(f"📄 Pages: {result_pdf.pages_processed}")
            print(f"📝 Texte: {result_pdf.text[:200]}...")
            print(f"🏷️  Tags: {result_pdf.tags}")
            print(f"⚠️  PII détectés: {result_pdf.pii_detected}")
        else:
            print("❌ Fichier PDF test non trouvé")
        
        # === TEST 2: VALIDATION NSFW ===
        print("\n📋 Test 2: Validation détection NSFW")
        
        # Générer images de test si besoin
        try:
            # Créer une image safe de test
            safe_image = np.zeros((200, 300, 3), dtype=np.uint8)
            safe_image.fill(100)  # Gris neutre
            cv2.putText(safe_image, "DOCUMENT SAFE", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imwrite("test_safe.jpg", safe_image)
            
            # Test image safe
            args_safe = VisionArgs(path="test_safe.jpg")
            result_safe = await analyze_document(args_safe)
            
            nsfw_detected_safe = "NUDITY" in result_safe.pii_types
            print(f"   🖼️  Image safe: {'❌ Faux positif' if nsfw_detected_safe else '✅ Correctement classée'}")
            
            # Créer une image avec beaucoup de tons chair
            nsfw_image = np.zeros((200, 300, 3), dtype=np.uint8)
            # Remplir avec tons chair (couleur BGR qui donne HSV dans plage peau)
            nsfw_image[:, :] = [150, 180, 220]  # Ton chair dominant
            cv2.imwrite("test_nsfw_sim.jpg", nsfw_image)
            
            # Test image nsfw simulée
            args_nsfw = VisionArgs(path="test_nsfw_sim.jpg")
            result_nsfw = await analyze_document(args_nsfw)
            
            nsfw_detected_nsfw = "NUDITY" in result_nsfw.pii_types
            print(f"   🔥 Image NSFW sim: {'✅ Correctement détectée' if nsfw_detected_nsfw else '❌ Non détectée'}")
            
            # Statistiques
            print(f"\n📊 Résultats validation NSFW:")
            print(f"   Safe → NSFW: {'❌' if nsfw_detected_safe else '✅'}")
            print(f"   NSFW → NSFW: {'✅' if nsfw_detected_nsfw else '❌'}")
            print(f"   Précision: {int(not nsfw_detected_safe and nsfw_detected_nsfw) * 100}%")
            
        except Exception as e:
            print(f"❌ Erreur test NSFW: {e}")
        
        # === TEST 3: PERFORMANCE ET ROBUSTESSE ===
        print("\n📋 Test 3: Performance et robustesse")
        
        # Test fichier inexistant
        args_missing = VisionArgs(path="fichier_inexistant.jpg")
        result_missing = await analyze_document(args_missing)
        print(f"📂 Fichier manquant: {result_missing.status}")
        
        # Test modèle NSFW
        print(f"🧠 Modèle NSFW ONNX: {'✅ Disponible' if ONNX_AVAILABLE else '❌ Fallback only'}")
        print(f"� Support PDF: {'✅ Disponible' if PDF_AVAILABLE else '❌ Installez pdf2image'}")
        print(f"�📂 Dossier modèles: {Path('ai_models/nsfw').exists()}")
        
        print(f"\n🎯 Pipeline complet testé avec support PDF + NSFW!")
    
    # Lancer les tests
    asyncio.run(test_vision_complete())
