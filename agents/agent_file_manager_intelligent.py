#!/usr/bin/env python3
"""
Agent File Manager MCP Intelligent avec Llama
=============================================

Agent File Manager avancé qui utilise Llama pour:
- analysisr le content/résumé des files
- Déterminer intelligemment l'organisation en dossiers
- Classer par catégories thématiques
- Respecter la sécurité (public/secure)
- Créer une structure logique et intuitive
"""

import os
import sys
import json
import asyncio
import logging
import shutil
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Imports MCP
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
from mcp.types import TextContent
from pydantic import BaseModel, Field

# LangChain pour l'IA
try:
    from langchain_community.llms import Ollama
    LANGCHAIN_AVAILABLE = True
    print("✅ LangChain disponible pour File Manager")
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain non disponible")

# Logging configuration with automatic directory creation
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / 'file_manager.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Configuration Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.2:latest")

# Initialisation du LLM
llm = None
if LANGCHAIN_AVAILABLE:
    try:
        llm = Ollama(
            model=LLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1  # More deterministic for classification
        )
        # Connection test
        test_response = llm.invoke("Test file organization")
        logger.info("✅ Ollama/Llama File Manager connected")
        print("✅ Agent File Manager AI ready")
    except Exception as e:
        logger.warning(f"⚠️ Ollama connection failed: {e}")
        print(f"⚠️ Ollama connection failed: {e}")
        llm = None

class FileOrganizationRequest(BaseModel):
    """File organization request"""
    source_folder: str
    target_folder: str = "organized"
    file_analysiss: List[Dict[str, Any]] = []

class FileOrganizationResponse(BaseModel):
    """File organization response"""
    success: bool
    files_organized: int
    folders_created: List[str]
    organization_structure: Dict[str, Any]
    error_message: Optional[str] = None

