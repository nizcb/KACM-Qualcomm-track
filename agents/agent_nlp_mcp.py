"""
NLP MCP Agent with Full AI Capabilities - Autonomous Agent Version
================================================================

Autonomous AI MCP agent that can:
- Analyze files and detect PII with contextual intelligence
- Reason about tasks to accomplish (ReAct pattern)
- Plan actions autonomously
- Use tools intelligently
- Handle complex requests with Groq/Ollama/Llama
- Expose all capabilities via official MCP protocol

Uses Groq (fast cloud) + Ollama (local fallback) + LangChain for AI, with intelligent backend selection.
"""

import asyncio
import json
import logging
import os
import re
import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from collections import Counter

# Suppress Pydantic warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Official MCP imports
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
from mcp.server.fastmcp import Image
from mcp.types import TextContent
from pydantic import BaseModel, Field

# AI Backend imports
try:
    from .ai_backend import get_ai_backend, generate_text, is_ai_available, get_ai_info
    AI_BACKEND_AVAILABLE = True
    print("✅ AI Backend available")
except ImportError:
    AI_BACKEND_AVAILABLE = False
    print("⚠️ AI Backend not available")

# LangChain imports for AI (fallback)
try:
    from langchain_community.llms import Ollama
    from langchain.tools import tool
    LANGCHAIN_AVAILABLE = True
    print("✅ LangChain available")
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain not available")

# PDF Support
try:
    import PyPDF2
    PDF_AVAILABLE = True
    print("✅ PDF support available (PyPDF2)")
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PDF support not available (pip install PyPDF2)")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
    print("✅ Advanced PDF support available (PyMuPDF)")
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("⚠️ Advanced PDF support not available (pip install pymupdf)")

# Ensure logs directory exists
logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Logging configuration with Unicode support for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ollama Configuration (fallback)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.2:latest")

# Initialize AI Backend
ai_backend = None
llm = None  # Legacy compatibility - use ai_backend instead

if AI_BACKEND_AVAILABLE:
    try:
        ai_backend = get_ai_backend()
        if ai_backend.is_available():
            info = ai_backend.get_backend_info()
            logger.info(f"✅ AI Backend ready: {info['backend']} ({info['model']})")
            print(f"✅ AI Agent ready: {info['backend']} backend")
            llm = ai_backend  # For legacy compatibility during transition
        else:
            logger.warning("⚠️ No AI backend available")
            print("⚠️ No AI backend available")
    except Exception as e:
        logger.warning(f"⚠️ AI Backend initialization failed: {e}")
        print(f"⚠️ AI Backend initialization failed: {e}")
        ai_backend = None

# Advanced regex patterns for PII detection
PII_REGEXES: Dict[str, re.Pattern] = {
    "EMAIL": re.compile(r"[\w\.\-]+@[\w\.-]+\.[a-z]{2,}", re.I),
    "PHONE": re.compile(r"\+?\d{1,3}[\s\-]?\d[\d\s\-]{8,}\d", re.I),
    "CARD": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
    "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b"),
    "SSN": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"),
}
# ──────────────────────────────────────────────────────────────────────────
# Utility functions for file processing (identical to original)
# ──────────────────────────────────────────────────────────────────────────

def extract_pdf_content(file_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Text content of the PDF
    """
    content = ""
    
    # Try PyMuPDF first (more performant)
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(file_path)
            for page_num in range(doc.page_count):
                page = doc[page_num]
                content += page.get_text() + "\n"
            doc.close()
            return content
        except Exception as e:
            logger.warning(f"⚠️ PyMuPDF error: {e}")
    
    # Fallback with PyPDF2
    if PDF_AVAILABLE:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text() + "\n"
            return content
        except Exception as e:
            return f"Error during PDF extraction: {str(e)}"
    
    return "No PDF library available"

# ──────────────────────────────────────────────────────────────────────────
# Configuration et modèles avancés (mis à jour avec les capacités de l'original)
# ──────────────────────────────────────────────────────────────────────────
@dataclass
class NLPConfig:
    """Configuration for NLP agent with AI"""
    max_text_length: int = 10000
    use_ai_analysis: bool = True  # Use AI for analysis
    llm_model: str = LLAMA_MODEL
    log_file: str = str(Path(__file__).parent.parent / "logs" / "nlp_agent.log")
    offline_mode: bool = False

# Modèles Pydantic pour la sortie structurée MCP
class FileAnalysisResult(BaseModel):
    """Résultat de l'analyse de fichier (compatible avec l'original)"""
    file_path: str = Field(description="Chemin du fichier analysé")
    resume: str = Field(description="Résumé intelligent du contenu")
    warning: bool = Field(description="Présence d'informations PII")
    analysis_method: str = Field(description="Méthode d'analyse utilisée", default="ai_enhanced")
    
class TextAnalysisResult(BaseModel):
    """Résultat de l'analyse de texte"""
    word_count: int = Field(description="Nombre de mots")
    char_count: int = Field(description="Nombre de caractères")
    sentences: int = Field(description="Nombre de phrases")
    paragraphs: int = Field(description="Nombre de paragraphes")
    keywords: List[str] = Field(description="Mots-clés principaux")
    sentiment: str = Field(description="Sentiment général")
    language: str = Field(description="Langue détectée")
    ai_summary: Optional[str] = Field(description="Résumé généré par l'IA", default=None)

class PIIDetectionResult(BaseModel):
    """Résultat de la détection PII"""
    found_pii: bool = Field(description="PII détectées")
    pii_types: List[str] = Field(description="Types de PII trouvés")
    pii_count: int = Field(description="Nombre total de PII")
    redacted_text: str = Field(description="Texte avec PII masquées")
    ai_analysis: Optional[str] = Field(description="Analyse IA des PII", default=None)

class SummaryResult(BaseModel):
    """Résultat du résumé"""
    summary: str = Field(description="Résumé du texte")
    key_points: List[str] = Field(description="Points clés")
    summary_length: int = Field(description="Longueur du résumé")
    compression_ratio: float = Field(description="Ratio de compression")
    ai_enhanced: bool = Field(description="Résumé amélioré par l'IA", default=False)

class TranslationResult(BaseModel):
    """Résultat de la traduction"""
    translated_text: str = Field(description="Texte traduit")
    source_language: str = Field(description="Langue source")
    target_language: str = Field(description="Langue cible")
    confidence: float = Field(description="Confiance de la traduction")