class IntelligentFileManager:
    """File Manager intelligent avec IA"""
    
    def __init__(self, llm_instance=None):
        self.llm = llm_instance or llm
        self.organization_log = []
        
    def analyze_content_for_organization(self, file_path: str, multi_agent_analysis: Dict[str, Any]) -> Dict[str, str]:
        """
        Utilise Llama pour déterminer l'organisation optimale d'un fichier
        en analysant selon le type de fichier (texte/audio/image)
        """
        if not self.llm:
            # Fallback sans IA
            return self._fallback_organization(file_path, multi_agent_analysis)
        
        try:
            # Déterminer le type de fichier principal
            file_ext = Path(file_path).suffix.lower()
            file_type = self._determine_file_type(file_ext)
            
            # Extraire les données pertinentes selon le type
            content_data = self._extract_relevant_content(multi_agent_analysis, file_type)
            
            # Construire le prompt structuré selon le type de fichier
            prompt = self._build_structured_prompt(Path(file_path).name, file_type, content_data)

            response = self.llm.invoke(prompt)
            
            # Parser la réponse
            any_warning = any([
                multi_agent_analysis.get("nlp_warning", False),
                multi_agent_analysis.get("audio_warning", False), 
                multi_agent_analysis.get("vision_warning", False)
            ])
            return self._parse_llama_organization_response(response, any_warning)
            
        except Exception as e:
            logger.error(f"AI organization error: {e}")
            return self._fallback_organization(file_path, multi_agent_analysis)
    
    def _parse_llama_organization_response(self, response: str, is_sensitive: bool) -> Dict[str, str]:
        """Parse Llama response"""
        try:
            lines = response.strip().split('\n')
            result = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().upper()
                    value = value.strip()
                    
                    if key == "CATEGORY" or key == "CATÉGORIE" or key == "CATEGORIE":
                        result["category"] = self._sanitize_folder_name(value)
                    elif key == "SUBCATEGORY" or key == "SOUS-CATÉGORIE" or key == "SOUS-CATEGORIE":
                        result["subcategory"] = self._sanitize_folder_name(value)
                    elif key == "SECURITY" or key == "SÉCURITÉ" or key == "SECURITE":
                        result["security"] = "secure" if "secure" in value.lower() or is_sensitive else "public"
                    elif key == "PRIORITY" or key == "PRIORITÉ" or key == "PRIORITE":
                        result["priority"] = value.lower()
                    elif key == "JUSTIFICATION":
                        result["justification"] = value
            
            # Default values if missing
            result.setdefault("category", "documents")
            result.setdefault("subcategory", "general")
            result.setdefault("security", "secure" if is_sensitive else "public")
            result.setdefault("priority", "medium")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing Llama response: {e}")
            return self._fallback_organization("", "", is_sensitive)
    
    def _fallback_organization(self, file_path: str, multi_agent_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Intelligent organization by semantic analysis without AI"""
        file_name = Path(file_path).name.lower()
        file_ext = Path(file_path).suffix.lower()
        
        # Extract ALL content analyzed by agents
        nlp_content = multi_agent_analysis.get("nlp_summary", "")
        audio_transcript = multi_agent_analysis.get("audio_transcript", "")
        audio_summary = multi_agent_analysis.get("audio_summary", "")
        vision_ocr = multi_agent_analysis.get("vision_ocr_text", "")
        vision_desc = multi_agent_analysis.get("vision_description", "")
        
        # Combiner TOUTES les informations textuelles
        all_content = f"{nlp_content} {audio_transcript} {audio_summary} {vision_ocr} {vision_desc}".lower()
        
        # Vérifier s'il y a des PII dans N'IMPORTE QUEL agent
        is_sensitive = any([
            multi_agent_analysis.get("nlp_warning", False),
            multi_agent_analysis.get("audio_warning", False),
            multi_agent_analysis.get("vision_warning", False)
        ])
        
        # Déterminer le type de fichier principal
        file_type = self._determine_file_type(file_ext)
        
        # INTELLIGENT SEMANTIC ANALYSIS (without rigid rules)
        category, subcategory = self._intelligent_semantic_analysis(
            filename=file_name,
            file_type=file_type,
            content=all_content,
            nlp_content=nlp_content,
            audio_content=f"{audio_transcript} {audio_summary}",
            vision_content=f"{vision_ocr} {vision_desc}"
        )
        
        # Déterminer la priorité selon le content
        priority = self._determine_priority(all_content, is_sensitive)
        
        return {
            "category": category,
            "subcategory": subcategory,
            "security": "secure" if is_sensitive else "public",
            "priority": priority,
            "justification": f"Semantic analysis {file_type}: {category}/{subcategory}"
        }
    
    def _sanitize_folder_name(self, name: str) -> str:
        """Nettoie un nom de dossier"""
        # Enlever les caractères spéciaux, garder alphanumériques et tirets
        clean = re.sub(r'[^\w\-]', '', name.lower())
        return clean or "general"
    
    def create_folder_structure(self, target_folder: str, organization: Dict[str, str]) -> str:
        """Creates folder structure according to organization"""
        base_path = Path(target_folder)
        
        # Structure: target_folder/security/category/subcategory/
        folder_path = base_path / organization["security"] / organization["category"] / organization["subcategory"]
        folder_path.mkdir(parents=True, exist_ok=True)
        
        return str(folder_path)
    
    def organize_file(self, file_path: str, multi_agent_analysis: Dict[str, Any], target_folder: str) -> Dict[str, Any]:
        """Organise un fichier selon l'analysis de TOUS les agents"""
        try:
            # analysisr pour l'organisation avec toutes les données
            organization = self.analyze_content_for_organization(file_path, multi_agent_analysis)
            
            # Créer la structure de dossiers
            target_path = self.create_folder_structure(target_folder, organization)
            
            # Déplacer le fichier
            source = Path(file_path)
            destination = Path(target_path) / source.name
            
            # Éviter d'écraser si le fichier existe déjà
            counter = 1
            while destination.exists():
                stem = source.stem
                suffix = source.suffix
                destination = Path(target_path) / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.move(str(source), str(destination))
            
            result = {
                "source_path": str(source),
                "destination_path": str(destination),
                "organization": organization,
                "multi_agent_analysis": multi_agent_analysis,
                "success": True
            }
            
            self.organization_log.append(result)
            logger.info(f"✅ File organized (multi-agents): {source.name} -> {organization['category']}/{organization['subcategory']}")
            
            return result
            
        except Exception as e:
            error_result = {
                "source_path": file_path,
                "error": str(e),
                "success": False
            }
            logger.error(f"❌ Erreur organisation fichier {file_path}: {e}")
            return error_result
    
    def organize_multiple_files(self, file_analysiss: List[Dict[str, Any]], target_folder: str = "organized") -> FileOrganizationResponse:
        """Organise plusieurs files selon leurs analysiss"""
        logger.info(f"🗂️ Starting organization of {len(file_analysiss)} files")
        
        successful_files = 0
        failed_files = 0
        folders_created = set()
        organization_structure = {}
        
        for analysis in file_analysiss:
            file_path = analysis.get("filepath", "")
            
            if not Path(file_path).exists():
                logger.warning(f"⚠️ Fichier introuvable: {file_path}")
                failed_files += 1
                continue
            
            result = self.organize_file(file_path, analysis, target_folder)
            
            if result["success"]:
                successful_files += 1
                org = result["organization"]
                
                # Construire la structure d'organisation
                security = org["security"]
                category = org["category"]
                subcategory = org["subcategory"]
                
                if security not in organization_structure:
                    organization_structure[security] = {}
                if category not in organization_structure[security]:
                    organization_structure[security][category] = {}
                if subcategory not in organization_structure[security][category]:
                    organization_structure[security][category][subcategory] = []
                
                organization_structure[security][category][subcategory].append({
                    "filename": Path(file_path).name,
                    "destination": result["destination_path"],
                    "priority": org["priority"]
                })
                
                # Ajouter les dossiers créés
                folder_path = f"{security}/{category}/{subcategory}"
                folders_created.add(folder_path)
                
            else:
                failed_files += 1
        
        # Créer le rapport d'organisation
        success = failed_files == 0
        response = FileOrganizationResponse(
            success=success,
            files_organized=successful_files,
            folders_created=list(folders_created),
            organization_structure=organization_structure,
            error_message=f"{failed_files} files en erreur" if failed_files > 0 else None
        )
        
        logger.info(f"✅ Organization completed: {successful_files} successful, {failed_files} failed")
        return response
    
    def generate_organization_report(self, response: FileOrganizationResponse, target_folder: str) -> str:
        """Generates organization report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"organization_report_{timestamp}.json"
        
        report = {
            "timestamp": timestamp,
            "target_folder": target_folder,
            "summary": {
                "files_organized": response.files_organized,
                "folders_created": len(response.folders_created),
                "success": response.success
            },
            "organization_structure": response.organization_structure,
            "folders_created": response.folders_created,
            "detailed_log": self.organization_log
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 Organization report generated: {report_path}")
        return report_path

    def _determine_file_type(self, file_ext: str) -> str:
        """Determines the main file type"""
        if file_ext in ['.txt', '.pdf', '.doc', '.docx', '.rtf', '.odt']:
            return "document"
        elif file_ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac']:
            return "audio"
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff']:
            return "image"
        elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']:
            return "video"
        else:
            return "document"  # Par défaut traiter comme document

    def _extract_relevant_content(self, multi_agent_analysis: Dict[str, Any], file_type: str) -> Dict[str, str]:
        """Extrait le content pertinent selon le type de fichier"""
        content = {
            "primary_content": "",
            "secondary_content": "",
            "contains_pii": False
        }
        
        if file_type == "document":
            # Pour les documents : priorité au NLP
            content["primary_content"] = multi_agent_analysis.get("nlp_summary", "")
            content["secondary_content"] = multi_agent_analysis.get("vision_ocr_text", "")
            content["contains_pii"] = multi_agent_analysis.get("nlp_warning", False) or multi_agent_analysis.get("vision_warning", False)
            
        elif file_type == "audio":
            # Pour l'audio : priorité à la transcription
            content["primary_content"] = multi_agent_analysis.get("audio_transcript", "")
            content["secondary_content"] = multi_agent_analysis.get("audio_summary", "")
            content["contains_pii"] = multi_agent_analysis.get("audio_warning", False)
            
        elif file_type == "image":
            # Pour les images : priorité à l'OCR et description
            content["primary_content"] = multi_agent_analysis.get("vision_ocr_text", "")
            content["secondary_content"] = multi_agent_analysis.get("vision_description", "")
            content["contains_pii"] = multi_agent_analysis.get("vision_warning", False)
            
        elif file_type == "video":
            # Pour les vidéos : combiner audio et vision
            content["primary_content"] = multi_agent_analysis.get("audio_transcript", "")
            content["secondary_content"] = multi_agent_analysis.get("vision_description", "")
            content["contains_pii"] = multi_agent_analysis.get("audio_warning", False) or multi_agent_analysis.get("vision_warning", False)
        
        return content
    
    def _build_structured_prompt(self, filename: str, file_type: str, content_data: Dict[str, str]) -> str:
        """Builds a structured and concise prompt for the LLM"""
        
        prompt = f"""EXPERT ORGANISATION FICHIERS ENTREPRISE

=== CONTEXTE ===
Fichier: {filename}
Type: {file_type.upper()}
content principal: {content_data['primary_content'][:400]}
content secondaire: {content_data['secondary_content'][:200]}
Sensitive data: {'DETECTED' if content_data['contains_pii'] else 'NONE'}

=== DOMAINES MÉTIER AUTORISÉS ===
rh_personnel | finance_comptabilite | legal_juridical | technical_it
communication_marketing | administration_management | projects_research | multimedia_creation

=== RÈGLES STRICTES ===
• INTERDICTION: "general", "autres", "misc", "divers"
• OBLIGATION: Catégorie métier spécifique
• CRÉATIVITÉ: Sous-catégorie contextuelle précise
• SÉCURITÉ: "secure" si PII détectées, sinon "public"

=== INSTRUCTION ===
analysisr le content et déterminer la meilleure organisation métier.
Priorité au content le plus informatif selon le type de fichier.
Créer une sous-catégorie descriptive et professionnelle.

=== FORMAT RÉPONSE ===
CATÉGORIE: [domaine métier précis]
SOUS-CATÉGORIE: [classification contextuelle créative]
SÉCURITÉ: [public/secure]
PRIORITÉ: [haute/moyenne/basse]
JUSTIFICATION: [analysis contextuelle concise]"""

        return prompt

    def _intelligent_semantic_analysis(self, filename: str, file_type: str, content: str, 
                                      nlp_content: str, audio_content: str, vision_content: str) -> tuple:
        """
        Intelligent semantic analysis that leaves free choice to context
        Pas de règles rigides - juste des mots-clés et de la logique contextuelle
        """
        
        # Définir les domaines thématiques avec leurs mots-clés indicateurs
        thematic_domains = {
            "rh_personnel": {
                "keywords": ["cv", "curriculum", "candidat", "emploi", "recrutement", "entretien", 
                           "salaire", "formation", "competence", "experience", "embauche", "carriere"],
                "contexts": ["ressources humaines", "management personnel", "recrutement", "formation"]
            },
            "finance_comptabilite": {
                "keywords": ["facture", "budget", "comptabilite", "finance", "cout", "prix", 
                           "paiement", "tresorerie", "devis", "invoice", "montant", "euros"],
                "contexts": ["finances", "comptabilité", "management financière", "facturation"]
            },
            "legal_juridical": {
                "keywords": ["contrat", "accord", "legal", "legal", "clause", "signature", 
                           "convention", "cgu", "cgv", "conformite", "droit", "procedure"],
                "contexts": ["legal", "légal", "contrats", "conformité"]
            },
            "technical_it": {
                "keywords": ["config", "api", "serveur", "base", "donnees", "infrastructure", 
                           "code", "script", "technical", "systeme", "reseau", "deployment"],
                "contexts": ["it", "technical", "développement", "infrastructure"]
            },
            "communication_marketing": {
                "keywords": ["marketing", "communication", "presentation", "campagne", "publicitaire", 
                           "commercial", "vente", "brand", "marque", "promotion", "newsletter"],
                "contexts": ["marketing", "communication", "commercial", "promotion"]
            },
            "projects_research": {
                "keywords": ["rapport", "etude", "analysis", "research", "projet", "veille", 
                           "benchmark", "statistique", "donnees", "investigation", "evaluation"],
                "contexts": ["research", "analysis", "études", "projects"]
            },
            "multimedia_creation": {
                "keywords": ["design", "creation", "multimedia", "image", "audio", "video", 
                           "graphique", "visuel", "photo", "musique", "podcast", "emission"],
                "contexts": ["création", "multimédia", "design", "content créatif"]
            },
            "administration_management": {
                "keywords": ["procedure", "proces", "management", "administration", "qualite", 
                           "organisation", "process", "workflow", "coordination", "planification"],
                "contexts": ["administration", "management", "organisation", "procédures"]
            }
        }
        
        # Calculer les scores thématiques pour chaque domaine
        domain_scores = {}
        
        for domain, data in thematic_domains.items():
            score = 0
            
            # Score basé sur les mots-clés dans le nom du fichier (poids fort)
            for keyword in data["keywords"]:
                if keyword in filename:
                    score += 3
            
            # Score basé sur les mots-clés dans le content (poids moyen)
            for keyword in data["keywords"]:
                score += content.count(keyword) * 2
            
            # Score spécialisé selon le type de fichier
            if file_type == "audio" and domain in ["rh_personnel", "administration_management", "communication_marketing"]:
                score += 1  # Bonus pour domaines compatibles audio
            elif file_type == "image" and domain in ["communication_marketing", "multimedia_creation", "legal_juridical", "finance_comptabilite"]:
                score += 1  # Bonus pour domaines compatibles image
            elif file_type == "document" and domain in ["legal_juridical", "projects_research", "technical_it"]:
                score += 1  # Bonus pour domaines compatibles document
            
            domain_scores[domain] = score
        
        # Sélectionner le domaine avec le meilleur score
        best_domain = max(domain_scores, key=domain_scores.get)
        
        # Si aucun score significatif, choisir selon le type de fichier
        if domain_scores[best_domain] == 0:
            if file_type == "audio":
                best_domain = "multimedia_creation"
            elif file_type == "image":
                best_domain = "multimedia_creation"
            else:
                best_domain = "administration_management"
        
        # Générer une sous-catégorie intelligente selon le contexte
        subcategory = self._generate_intelligent_subcategory(
            domain=best_domain,
            file_type=file_type,
            filename=filename,
            content=content,
            nlp_content=nlp_content,
            audio_content=audio_content,
            vision_content=vision_content
        )
        
        return best_domain, subcategory
    
    def _generate_intelligent_subcategory(self, domain: str, file_type: str, filename: str, 
                                        content: str, nlp_content: str, audio_content: str, 
                                        vision_content: str) -> str:
        """
        Génère une sous-catégorie intelligente basée sur l'analysis contextuelle fine
        """
        
        # analysisr le content le plus pertinent selon le type de fichier
        primary_content = ""
        if file_type == "audio":
            primary_content = audio_content
        elif file_type == "image":
            primary_content = vision_content
        else:
            primary_content = nlp_content
        
        # Si pas de content principal, utiliser tout le content
        if not primary_content.strip():
            primary_content = content
        
        # Générer la sous-catégorie selon le domaine et le contexte
        subcategory_generators = {
            "rh_personnel": self._generate_rh_subcategory,
            "finance_comptabilite": self._generate_finance_subcategory,
            "legal_juridical": self._generate_legal_subcategory,
            "technical_it": self._generate_technical_subcategory,
            "communication_marketing": self._generate_communication_subcategory,
            "projects_research": self._generate_research_subcategory,
            "multimedia_creation": self._generate_multimedia_subcategory,
            "administration_management": self._generate_administration_subcategory
        }
        
        generator = subcategory_generators.get(domain, lambda f, c, t: "documents_divers")
        return generator(filename, primary_content, file_type)
    
    def _generate_rh_subcategory(self, filename: str, content: str, file_type: str) -> str:
        """Génère sous-catégorie RH selon le contexte"""
        if any(kw in filename or kw in content for kw in ["cv", "curriculum", "candidat"]):
            return "candidatures_cv"
        elif any(kw in filename or kw in content for kw in ["entretien", "interview"]):
            return "entretiens_recrutement"
        elif any(kw in filename or kw in content for kw in ["formation", "cours", "apprentissage"]):
            return "formations_developpement"
        elif any(kw in filename or kw in content for kw in ["contrat", "travail", "emploi"]):
            return "contrats_emploi"
        elif any(kw in filename or kw in content for kw in ["salaire", "paie", "remuneration"]):
            return "management_paie"
        elif file_type == "audio":
            return "enregistrements_rh"
        else:
            return "documents_personnel"
    
    def _generate_finance_subcategory(self, filename: str, content: str, file_type: str) -> str:
        """Génère sous-catégorie Finance selon le contexte"""
        if any(kw in filename or kw in content for kw in ["facture", "invoice"]):
            if any(kw in content for kw in ["client", "vente"]):
                return "factures_clients"
            elif any(kw in content for kw in ["fournisseur", "achat"]):
                return "factures_fournisseurs"
            else:
                return "facturation"
        elif any(kw in filename or kw in content for kw in ["budget", "prevision", "planification"]):
            return "budgets_previsions"
        elif any(kw in filename or kw in content for kw in ["comptabilite", "bilan", "compte"]):
            return "comptabilite_generale"
        elif any(kw in filename or kw in content for kw in ["tresorerie", "cash", "liquidite"]):
            return "management_tresorerie"
        elif file_type == "image":
            return "documents_scannes"
        else:
            return "documents_financiers"
    
    def _generate_legal_subcategory(self, filename: str, content: str, file_type: str) -> str:
        """Génère sous-catégorie legal selon le contexte"""
        if any(kw in filename or kw in content for kw in ["contrat", "accord", "convention"]):
            return "contrats_accords"
        elif any(kw in filename or kw in content for kw in ["conformite", "rgpd", "compliance"]):
            return "conformite_reglementaire"
        elif any(kw in filename or kw in content for kw in ["procedure", "proces", "litige"]):
            return "procedures_legals"
        elif any(kw in filename or kw in content for kw in ["propriete", "brevet", "marque"]):
            return "propriete_intellectuelle"
        elif file_type == "image":
            return "documents_legals_scannes"
        else:
            return "documents_legals"
    
    def _generate_technical_subcategory(self, filename: str, content: str, file_type: str) -> str:
        """Génère sous-catégorie technical selon le contexte"""
        if any(kw in filename or kw in content for kw in ["config", "configuration", "setup"]):
            return "configurations_systeme"
        elif any(kw in filename or kw in content for kw in ["api", "documentation", "guide"]):
            return "documentation_technical"
        elif any(kw in filename or kw in content for kw in ["script", "code", "automation"]):
            return "scripts_automatisation"
        elif any(kw in filename or kw in content for kw in ["serveur", "infrastructure", "reseau"]):
            return "infrastructure_systemes"
        elif any(kw in filename or kw in content for kw in ["base", "donnees", "database"]):
            return "management_donnees"
        elif file_type == "image":
            return "captures_ecran_technicals"
        else:
            return "documentation_it"
    
    def _generate_communication_subcategory(self, filename: str, content: str, file_type: str) -> str:
        """Génère sous-catégorie Communication selon le contexte"""
        if any(kw in filename or kw in content for kw in ["presentation", "pitch", "slides"]):
            return "presentations_commerciales"
        elif any(kw in filename or kw in content for kw in ["campagne", "publicitaire", "advertising"]):
            return "campagnes_publicitaires"
        elif any(kw in filename or kw in content for kw in ["brand", "marque", "identite"]):
            return "identite_marque"
        elif any(kw in filename or kw in content for kw in ["newsletter", "communication", "info"]):
            return "communications_externes"
        elif file_type == "audio":
            return "contents_audio_marketing"
        elif file_type == "image":
            return "supports_visuels"
        else:
            return "supports_communication"
    
    def _generate_research_subcategory(self, filename: str, content: str, file_type: str) -> str:
        """Génère sous-catégorie research selon le contexte"""
        if any(kw in filename or kw in content for kw in ["rapport", "report", "synthese"]):
            return "rapports_etudes"
        elif any(kw in filename or kw in content for kw in ["analysis", "analysis", "evaluation"]):
            return "analysiss_donnees"
        elif any(kw in filename or kw in content for kw in ["veille", "benchmark", "concurrence"]):
            return "veille_concurrentielle"
        elif any(kw in filename or kw in content for kw in ["research", "investigation", "study"]):
            return "researchs_approfondies"
        elif any(kw in filename or kw in content for kw in ["projet", "project", "initiative"]):
            return "documentation_projects"
        elif file_type == "audio":
            return "interviews_research"
        else:
            return "etudes_researchs"
    
    def _generate_multimedia_subcategory(self, filename: str, content: str, file_type: str) -> str:
        """Génère sous-catégorie Multimédia selon le contexte"""
        if file_type == "audio":
            if any(kw in filename or kw in content for kw in ["podcast", "emission", "radio"]):
                return "podcasts_emissions"
            elif any(kw in filename or kw in content for kw in ["musique", "music", "son"]):
                return "contents_audio"
            else:
                return "enregistrements_multimedia"
        elif file_type == "image":
            if any(kw in filename or kw in content for kw in ["design", "creation", "graphique"]):
                return "creations_graphiques"
            elif any(kw in filename or kw in content for kw in ["photo", "photography", "image"]):
                return "photographies"
            else:
                return "contents_visuels"
        elif file_type == "video":
            return "productions_video"
        else:
            return "files_multimedia"
    
    def _generate_administration_subcategory(self, filename: str, content: str, file_type: str) -> str:
        """Génère sous-catégorie Administration selon le contexte"""
        if any(kw in filename or kw in content for kw in ["procedure", "process", "workflow"]):
            return "procedures_internes"
        elif any(kw in filename or kw in content for kw in ["reunion", "meeting", "assemblee"]):
            return "reunions_governance"
        elif any(kw in filename or kw in content for kw in ["qualite", "iso", "certification"]):
            return "qualite_certification"
        elif any(kw in filename or kw in content for kw in ["planning", "organisation", "coordination"]):
            return "organisation_planning"
        elif file_type == "audio":
            return "enregistrements_administratifs"
        else:
            return "documents_administratifs"
    
    def _determine_priority(self, content: str, is_sensitive: bool) -> str:
        """Détermine la priorité selon le content et la sensibilité"""
        if is_sensitive:
            return "haute"
        elif any(keyword in content for keyword in ['urgent', 'prioritaire', 'important', 'critique']):
            return "haute"
        elif any(keyword in content for keyword in ['routine', 'standard', 'normal']):
            return "basse"
        else:
            return "moyenne"
        
        # Fonction principale pour utilisation externe
async def organize_files_with_ai(file_analysiss: List[Dict[str, Any]], target_folder: str = "organized") -> FileOrganizationResponse:
    """
    Fonction principale pour organiser des files avec l'IA
    
    Args:
        file_analysiss: Liste des analysiss de files avec filepath, summary, warning
        target_folder: Dossier cible pour l'organisation
    
    Returns:
        FileOrganizationResponse avec les résultats
    """
    manager = IntelligentFileManager()
    return manager.organize_multiple_files(file_analysiss, target_folder)

if __name__ == "__main__":
    print("🗂️ Agent File Manager Intelligent - Test")
    
    # Exemple d'utilisation
    sample_analysiss = [
        {
            "filepath": "test_files/document_confidentiel.txt",
            "summary": "Document confidentiel contenant des informations personnelles",
            "warning": True
        },
        {
            "filepath": "test_files/rapport_public.txt", 
            "summary": "Rapport public d'analysis de marché",
            "warning": False
        }
    ]
    
    async def test():
        manager = IntelligentFileManager()
        result = manager.organize_multiple_files(sample_analysiss, "organized_test")
        report_path = manager.generate_organization_report(result, "organized_test")
        print(f"📋 Test terminé, rapport: {report_path}")
    
    asyncio.run(test())