class BatchProcessingResult(BaseModel):
    """Résultat du traitement en lot"""
    batch_info: Dict[str, Any] = Field(description="Informations du lot")
    files: List[Dict[str, Any]] = Field(description="Summary of files")
    detailed_results: Dict[str, Any] = Field(description="Résultats détaillés")

# ──────────────────────────────────────────────────────────────────────────
# Agent IA Principal (identique à l'original avec intégration MCP)
# ──────────────────────────────────────────────────────────────────────────
class NLPAgent:
    """Autonomous AI agent for NLP analysis with reasoning capabilities - MCP Version"""
    
    def __init__(self, config: NLPConfig):
        self.config = config
        # Use the global ai_backend for AI capabilities
        self.ai_backend = ai_backend if not config.offline_mode else None
        self.llm = self.ai_backend  # Legacy compatibility
        self.conversation_history = []  # Simple memory
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs(os.path.dirname(self.config.log_file), exist_ok=True)
        handler = logging.FileHandler(self.config.log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        
    def _generate_smart_summary(self, content: str) -> str:
        """Generate intelligent summary with AI if available"""
        if not self.config.offline_mode and self.ai_backend:
            try:
                prompt = f"""Summarize the following text in maximum 3 sentences in English, keeping essential information:

Text: {content}

Summary:
Never start the summary with an introduction like "Here is the summary" or similar.
"""
                response = generate_text(self.ai_backend, prompt)
                return response.strip()
            except Exception as e:
                logger.warning(f"⚠️ AI error, switching to offline mode: {e}")
        
        # Fallback: simple summary
        sentences = content.replace('\n', ' ').split('.')
        summary_sentences = []
        for sentence in sentences:
            if sentence.strip() and len(summary_sentences) < 3:
                summary_sentences.append(sentence.strip())
        
        return '. '.join(summary_sentences) + '.' if summary_sentences else "Summary not available."

    def _detect_pii_intelligent(self, content: str) -> bool:
        """Detect PII with AI if available, otherwise use regex"""
        if not self.config.offline_mode and self.ai_backend:
            try:
                prompt = f"""You are a data security expert. Analyze the following text and detect ONLY real personally identifiable information (PII) present.

Types of PII to look for with attention to context:
- Real email addresses (not fictional examples)
- Real phone numbers
- Real credit card numbers (not test numbers like 4242 4242 4242 4242)
- Real IBAN/account numbers
- Real social security numbers
- Complete real postal addresses
- Specific birth dates
- Real ID/passport numbers
- Full names of real people

IMPORTANT: Ignore fictional examples, test data, placeholders, and obviously fake data.

Text to analyze:
{content}

Respond ONLY with:
- "NO_PII" if no real personal information is detected
- "PII_DETECTED" if real PII is present

Response:"""
                
                response = generate_text(self.ai_backend, prompt)
                response = response.strip().upper()
                
                if "PII_DETECTED" in response:
                    logger.info("[PII] PII detected by AI")
                    return True
                else:
                    logger.info("[OK] No PII detected by AI")
                    return False
                    
            except Exception as e:
                logger.warning(f"⚠️ AI error for PII detection, switching to regex mode: {e}")
        
        # Fallback: regex detection
        for label, pattern in PII_REGEXES.items():
            if pattern.search(content):
                logger.info(f"[PII] PII detected by regex: {label}")
                return True
        
        logger.info("[OK] No PII detected by regex")
        return False
    
    def reason_and_act(self, query: str) -> str:
        """Reason and act on a given query using ReAct pattern"""
        if not self.ai_backend or self.config.offline_mode:
            return "AI Agent not available, using fallback mode"
        
        # Simplified ReAct reasoning template
        prompt = f"""You are an AI agent specialized in NLP analysis and PII detection.

You have access to the following tools:
1. read_file_tool(file_path) - Read a file (text or PDF)
2. generate_smart_summary_tool(text) - Generate intelligent summary
3. detect_pii_tool(text) - Detect PII
4. save_json_tool(data, filename) - Save to JSON
5. list_files_tool(directory) - List files
6. process_multiple_files_tool(file_paths) - Process multiple files (comma-separated)

Use the following reasoning format:
Thought: [What I need to do]
Action: [Tool to use]
Action Input: [Tool parameters]
Observation: [Action result]
... (repeat if necessary)
Final Answer: [Final response]

Question: {query}

Start by thinking:"""

        try:
            # Generate response with reasoning
            response = generate_text(self.ai_backend, prompt)
            
            # Process response to extract actions
            return self._process_reasoning_response(response, query)
        except Exception as e:
            return f"Error during reasoning: {e}"
    
    def _process_reasoning_response(self, response: str, original_query: str) -> str:
        """Process reasoning response and execute actions"""
        lines = response.split('\n')
        result = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Action:'):
                action = line.replace('Action:', '').strip()
                result.append(f"[ACTION] Action: {action}")
            elif line.startswith('Thought:'):
                thought = line.replace('Thought:', '').strip()
                result.append(f"[THOUGHT] Thinking: {thought}")
            elif line.startswith('Final Answer:'):
                answer = line.replace('Final Answer:', '').strip()
                result.append(f"[ANSWER] Final response: {answer}")
        
        return '\n'.join(result) if result else response
    
    def process_file_with_reasoning(self, file_path: str) -> Dict[str, Any]:
        """Process a file using AI agent reasoning"""
        
        if self.ai_backend and not self.config.offline_mode:
            try:
                # Utilisation de l'agent IA pour traiter le fichier
                query = f"""Analyse le fichier '{file_path}' et produis un résultat JSON avec:
                1. Lis le contenu du fichier
                2. Génère un résumé du contenu
                3. Détecte la présence de PII
                4. Crée un JSON avec file_path, resume, et warning (boolean)
                5. Sauvegarde le résultat dans un fichier nommé '{os.path.splitext(os.path.basename(file_path))[0]}_analysis.json'
                
                Retourne uniquement le JSON final."""
                
                # Raisonnement de l'agent
                reasoning = self.reason_and_act(query)
                logger.info(f"[AI] Raisonnement de l'agent:\n{reasoning}\n")
                
                # Exécution directe des outils pour obtenir le résultat
                return self._execute_analysis(file_path)
                
            except Exception as e:
                logger.error(f"Erreur avec l'agent IA: {e}")
                return self._fallback_process_file(file_path)
        else:
            return self._fallback_process_file(file_path)
    
    def _execute_analysis(self, file_path: str) -> Dict[str, Any]:
        """Execute analysis with available tools"""
        try:
            # Read file directly
            logger.info("[READ] Reading file...")
            if not os.path.isabs(file_path):
                current_dir = os.getcwd()
                full_path = os.path.join(current_dir, file_path)
            else:
                full_path = file_path
            
            # Check file extension
            _, ext = os.path.splitext(full_path.lower())
            
            if ext == '.pdf':
                # PDF processing
                if PDF_AVAILABLE or PYMUPDF_AVAILABLE:
                    content = extract_pdf_content(full_path)
                    logger.info(f"[PDF] PDF content extracted ({len(content)} characters)")
                else:
                    content = "Error: No PDF library available"
                    logger.warning("[WARN] No PDF library available")
            else:
                # Process text files
                with open(full_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                logger.info(f"[TEXT] Text content read ({len(content)} characters)")
            
            # Generate intelligent summary
            logger.info("[AI] Generating summary...")
            resume = self._generate_smart_summary(content)
            
            # Intelligent PII detection
            logger.info("[AI] Intelligent PII detection...")
            pii_found = self._detect_pii_intelligent(content)
            
            # Build final result
            result = {
                "file_path": os.path.abspath(file_path),
                "resume": resume,
                "warning": pii_found
            }
            
            # Sauvegarde automatique
            output_file = f"{os.path.splitext(os.path.basename(file_path))[0]}_analysis.json"
            logger.info(f"[SAVE] Sauvegarde dans {output_file}...")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return result
            
        except Exception as e:
            return {
                "file_path": os.path.abspath(file_path) if os.path.exists(file_path) else file_path,
                "resume": f"Erreur lors du traitement : {str(e)}",
                "warning": False
            }
    
    def _fallback_process_file(self, file_path: str) -> Dict[str, Any]:
        """File processing in fallback mode (without AI agent)"""
        try:
            # Read file directly
            logger.info("[READ] Reading file...")
            if not os.path.isabs(file_path):
                current_dir = os.getcwd()
                full_path = os.path.join(current_dir, file_path)
            else:
                full_path = file_path
            
            # Check file extension
            _, ext = os.path.splitext(full_path.lower())
            
            if ext == '.pdf':
                # PDF processing
                if PDF_AVAILABLE or PYMUPDF_AVAILABLE:
                    content = extract_pdf_content(full_path)
                    logger.info(f"[PDF] PDF content extracted ({len(content)} characters)")
                else:
                    content = "Error: No PDF library available"
                    logger.warning("[WARN] No PDF library available")
            else:
                # Process text files
                with open(full_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                logger.info(f"[TEXT] Text content read ({len(content)} characters)")
            
            # Generate intelligent summary
            logger.info("[AI] Generating summary...")
            resume = self._generate_smart_summary(content)
            
            # Intelligent PII detection
            logger.info("[AI] Intelligent PII detection...")
            pii_found = self._detect_pii_intelligent(content)
            
            # Construction du résultat final
            result = {
                "file_path": os.path.abspath(file_path),
                "resume": resume,
                "warning": pii_found
            }
            
            return result
            
        except Exception as e:
            return {
                "file_path": os.path.abspath(file_path) if os.path.exists(file_path) else file_path,
                "resume": f"Erreur lors du traitement : {str(e)}",
                "warning": False
            }
    
    def chat(self, message: str) -> str:
        """Chat interface with AI agent"""
        if self.ai_backend and not self.config.offline_mode:
            try:
                return self.reason_and_act(message)
            except Exception as e:
                return f"Error during chat: {e}"
        else:
            return "Offline mode enabled. Use direct commands to process files."
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extraction de texte depuis un PDF"""
        try:
            return extract_pdf_content(pdf_path)
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction PDF: {e}")
            return ""
    
    def generate_smart_summary(self, text: str) -> str:
        """Génère un résumé intelligent avec LLM si disponible, sinon utilise un fallback."""
        return self._generate_smart_summary(text)

    def detect_pii_intelligent(self, text: str) -> PIIDetectionResult:
        """Détecte les informations personnelles identifiables (PII) dans un texte avec IA."""
        ai_analysis = None
        found_pii = False
        pii_types = []
        pii_count = 0
        redacted_text = text
        
        try:
            # Use AI if available for intelligent detection
            if self.ai_backend and self.config.use_ai_analysis:
                try:
                    prompt = f"""You are a data security expert. Analyze the following text and detect ONLY real personally identifiable information (PII) present.

Types of PII to look for with attention to context:
- Real email addresses (not fictional examples)
- Real phone numbers
- Real credit card numbers (not test numbers like 4242 4242 4242 4242)
- Real IBAN/account numbers
- Real social security numbers
- Complete real postal addresses
- Specific birth dates
- Real ID/passport numbers
- Full names of real people

IMPORTANT: Ignore fictional examples, test data, placeholders, and obviously fake data.

Text to analyze:
{text}

Respond ONLY with:
- "NO_PII" if no real personal information is detected
- "PII_DETECTED: [detected types]" if real PII is present

Response:"""
                    
                    response = generate_text(self.ai_backend, prompt)
                    ai_analysis = response.strip()
                    
                    if "NO_PII" in response.upper():
                        found_pii = False
                    elif "PII_DETECTED" in response.upper():
                        found_pii = True
                        # Extract types if specified
                        if ":" in response:
                            types_part = response.split(":")[1].strip()
                            pii_types = [t.strip() for t in types_part.split(",")]
                        
                except Exception as ai_error:
                    logger.warning(f"⚠️ AI error for PII detection, switching to regex mode: {ai_error}")
            
            # Fallback or complement: regex detection
            if not ai_analysis or not found_pii:
                regex_pii = []
                
                for label, pattern in PII_REGEXES.items():
                    matches = pattern.findall(text)
                    if matches:
                        found_pii = True
                        regex_pii.append(label)
                        pii_count += len(matches)
                        # Mask PII
                        redacted_text = pattern.sub(f"[{label}_REDACTED]", redacted_text)
                
                if regex_pii:
                    pii_types.extend(regex_pii)
            
            pii_count = max(pii_count, len(pii_types))
            
            return PIIDetectionResult(
                found_pii=found_pii,
                pii_types=list(set(pii_types)),  # Supprimer les doublons
                pii_count=pii_count,
                redacted_text=redacted_text,
                ai_analysis=ai_analysis
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection PII: {e}")
            return PIIDetectionResult(
                found_pii=False,
                pii_types=[],
                pii_count=0,
                redacted_text=text,
                ai_analysis=f"Erreur: {str(e)}"
            )
            
    def analyze_text_basic(self, text: str) -> TextAnalysisResult:
        """Analyse basique du texte avec amélioration IA"""
        words = text.split()
        sentences = text.split('.')
        paragraphs = text.split('\n\n')
        
        # Extraction des mots-clés simples
        word_freq = Counter(word.lower().strip('.,!?;:') for word in words if len(word) > 3)
        keywords = [word for word, freq in word_freq.most_common(10)]
        
        # Simple language detection
        language = "fr" if any(word in text.lower() for word in ["le", "la", "de", "et", "à"]) else "en"
        
        # Default sentiment
        sentiment = "neutral"
        ai_summary = None
        
        # Use AI if available
        if self.ai_backend and self.config.use_ai_analysis:
            try:
                # Sentiment analysis with AI
                sentiment_prompt = f"""Analyze the sentiment of the following text and respond ONLY with: positive, negative, or neutral.

Text: {text[:500]}

Sentiment:"""
                sentiment_response = generate_text(self.ai_backend, sentiment_prompt)
                sentiment = sentiment_response.strip().lower()
                
                # Generate AI summary
                ai_summary = self.generate_smart_summary(text)
                
            except Exception as e:
                logger.warning(f"AI analysis error: {e}")
        
        return TextAnalysisResult(
            word_count=len(words),
            char_count=len(text),
            sentences=len(sentences),
            paragraphs=len(paragraphs),
            keywords=keywords,
            sentiment=sentiment,
            language=language,
            ai_summary=ai_summary
        )
        
    def summarize_text(self, text: str, max_length: int = 150) -> SummaryResult:
        """Text summary with AI"""
        # Use AI for summary if available
        ai_enhanced = False
        summary = ""
        key_points = []
        
        if self.ai_backend and self.config.use_ai_analysis:
            try:
                summary = self.generate_smart_summary(text)
                ai_enhanced = True
                
                # Extract key points with AI
                key_points_prompt = f"""Extract maximum 3 key points from the following text as a short list:

Text: {text}

Key points (one per line, start with -):"""
                key_points_response = generate_text(self.ai_backend, key_points_prompt)
                key_points = [point.strip('- ').strip() for point in key_points_response.split('\n') if point.strip().startswith('-')][:3]
                
            except Exception as e:
                logger.warning(f"AI summary error: {e}")
                ai_enhanced = False
        
        # Fallback if AI is not available
        if not summary:
            sentences = text.split('.')
            if len(sentences) <= 3:
                summary = text
            else:
                # Take first and last sentences
                summary = '. '.join(sentences[:2] + sentences[-1:])
            
            # Points clés basiques
            if len(sentences) > 5:
                key_points = sentences[1:4]  # Phrases du milieu
        
        compression_ratio = len(summary) / len(text) if text else 0
        
        return SummaryResult(
            summary=summary,
            key_points=key_points,
            summary_length=len(summary),
            compression_ratio=compression_ratio,
            ai_enhanced=ai_enhanced
        )
        
    def translate_text(self, text: str, target_lang: str = "en") -> TranslationResult:
        """Translation with AI if available"""
        # Use AI for translation if available
        if self.ai_backend and self.config.use_ai_analysis:
            try:
                translate_prompt = f"""Translate the following text to {target_lang}. Respond ONLY with the translation, no commentary:

Text to translate: {text}

Translation:"""
                translated_text = generate_text(self.ai_backend, translate_prompt).strip()
                
                return TranslationResult(
                    translated_text=translated_text,
                    source_language="auto",
                    target_language=target_lang,
                    confidence=0.9
                )
            except Exception as e:
                logger.warning(f"AI translation error: {e}")
        
        # Fallback: basic translation (placeholder)
        return TranslationResult(
            translated_text=f"[TRANSLATION to {target_lang}]: {text}",
            source_language="auto",
            target_language=target_lang,
            confidence=0.8
        )
        
    def process_multiple_files_with_reasoning(self, file_paths: List[str]) -> Dict[str, Any]:
        """Process multiple files using AI agent reasoning"""
        results = {}
        summary_results = []
        total_warnings = 0
        
        logger.info(f"[BATCH] Processing {len(file_paths)} files...")
        
        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"[{i}/{len(file_paths)}] Traitement du fichier: {file_path}")
            
            try:
                # Traiter chaque fichier individuellement
                result = self.process_file_with_reasoning(file_path)
                
                # Ajouter au résultat global
                file_key = os.path.basename(file_path)
                results[file_key] = result
                
                # Préparer le résumé
                summary_results.append({
                    "file": file_key,
                    "path": result["file_path"],
                    "has_pii": result["warning"],
                    "summary_preview": result["resume"][:100] + "..." if len(result["resume"]) > 100 else result["resume"]
                })
                
                if result["warning"]:
                    total_warnings += 1
                    
            except Exception as e:
                logger.error(f"[ERROR] Erreur lors du traitement de {file_path}: {e}")
                results[os.path.basename(file_path)] = {
                    "file_path": file_path,
                    "resume": f"Erreur lors du traitement: {str(e)}",
                    "warning": False
                }
        
        # Créer un résumé global
        batch_summary = {
            "batch_info": {
                "total_files": len(file_paths),
                "processed_files": len(results),
                "files_with_pii": total_warnings,
                "processing_date": datetime.now().isoformat()
            },
            "files": summary_results,
            "detailed_results": results
        }
        
        return batch_summary

# Création de l'agent NLP avec configuration
config = NLPConfig()
agent = None  # Lazy loading

def get_agent():
    """Lazy loading de l'agent NLP"""
    global agent
    if agent is None:
        agent = NLPAgent(config)
    return agent

# ──────────────────────────────────────────────────────────────────────────
# Serveur MCP avec capacités IA complètes
# ──────────────────────────────────────────────────────────────────────────

# Création du serveur MCP
mcp = FastMCP("NLP Agent IA", dependencies=["langchain_community", "PyPDF2", "pydantic", "pymupdf"])

# Ressources MCP améliorées
@mcp.resource("nlp://config")
def get_nlp_config() -> str:
    """Configuration de l'agent NLP avec IA"""
    return json.dumps({
        "max_text_length": config.max_text_length,
        "use_ai_analysis": config.use_ai_analysis,
        "llm_model": config.llm_model,
        "supported_formats": ["txt", "pdf", "py", "md", "json", "csv", "xml", "html", "log"],
        "capabilities": ["analyze", "summarize", "detect_pii", "translate", "reason", "chat", "batch_processing"],
        "ai_features": [
            "intelligent_summary", 
            "contextual_pii_detection", 
            "sentiment_analysis", 
            "reasoning_and_planning",
            "autonomous_task_execution",
            "multi_format_support",
            "batch_processing"
        ],
        "ollama_status": "connected" if llm else "disconnected",
        "fallback_mode": "available"
    }, indent=2)

@mcp.resource("nlp://status")
def get_nlp_status() -> str:
    """Statut complet de l'agent NLP IA"""
    return json.dumps({
        "status": "ready",
        "ai_available": llm is not None,
        "agent_mode": "ai_enhanced" if llm else "fallback",
        "langchain_available": LANGCHAIN_AVAILABLE,
        "pdf_support": PDF_AVAILABLE or PYMUPDF_AVAILABLE,
        "pymupdf_available": PYMUPDF_AVAILABLE,
        "pypdf2_available": PDF_AVAILABLE,
        "offline_mode": config.offline_mode,
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0 - Agent IA Autonome MCP",
        "reasoning_capabilities": "ReAct pattern enabled" if llm else "disabled",
        "supported_operations": [
            "file_analysis",
            "text_analysis", 
            "pii_detection",
            "summarization",
            "translation",
            "chat_interaction",
            "reasoning_and_planning",
            "batch_processing"
        ]
    }, indent=2)

@mcp.resource("nlp://capabilities")
def get_nlp_capabilities() -> str:
    """Capacités avancées de l'agent IA"""
    return json.dumps({
        "autonomous_features": {
            "reasoning": "ReAct pattern with Llama 3.2",
            "planning": "Multi-step task orchestration",
            "memory": "Conversation history maintained",
            "fallback": "Intelligent degradation without AI"
        },
        "analysis_capabilities": {
            "text_analysis": "Deep NLP analysis with AI enhancement",
            "sentiment_analysis": "AI-powered sentiment detection",
            "keyword_extraction": "Frequency-based + AI semantic analysis",
            "language_detection": "Rule-based + AI confirmation"
        },
        "pii_detection": {
            "method": "AI + Regex hybrid approach",
            "context_awareness": "Distinguishes real vs. fake data",
            "supported_types": ["email", "phone", "credit_card", "ssn", "iban", "addresses"]
        },
        "document_processing": {
            "formats": ["PDF", "TXT", "MD", "JSON", "CSV", "XML", "HTML", "LOG", "PY"],
            "pdf_extraction": "PyMuPDF + PyPDF2 fallback",
            "batch_processing": "Multiple files simultaneously"
        },
        "ai_integration": {
            "llm_model": LLAMA_MODEL,
            "base_url": OLLAMA_BASE_URL,
            "temperature": 0.7,
            "connection_status": "active" if llm else "inactive"
        }
    }, indent=2)

# Outils MCP avec capacités IA complètes (identiques à l'agent original)
@mcp.tool()
def analyze_text(text: str) -> TextAnalysisResult:
    """Analyse complète d'un texte avec IA (identique à l'agent original)"""
    if len(text) > config.max_text_length:
        text = text[:config.max_text_length]
    
    try:
        result = get_agent().analyze_text_basic(text)
        logger.info(f"Analyse de texte réussie: {result.word_count} mots, IA: {result.ai_summary is not None}")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {e}")
        raise

@mcp.tool()
def analyze_file(file_path: str) -> FileAnalysisResult:
    """Analyse d'un fichier avec IA (compatibilité avec l'agent original)"""
    try:
        result = get_agent().process_file_with_reasoning(file_path)
        
        # Conversion vers le format MCP
        return FileAnalysisResult(
            file_path=result["file_path"],
            resume=result["resume"],
            warning=result["warning"],
            analysis_method="ai_enhanced" if llm else "fallback"
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du fichier {file_path}: {e}")
        raise

@mcp.tool()

def analyze_text_pii_with_ai_corrected(text: str) -> Dict[str, Any]:
    """
    Version corrigée de l'analyse PII avec IA + fallback regex FORCÉ
    
    CORRECTION CRITIQUE:
    - Force l'utilisation du fallback regex si l'IA échoue
    - Combine les résultats IA + regex pour plus de robustesse
    - Log détaillé pour debugging
    - Logique de décision améliorée
    """
    logger.info("🔍 Analyse PII corrigée - Démarrage")
    
    # Résultat par défaut
    result = {
        "filepath": "analysis",
        "summary": "Analyse en cours...",
        "warning": False,
        "pii_detected": [],
        "method_used": "unknown",
        "debug_info": {}
    }
    
    # 1. TOUJOURS faire l'analyse regex en premier (fallback garanti)
    logger.info("🔍 Étape 1: Analyse regex (fallback)")
    regex_pii = detect_pii_in_text(text)
    regex_warning = len(regex_pii) > 0
    
    result["debug_info"]["regex_pii"] = regex_pii
    result["debug_info"]["regex_warning"] = regex_warning
    
    logger.info(f"📊 Regex - PII détectées: {regex_pii}")
    logger.info(f"📊 Regex - Warning: {regex_warning}")
    
    # 2. Tentative d'analyse IA (si disponible)
    ai_result = None
    ai_warning = False
    
    if llm and LANGCHAIN_AVAILABLE:
        try:
            logger.info("🔍 Étape 2: Analyse IA")
            
            prompt = f"""Analyse ce texte et détermine s'il contient des informations personnelles identifiables (PII).
            
PII incluent: emails, téléphones, cartes bancaires, IBAN, adresses, noms complets, etc.

Texte à analyser:
{text[:1000]}

Réponds par 'OUI' si PII détectées, 'NON' sinon, suivi d'une explication courte."""

            ai_response = llm.invoke(prompt)
            
            # Parser la réponse IA
            if ai_response and isinstance(ai_response, str):
                ai_response_lower = ai_response.lower()
                if "oui" in ai_response_lower or "yes" in ai_response_lower:
                    ai_warning = True
                elif "non" in ai_response_lower or "no" in ai_response_lower:
                    ai_warning = False
                else:
                    # Réponse ambiguë, utiliser regex
                    logger.warning("⚠️ Réponse IA ambiguë, utilisation regex")
                    ai_warning = regex_warning
                
                ai_result = ai_response
                result["debug_info"]["ai_response"] = ai_response
                result["debug_info"]["ai_warning"] = ai_warning
                
                logger.info(f"📊 IA - Réponse: {ai_response[:100]}...")
                logger.info(f"📊 IA - Warning: {ai_warning}")
            else:
                logger.warning("⚠️ Réponse IA invalide, utilisation regex")
                ai_warning = regex_warning
                
        except Exception as e:
            logger.error(f"❌ Erreur IA: {e}")
            ai_result = None
            ai_warning = regex_warning  # Fallback vers regex
    else:
        logger.info("ℹ️ IA non disponible, utilisation regex uniquement")
        ai_warning = regex_warning
    
    # 3. LOGIQUE DE DÉCISION CORRIGÉE
    # Priorité: Si regex OU IA détectent des PII -> WARNING = True
    final_warning = regex_warning or ai_warning
    
    logger.info(f"🎯 Décision finale: regex={regex_warning} OR ai={ai_warning} = {final_warning}")
    
    # 4. Construction du résultat final
    if ai_result:
        result["summary"] = ai_result
        result["method_used"] = "ai_with_regex_fallback"
    else:
        result["summary"] = f"Analyse regex: {len(regex_pii)} types de PII détectés: {', '.join(regex_pii)}"
        result["method_used"] = "regex_only"
    
    result["warning"] = final_warning
    result["pii_detected"] = regex_pii
    
    logger.info(f"✅ Analyse terminée - Warning: {final_warning}")
    return result


def detect_pii_in_text(text: str) -> PIIDetectionResult:
    """Détection intelligente des informations personnelles avec IA"""
    try:
        result = get_agent().detect_pii_intelligent(text)
        logger.info(f"Détection PII: {result.pii_count} éléments trouvés, IA: {result.ai_analysis is not None}")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la détection PII: {e}")
        raise

@mcp.tool()
def summarize_text(text: str, max_length: int = 150) -> SummaryResult:
    """Résumé intelligent d'un texte avec IA"""
    try:
        result = get_agent().summarize_text(text, max_length)
        logger.info(f"Résumé généré: {result.summary_length} caractères, IA: {result.ai_enhanced}")
        return result
    except Exception as e:
        logger.error(f"Erreur lors du résumé: {e}")
        raise

@mcp.tool()
def translate_text(text: str, target_language: str = "en") -> TranslationResult:
    """Traduction intelligente d'un texte avec IA"""
    try:
        result = get_agent().translate_text(text, target_language)
        logger.info(f"Traduction vers {target_language} réussie")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la traduction: {e}")
        raise

@mcp.tool()
def chat_with_agent(message: str) -> str:
    """Chat interactif avec l'agent IA NLP"""
    try:
        result = get_agent().chat(message)
        logger.info(f"Chat traité: {len(message)} caractères d'entrée")
        return result
    except Exception as e:
        logger.error(f"Erreur lors du chat: {e}")
        raise

@mcp.tool()
def reason_about_task(query: str) -> str:
    """Raisonnement et planification de tâches avec l'agent IA"""
    try:
        result = get_agent().reason_and_act(query)
        logger.info(f"Raisonnement effectué pour: {query[:50]}...")
        return result
    except Exception as e:
        logger.error(f"Erreur lors du raisonnement: {e}")
        raise

@mcp.tool()
def process_multiple_files(file_paths: List[str]) -> BatchProcessingResult:
    """Batch processing of multiple files with AI"""
    try:
        result = get_agent().process_multiple_files_with_reasoning(file_paths)
        logger.info(f"Traitement en lot terminé: {len(file_paths)} files")
        
        return BatchProcessingResult(
            batch_info=result["batch_info"],
            files=result["files"],
            detailed_results=result["detailed_results"]
        )
    except Exception as e:
        logger.error(f"Erreur lors du traitement en lot: {e}")
        raise

@mcp.tool()
async def process_document(file_path: str, operations: List[str], ctx: Context) -> Dict[str, Any]:
    """Traitement complet d'un document avec plusieurs opérations utilisant l'IA"""
    await ctx.info(f"Traitement intelligent du document: {file_path}")
    
    try:
        # Lecture du fichier
        if file_path.lower().endswith('.pdf'):
            text = get_agent().extract_text_from_pdf(file_path)
            await ctx.info("📄 Texte extrait du PDF avec succès")
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            await ctx.info("📄 Fichier texte lu avec succès")
        
        results = {}
        agent_instance = get_agent()
        
        # Exécution des opérations demandées avec IA
        for operation in operations:
            await ctx.info(f"🤖 Exécution de l'opération IA: {operation}")
            
            if operation == "analyze":
                results["analysis"] = agent_instance.analyze_text_basic(text)
                await ctx.info("✅ Analyse complète terminée")
            elif operation == "summarize":
                results["summary"] = agent_instance.summarize_text(text)
                await ctx.info("✅ Résumé intelligent généré")
            elif operation == "detect_pii":
                results["pii_detection"] = agent_instance.detect_pii_intelligent(text)
                await ctx.info("✅ Détection PII intelligente terminée")
            elif operation == "translate":
                results["translation"] = agent_instance.translate_text(text)
                await ctx.info("✅ Traduction avec IA terminée")
            elif operation == "reason":
                reasoning = agent_instance.reason_and_act(f"Analyse ce document: {text[:500]}...")
                results["reasoning"] = {"analysis": reasoning}
                await ctx.info("✅ Raisonnement IA terminé")
            elif operation == "file_analysis":
                # Utiliser la méthode de traitement de fichier complète
                file_result = agent_instance.process_file_with_reasoning(file_path)
                results["file_analysis"] = file_result
                await ctx.info("✅ Analyse de fichier complète terminée")
            else:
                await ctx.warning(f"Opération inconnue: {operation}")
        
        await ctx.info("🎉 Traitement intelligent terminé avec succès")
        return results
        
    except Exception as e:
        await ctx.error(f"Erreur lors du traitement: {e}")
        raise

@mcp.tool()
async def batch_analyze_directory(directory_path: str, file_extensions: List[str], ctx: Context) -> BatchProcessingResult:
    """Analyse en lot d'un répertoire complet avec IA"""
    await ctx.info(f"Analyse intelligente du répertoire: {directory_path}")
    
    if not file_extensions:
        file_extensions = ['.txt', '.py', '.md', '.json', '.csv', '.xml', '.html', '.log', '.pdf']
    
    try:
        file_paths = []
        
        # Parcourir le répertoire
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file.lower())
                
                if ext in file_extensions:
                    file_paths.append(file_path)
        
        await ctx.info(f"📁 {len(file_paths)} files trouvés")
        
        if not file_paths:
            await ctx.warning("Aucun fichier trouvé avec les extensions spécifiées")
            return BatchProcessingResult(
                batch_info={"error": "Aucun fichier trouvé"},
                files=[],
                detailed_results={}
            )
        
        # Traitement en lot
        result = get_agent().process_multiple_files_with_reasoning(file_paths)
        await ctx.info(f"✅ Traitement en lot terminé: {len(file_paths)} files")
        
        return BatchProcessingResult(
            batch_info=result["batch_info"],
            files=result["files"],
            detailed_results=result["detailed_results"]
        )
        
    except Exception as e:
        await ctx.error(f"Erreur lors de l'analyse du répertoire: {e}")
        raise

# Prompts MCP améliorés avec IA (identiques aux capacités de l'agent original)
@mcp.prompt(title="Analyse Intelligente de Document")
def analyze_document_prompt(file_path: str, operations: str = "analyze,summarize,detect_pii") -> str:
    """Prompt pour l'analyse complète d'un document avec IA"""
    ops_list = [op.strip() for op in operations.split(',')]
    return f"""
🤖 Agent IA NLP - Analyse Intelligente de Document

📄 Document à analyser: {file_path}

🧠 Capacités IA disponibles:
- Llama 3.2 pour l'analyse contextuelle avancée
- Raisonnement autonome (ReAct pattern)
- Détection PII intelligente avec compréhension du contexte
- Résumés adaptatifs selon le type de contenu
- Traduction contextuelle et culturellement appropriée
- Planification automatique des tâches

🔧 Opérations IA à effectuer:
{chr(10).join(f'- {op} (avec intelligence artificielle)' for op in ops_list)}

📊 Formats supportés:
- PDF (extraction intelligente avec PyMuPDF + PyPDF2)
- Texte (TXT, MD, JSON, CSV, XML, HTML, LOG, PY)

⚡ Utiliser l'outil process_document avec les paramètres appropriés.

L'agent utilisera son raisonnement autonome pour optimiser l'analyse selon le type de document.
"""

@mcp.prompt(title="Détection PII Intelligente")
def intelligent_pii_detection_prompt(text: str) -> str:
    """Prompt pour la détection intelligente d'informations personnelles"""
    return f"""
🔒 Agent IA NLP - Détection PII Intelligente

📝 Texte à analyser: {text[:300]}...

🧠 Analyse IA avancée:
- Utilise Llama 3.2 pour l'analyse contextuelle
- Distinction automatique entre données réelles et exemples fictifs
- Évaluation de la sensibilité selon le contexte
- Détection de patterns complexes et variations linguistiques

🔍 Types de PII détectés intelligemment:
- Adresses email réelles (filtrage des exemples)
- Numéros de téléphone avec validation contextuelle
- Informations financières sensibles (cartes, IBAN, etc.)
- Données d'identité personnelle (SSN, passeports)
- Adresses et informations de localisation
- Noms et prénoms avec vérification contextuelle

⚙️ Méthodes de détection:
1. Analyse IA contextuelle (primaire)
2. Patterns regex avancés (fallback)
3. Validation croisée des résultats

🎯 Utiliser l'outil detect_pii_in_text pour une analyse intelligente.

L'agent déterminera automatiquement le niveau de sensibilité des informations détectées.
"""

@mcp.prompt(title="Raisonnement et Planification IA")
def reasoning_prompt(task: str) -> str:
    """Prompt pour le raisonnement et la planification de tâches"""
    return f"""
🧠 Agent IA NLP - Raisonnement Autonome

🎯 Tâche à analyser: {task}

🤖 Capacités de raisonnement:
- Pattern ReAct (Reasoning + Acting)
- Planification multi-étapes
- Adaptation dynamique de la stratégie
- Utilisation autonome d'outils spécialisés
- Mémoire conversationnelle
- Gestion d'erreurs intelligente

🔧 Outils disponibles:
- Analyse de documents (PDF, texte, multi-formats)
- Détection PII avec compréhension contextuelle
- Résumés adaptatifs selon le type de contenu
- Traduction contextuelle
- Orchestration de workflows complexes
- Traitement en lot de files

⚡ Capacités avancées:
- Analyse de documents multi-formats
- Batch processing intelligent
- Détection PII avec filtrage contextuel
- Résumés adaptatifs selon le domaine
- Traduction culturellement appropriée
- Planification automatique de tâches

🎯 Utiliser l'outil reason_about_task pour démarrer l'analyse intelligente.

L'agent analysera la tâche et créera un plan d'exécution optimal.
"""

@mcp.prompt(title="Chat Interactif IA")
def chat_prompt(context: str = "") -> str:
    """Prompt pour le chat interactif avec l'agent IA"""
    return f"""
💬 Agent IA NLP - Chat Interactif

{f"📋 Contexte: {context}" if context else ""}

🤖 Capacités conversationnelles:
- Raisonnement autonome avec Llama 3.2
- Compréhension contextuelle avancée
- Planification automatique des actions
- Exécution autonome de tâches complexes
- Mémoire conversationnelle
- Adaptation dynamique selon les besoins

💡 Exemples d'interactions:
- "Analyse ce document et dis-moi s'il contient des informations sensibles"
- "Résume-moi les points clés de ce texte en français"
- "Y a-t-il des données personnelles dans ce fichier PDF ?"
- "Traduis ce texte en gardant le sens original et le contexte"
- "Traite tous les files de ce dossier et génère un rapport"
- "Explique-moi pourquoi tu as détecté ces informations comme sensibles"

🔧 Actions automatiques:
- Lecture et extraction de contenu (PDF, texte)
- Analyse intelligente et contextuelle
- Détection PII avec justification
- Génération de résumés adaptatifs
- Traduction contextuelle
- Sauvegarde automatique des résultats

⚡ Utiliser l'outil chat_with_agent pour commencer la conversation.

L'agent comprendra vos demandes et planifiera automatiquement les actions nécessaires.
"""

@mcp.prompt(title="Traitement en Lot")
def batch_processing_prompt(directory_or_files: str, operations: str = "analyze,detect_pii") -> str:
    """Prompt pour le traitement en lot de files"""
    ops_list = [op.strip() for op in operations.split(',')]
    return f"""
🔄 Agent IA NLP - Traitement en Lot Intelligent

📁 Source: {directory_or_files}

🧠 Capacités de traitement en lot:
- Traitement parallèle intelligent
- Priorisation automatique selon le type de fichier
- Détection de format automatique
- Gestion d'erreurs robuste
- Génération de rapports consolidés

🔧 Opérations IA à effectuer:
{chr(10).join(f'- {op} (avec intelligence artificielle)' for op in ops_list)}

📊 Formats supportés:
- Documents PDF (extraction intelligente)
- Fichiers texte (TXT, MD, JSON, CSV, XML, HTML, LOG)
- Code source (PY, JS, etc.)
- Traitement récursif de dossiers

📋 Résultats générés:
- Rapport consolidé avec statistiques
- Analyse individuelle par fichier
- Détection PII avec alertes
- Résumés intelligents par document
- Sauvegarde automatique des résultats

⚡ Utiliser l'outil process_multiple_files ou batch_analyze_directory selon le cas.

L'agent optimisera automatiquement le traitement selon le volume et le type de files.
"""

# ──────────────────────────────────────────────────────────────────────────
# Fonctions utilitaires compatibles avec l'agent original
# ──────────────────────────────────────────────────────────────────────────

def process_file(file_path: str, offline_mode: bool = False) -> Dict[str, Any]:
    """Traite un fichier et retourne le résultat JSON (compatible avec l'agent original)"""
    config_temp = NLPConfig()
    config_temp.offline_mode = offline_mode
    agent_temp = NLPAgent(config_temp)
    return agent_temp.process_file_with_reasoning(file_path)

def process_multiple_files_standalone(file_paths: List[str], offline_mode: bool = False) -> Dict[str, Any]:
    """Traite plusieurs files et retourne le résultat JSON global (compatible avec l'agent original)"""
    config_temp = NLPConfig()
    config_temp.offline_mode = offline_mode
    agent_temp = NLPAgent(config_temp)
    return agent_temp.process_multiple_files_with_reasoning(file_paths)

def chat_mode():
    """Mode chat interactif avec l'agent IA (compatible avec l'agent original)"""
    print("🤖 Mode Chat Interactif - Agent IA NLP MCP")
    print("==========================================")
    print("Tapez 'quit' pour quitter, 'help' pour l'aide")
    
    agent_chat = get_agent()
    
    if not agent_chat.llm:
        print("⚠️ Agent IA non disponible, vérifiez Ollama")
        return
    
    print("\n💬 Chat prêt ! Posez vos questions...")
    
    while True:
        try:
            user_input = input("\n👤 Vous: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Au revoir!")
                break
            
            if user_input.lower() == 'help':
                print("""
🤖 Commandes disponibles:
- Analysez un fichier: "Analyse le fichier recit.txt" ou "Analyse le fichier document.pdf"
- Listez les files: "Quels files sont disponibles?"
- Posez des questions: "Résume-moi ce document"
- Détection PII: "Y a-t-il des informations sensibles?"
- Traitement en lot: "Traite tous les files .txt du dossier"
- quit/exit: Quitter le chat

📄 Formats supportés: .txt, .py, .md, .json, .csv, .xml, .html, .log, .pdf
🤖 L'agent utilise Llama 3.2 pour un raisonnement intelligent
                """)
                continue
            
            if not user_input:
                continue
            
            print("\n🤖 Agent IA: ", end="")
            response = agent_chat.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")

# ──────────────────────────────────────────────────────────────────────────
# Interface principale MCP
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Mode de lancement
    if len(sys.argv) > 1:
        if sys.argv[1] == "--chat":
            chat_mode()
        elif sys.argv[1] == "--test":
            # Test rapide de l'agent
            print("🔧 Test de l'agent IA NLP MCP...")
            test_agent = get_agent()
            if test_agent.llm:
                print("✅ Agent IA connecté et prêt")
            else:
                print("⚠️ Agent IA en mode fallback")
            print("🎯 Utilisez --chat pour le mode interactif")
        else:
            print("❌ Options: --chat pour le mode interactif, --test pour tester")
    else:
        # Lancement du serveur MCP
        print("🚀 Démarrage de l'Agent IA NLP MCP...")
    print("=" * 50)
    print("[STARTUP] Agent IA autonome avec Llama 3.2")
    print("[STARTUP] Support multi-formats (PDF, texte, etc.)")
    print("[STARTUP] Detection PII intelligente")
    print("[STARTUP] Capacites de raisonnement et planification")
    print("[STARTUP] Traitement en lot et workflows complexes")
    print("=" * 50)
    print("[MCP] Serveur MCP disponible sur stdio")
    print("[MCP] Pret a recevoir des connexions MCP...")
    
    # Vérification des capacités
    if llm:
        print("[AI] Llama 3.2 connecte - Mode IA complet")
    else:
        print("[WARN] Llama non disponible - Mode fallback active")
    
    if PDF_AVAILABLE or PYMUPDF_AVAILABLE:
        print("[PDF] Support PDF disponible")
    else:
        print("[WARN] Support PDF limite")
        
        print("\n[INFO] Utilisez un client MCP pour vous connecter")
        print("[INFO] Ou lancez avec --chat pour le mode interactif")
        
        # Lancement du serveur MCP
        mcp.run()
