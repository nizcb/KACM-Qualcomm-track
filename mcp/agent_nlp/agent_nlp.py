#!/usr/bin/env python
"""
Agent IA NLP - Version Agent Autonome
====================================

Agent IA autonome qui peut :
- Analyser des fichiers et détecter les PII
- Raisonner sur les tâches à accomplir
- Planifier ses actions
- Utiliser des outils de manière autonome
- Gérer des demandes complexes

Retourne un JSON avec :
- file_path : chemin du fichier (str)
- resume : résumé du contenu (str) 
- warning : présence d'informations PII (bool)
"""

import os
import sys
import re
import json
import warnings
from typing import Dict, List, Any, Optional

# Suppression des avertissements Pydantic
warnings.filterwarnings("ignore", category=DeprecationWarning)

# LangChain imports
from langchain_community.llms import Ollama
from langchain.tools import tool

# Support PDF
try:
    import PyPDF2
    PDF_AVAILABLE = True
    print("✅ Support PDF disponible (PyPDF2)")
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ Support PDF non disponible (pip install PyPDF2)")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
    print("✅ Support PDF avancé disponible (PyMuPDF)")
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("⚠️ Support PDF avancé non disponible (pip install pymupdf)")

# ──────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.2:latest")

# Initialisation du LLM
llm = Ollama(
    model=LLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.7
)

# ──────────────────────────────────────────────────────────────────────────
# Regex patterns pour la détection PII
# ──────────────────────────────────────────────────────────────────────────
PII_REGEXES: Dict[str, re.Pattern] = {
    "EMAIL": re.compile(r"[\w\.\-]+@[\w\.-]+\.[a-z]{2,}", re.I),
    "PHONE": re.compile(r"\+?\d{1,3}[\s\-]?\d[\d\s\-]{8,}\d", re.I),
    "CARD": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
    "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b"),
    "SSN": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"),
}

# ──────────────────────────────────────────────────────────────────────────
# Fonctions utilitaires pour le traitement de fichiers
# ──────────────────────────────────────────────────────────────────────────

def extract_pdf_content(file_path: str) -> str:
    """
    Extrait le contenu texte d'un fichier PDF.
    
    Args:
        file_path: Chemin vers le fichier PDF
        
    Returns:
        Contenu texte du PDF
    """
    content = ""
    
    # Essai avec PyMuPDF d'abord (plus performant)
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(file_path)
            for page_num in range(doc.page_count):
                page = doc[page_num]
                content += page.get_text() + "\n"
            doc.close()
            return content
        except Exception as e:
            print(f"⚠️ Erreur PyMuPDF: {e}")
    
    # Fallback avec PyPDF2
    if PDF_AVAILABLE:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text() + "\n"
            return content
        except Exception as e:
            return f"Erreur lors de l'extraction PDF: {str(e)}"
    
    return "Aucune bibliothèque PDF disponible"

# ──────────────────────────────────────────────────────────────────────────
# Outils pour l'Agent IA
# ──────────────────────────────────────────────────────────────────────────

@tool
def read_file_tool(file_path: str) -> str:
    """
    Lit le contenu d'un fichier texte ou PDF.
    
    Args:
        file_path: Chemin vers le fichier à lire
        
    Returns:
        Contenu du fichier sous forme de chaîne de caractères
    """
    try:
        if not os.path.isabs(file_path):
            current_dir = os.getcwd()
            full_path = os.path.join(current_dir, file_path)
        else:
            full_path = file_path
        
        # Vérifier l'extension du fichier
        _, ext = os.path.splitext(full_path.lower())
        
        if ext == '.pdf':
            # Traitement PDF
            if PDF_AVAILABLE or PYMUPDF_AVAILABLE:
                content = extract_pdf_content(full_path)
                return f"Contenu du fichier PDF '{file_path}':\n{content}"
            else:
                return f"Erreur: Aucune bibliothèque PDF disponible pour lire '{file_path}'"
        else:
            # Traitement fichiers texte
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return f"Contenu du fichier '{file_path}':\n{content}"
    except Exception as e:
        return f"Erreur lors de la lecture du fichier '{file_path}': {str(e)}"

@tool
def generate_smart_summary_tool(text: str) -> str:
    """
    Génère un résumé intelligent avec LLM si disponible, sinon utilise un fallback.
    
    Args:
        text: Texte à résumer
        
    Returns:
        Résumé intelligent du texte en 3 phrases maximum
    """
    try:
        # Utilisation du LLM si disponible
        try:
            prompt = f"""Résume le texte suivant en 3 phrases maximum en français, en gardant les informations essentielles :

Texte : {text}

Résumé :
Ne commence jamais le résumé par une introduction de type "Voici le résumé" ou similaire.
"""
            response = llm.invoke(prompt)
            return f"Résumé intelligent généré: {response.strip()}"
        except Exception as llm_error:
            print(f"⚠️ Erreur LLM, passage en mode fallback : {llm_error}")
            
            # Fallback : résumé simple
            sentences = text.replace('\n', ' ').split('.')
            summary_sentences = []
            for sentence in sentences:
                if sentence.strip() and len(summary_sentences) < 3:
                    summary_sentences.append(sentence.strip())
            
            result = '. '.join(summary_sentences) + '.' if summary_sentences else "Résumé non disponible."
            return f"Résumé généré (fallback): {result}"
            
    except Exception as e:
        return f"Erreur lors du résumé: {str(e)}"

@tool
def detect_pii_tool(text: str) -> str:
    """
    Détecte les informations personnelles identifiables (PII) dans un texte avec IA.
    
    Args:
        text: Texte à analyser
        
    Returns:
        Information sur la présence de PII trouvées
    """
    try:
        # Utilisation du LLM si disponible pour une détection intelligente
        try:
            prompt = f"""Tu es un expert en sécurité des données. Analyse le texte suivant et détecte UNIQUEMENT les informations personnelles identifiables (PII) réelles présentes.

Types de PII à rechercher avec attention au contexte:
- Adresses email réelles (pas d'exemples fictifs)
- Numéros de téléphone réels
- Numéros de carte bancaire/crédit réels (pas 4242 4242 4242 4242)
- Codes IBAN/RIB réels
- Numéros de sécurité sociale réels
- Adresses postales complètes réelles
- Dates de naissance spécifiques
- Numéros d'identité/passeport réels
- Noms et prénoms complets de personnes réelles

IMPORTANT: Ignore les exemples fictifs, les données de test, les placeholders, et les données manifestement fausses.

Texte à analyser :
{text}

Réponds UNIQUEMENT par:
- "AUCUNE_PII" si aucune information personnelle réelle n'est détectée
- "PII_DETECTEES" si des PII réelles sont présentes

Réponse:"""
            
            response = llm.invoke(prompt)
            response = response.strip()
            
            if "AUCUNE_PII" in response.upper():
                return "✅ Aucune PII détectée par l'IA. Le fichier semble sûr."
            elif "PII_DETECTEES" in response.upper():
                pii_types = response.split(":")[1].strip() if ":" in response else response
                return f"⚠️ PII détectées par l'IA: {pii_types}. ATTENTION: Ce fichier contient des informations sensibles!"
            else:
                # Fallback si la réponse n'est pas dans le format attendu
                return f"🔍 Analyse IA: {response}"
                
        except Exception as llm_error:
            print(f"⚠️ Erreur LLM pour PII, passage en mode regex : {llm_error}")
            
            # Fallback : détection par regex
            pii_found = []
            
            pii_patterns = {
                "EMAIL": re.compile(r"[\w\.\-]+@[\w\.-]+\.[a-z]{2,}", re.I),
                "PHONE": re.compile(r"\+?\d{1,3}[\s\-]?\d[\d\s\-]{8,}\d", re.I),
                "CARD": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
                "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b"),
                "SSN": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"),
            }
            
            for label, pattern in pii_patterns.items():
                if pattern.search(text):
                    pii_found.append(label)
            
            if pii_found:
                return f"⚠️ PII détectées (regex): {', '.join(pii_found)}. ATTENTION: Ce fichier contient des informations sensibles!"
            else:
                return "✅ Aucune PII détectée (regex). Le fichier semble sûr."
            
    except Exception as e:
        return f"Erreur lors de la détection PII: {str(e)}"

@tool
def save_json_tool(data: str, filename: str) -> str:
    """
    Sauvegarde des données au format JSON dans un fichier.
    
    Args:
        data: Données à sauvegarder (format JSON string)
        filename: Nom du fichier de sortie
        
    Returns:
        Confirmation de la sauvegarde
    """
    try:
        # Parse du JSON pour validation
        json_data = json.loads(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return f"✅ Données sauvegardées avec succès dans '{filename}'"
    except Exception as e:
        return f"Erreur lors de la sauvegarde: {str(e)}"

@tool
def list_files_tool(directory: str = ".") -> str:
    """
    Liste les fichiers dans un répertoire.
    
    Args:
        directory: Répertoire à explorer (par défaut le répertoire courant)
        
    Returns:
        Liste des fichiers du répertoire
    """
    try:
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                files.append(f"📄 {item}")
            elif os.path.isdir(item_path):
                files.append(f"📁 {item}/")
        
        return f"Contenu du répertoire '{directory}':\n" + "\n".join(files)
    except Exception as e:
        return f"Erreur lors de la liste des fichiers: {str(e)}"

@tool
def process_multiple_files_tool(file_paths: str) -> str:
    """
    Traite plusieurs fichiers en une seule fois.
    
    Args:
        file_paths: Liste des chemins des fichiers séparés par des virgules
        
    Returns:
        Résumé du traitement de tous les fichiers
    """
    try:
        paths = [path.strip() for path in file_paths.split(',')]
        results = []
        
        for file_path in paths:
            if os.path.exists(file_path):
                try:
                    # Utiliser read_file_tool pour lire le contenu
                    content = read_file_tool(file_path)
                    
                    # Générer le résumé
                    summary = generate_smart_summary_tool(content)
                    
                    # Détecter les PII
                    pii_check = detect_pii_tool(content)
                    
                    results.append(f"📄 {file_path}: {summary[:100]}... | {pii_check}")
                except Exception as e:
                    results.append(f"❌ {file_path}: Erreur - {str(e)}")
            else:
                results.append(f"⚠️ {file_path}: Fichier non trouvé")
        
        return f"Traitement de {len(paths)} fichiers:\n" + "\n".join(results)
    except Exception as e:
        return f"Erreur lors du traitement multiple: {str(e)}"

# ──────────────────────────────────────────────────────────────────────────
# Agent IA Principal
# ──────────────────────────────────────────────────────────────────────────
class AgentIA:
    """Agent IA autonome pour l'analyse NLP avec capacité de raisonnement"""
    
    def __init__(self, llm=None, offline_mode=False):
        self.llm = llm
        self.offline_mode = offline_mode
        self.conversation_history = []  # Mémoire simple
        
        # Outils disponibles pour l'agent
        self.tools = [
            read_file_tool,
            generate_smart_summary_tool,
            detect_pii_tool,
            save_json_tool,
            list_files_tool,
            process_multiple_files_tool
        ]
        
        # Initialisation de l'agent simplifié
        self.agent = None
        if not self.offline_mode and self.llm:
            self.agent = self  # L'agent est lui-même avec ses outils
    
    def reason_and_act(self, query: str) -> str:
        """Raisonne et agit sur une requête donnée"""
        if not self.llm or self.offline_mode:
            return "Agent IA non disponible, utilisation du mode fallback"
        
        # Template de raisonnement ReAct simplifié
        prompt = f"""Tu es un agent IA spécialisé en analyse NLP et détection PII.

Tu as accès aux outils suivants:
1. read_file_tool(file_path) - Lit un fichier (texte ou PDF)
2. generate_smart_summary_tool(text) - Génère un résumé intelligent
3. detect_pii_tool(text) - Détecte les PII
4. save_json_tool(data, filename) - Sauvegarde en JSON
5. list_files_tool(directory) - Liste les fichiers
6. process_multiple_files_tool(file_paths) - Traite plusieurs fichiers (séparés par des virgules)

Utilise le format de raisonnement suivant:
Thought: [Ce que je dois faire]
Action: [Outil à utiliser]
Action Input: [Paramètres de l'outil]
Observation: [Résultat de l'action]
... (répète si nécessaire)
Final Answer: [Réponse finale]

Question: {query}

Commence par réfléchir:"""

        try:
            # Génération de la réponse avec raisonnement
            response = self.llm.invoke(prompt)
            
            # Traitement de la réponse pour extraire les actions
            return self._process_reasoning_response(response, query)
        except Exception as e:
            return f"Erreur lors du raisonnement: {e}"
    
    def _process_reasoning_response(self, response: str, original_query: str) -> str:
        """Traite la réponse de raisonnement et exécute les actions"""
        lines = response.split('\n')
        result = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Action:'):
                action = line.replace('Action:', '').strip()
                result.append(f"🔧 Action: {action}")
            elif line.startswith('Thought:'):
                thought = line.replace('Thought:', '').strip()
                result.append(f"💭 Réflexion: {thought}")
            elif line.startswith('Final Answer:'):
                answer = line.replace('Final Answer:', '').strip()
                result.append(f"✅ Réponse finale: {answer}")
        
        return '\n'.join(result) if result else response
    
    def process_file_with_reasoning(self, file_path: str) -> Dict[str, Any]:
        """Traite un fichier en utilisant le raisonnement de l'agent IA"""
        
        if self.agent and not self.offline_mode:
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
                print(f"🧠 Raisonnement de l'agent:\n{reasoning}\n")
                
                # Exécution directe des outils pour obtenir le résultat
                return self._execute_analysis(file_path)
                
            except Exception as e:
                print(f"Erreur avec l'agent IA: {e}")
                return self._fallback_process_file(file_path)
        else:
            return self._fallback_process_file(file_path)
    
    def _generate_smart_summary(self, content: str) -> str:
        """Génère un résumé intelligent avec LLM si disponible"""
        if not self.offline_mode and self.llm:
            try:
                prompt = f"""Résume le texte suivant en 3 phrases maximum en français, en gardant les informations essentielles :

Texte : {content}

Résumé :
Ne commence jamais le résumé par une introduction de type "Voici le résumé" ou similaire.
"""
                response = llm.invoke(prompt)
                return response.strip()
            except Exception as e:
                print(f"⚠️ Erreur LLM, passage en mode offline : {e}")
        
        # Fallback : résumé simple
        sentences = content.replace('\n', ' ').split('.')
        summary_sentences = []
        for sentence in sentences:
            if sentence.strip() and len(summary_sentences) < 3:
                summary_sentences.append(sentence.strip())
        
        return '. '.join(summary_sentences) + '.' if summary_sentences else "Résumé non disponible."

    def _detect_pii_intelligent(self, content: str) -> bool:
        """Détecte les PII avec IA si disponible, sinon utilise regex"""
        if not self.offline_mode and self.llm:
            try:
                prompt = f"""Tu es un expert en sécurité des données. Analyse le texte suivant et détecte UNIQUEMENT les informations personnelles identifiables (PII) réelles présentes.

Types de PII à rechercher avec attention au contexte:
- Adresses email réelles (pas d'exemples fictifs)
- Numéros de téléphone réels
- Numéros de carte bancaire/crédit réels (pas 4242 4242 4242 4242)
- Codes IBAN/RIB réels
- Numéros de sécurité sociale réels
- Adresses postales complètes réelles
- Dates de naissance spécifiques
- Numéros d'identité/passeport réels
- Noms et prénoms complets de personnes réelles

IMPORTANT: Ignore les exemples fictifs, les données de test, les placeholders, et les données manifestement fausses.

Texte à analyser :
{content}

Réponds UNIQUEMENT par:
- "AUCUNE_PII" si aucune information personnelle réelle n'est détectée
- "PII_DETECTEES" si des PII réelles sont présentes

Réponse:"""
                
                response = self.llm.invoke(prompt)
                response = response.strip().upper()
                
                if "PII_DETECTEES" in response:
                    print("🔍 PII détectées par l'IA")
                    return True
                else:
                    print("✅ Aucune PII détectée par l'IA")
                    return False
                    
            except Exception as e:
                print(f"⚠️ Erreur LLM pour PII, passage en mode regex : {e}")
        
        # Fallback : détection par regex
        pii_patterns = {
            "EMAIL": re.compile(r"[\w\.\-]+@[\w\.-]+\.[a-z]{2,}", re.I),
            "PHONE": re.compile(r"\+?\d{1,3}[\s\-]?\d[\d\s\-]{8,}\d", re.I),
            "CARD": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
            "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b"),
            "SSN": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"),
        }
        
        for label, pattern in pii_patterns.items():
            if pattern.search(content):
                print(f"🔍 PII détectées par regex: {label}")
                return True
        
        print("✅ Aucune PII détectée par regex")
        return False
    def _execute_analysis(self, file_path: str) -> Dict[str, Any]:
        """Exécute l'analyse avec les outils disponibles"""
        try:
            # Lecture du fichier directement
            print("🔧 Lecture du fichier...")
            if not os.path.isabs(file_path):
                current_dir = os.getcwd()
                full_path = os.path.join(current_dir, file_path)
            else:
                full_path = file_path
            
            # Vérifier l'extension du fichier
            _, ext = os.path.splitext(full_path.lower())
            
            if ext == '.pdf':
                # Traitement PDF
                if PDF_AVAILABLE or PYMUPDF_AVAILABLE:
                    content = extract_pdf_content(full_path)
                    print(f"📄 Contenu PDF extrait ({len(content)} caractères)")
                else:
                    content = "Erreur: Aucune bibliothèque PDF disponible"
                    print("⚠️ Aucune bibliothèque PDF disponible")
            else:
                # Traitement fichiers texte
                with open(full_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                print(f"📄 Contenu texte lu ({len(content)} caractères)")
            
            # Génération du résumé intelligent
            print("🔧 Génération du résumé...")
            resume = self._generate_smart_summary(content)
            
            # Détection PII intelligente
            print("🔧 Détection intelligente des PII...")
            pii_found = self._detect_pii_intelligent(content)
            
            # Construction du résultat final
            result = {
                "file_path": os.path.abspath(file_path),
                "resume": resume,
                "warning": pii_found
            }
            
            # Sauvegarde automatique
            output_file = f"{os.path.splitext(os.path.basename(file_path))[0]}_analysis.json"
            print(f"🔧 Sauvegarde dans {output_file}...")
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
        """Traitement de fichier en mode fallback (sans agent IA)"""
        try:
            # Lecture du fichier directement
            print("📁 Lecture du fichier...")
            if not os.path.isabs(file_path):
                current_dir = os.getcwd()
                full_path = os.path.join(current_dir, file_path)
            else:
                full_path = file_path
            
            # Vérifier l'extension du fichier
            _, ext = os.path.splitext(full_path.lower())
            
            if ext == '.pdf':
                # Traitement PDF
                if PDF_AVAILABLE or PYMUPDF_AVAILABLE:
                    content = extract_pdf_content(full_path)
                    print(f"📄 Contenu PDF extrait ({len(content)} caractères)")
                else:
                    content = "Erreur: Aucune bibliothèque PDF disponible"
                    print("⚠️ Aucune bibliothèque PDF disponible")
            else:
                # Traitement fichiers texte
                with open(full_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                print(f"📄 Contenu texte lu ({len(content)} caractères)")
            
            # Génération du résumé intelligent
            print("✍️ Génération du résumé...")
            resume = self._generate_smart_summary(content)
            
            # Détection PII intelligente
            print("🔍 Détection intelligente des PII...")
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
        """Interface de chat avec l'agent IA"""
        if self.agent and not self.offline_mode:
            try:
                return self.reason_and_act(message)
            except Exception as e:
                return f"Erreur lors du chat: {e}"
        else:
            return "Mode offline activé. Utilisez les commandes directes pour traiter les fichiers."
    
    def process_multiple_files_with_reasoning(self, file_paths: List[str]) -> Dict[str, Any]:
        """Traite plusieurs fichiers en utilisant le raisonnement de l'agent IA"""
        results = {}
        summary_results = []
        total_warnings = 0
        
        print(f"🔄 Traitement de {len(file_paths)} fichiers...")
        
        for i, file_path in enumerate(file_paths, 1):
            print(f"\n📄 Traitement du fichier {i}/{len(file_paths)}: {file_path}")
            
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
                print(f"❌ Erreur lors du traitement de {file_path}: {e}")
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
                "processing_date": "2025-07-06"
            },
            "files": summary_results,
            "detailed_results": results
        }
        
        # Sauvegarder le résultat global
        batch_output_file = f"batch_analysis_{len(file_paths)}_files.json"
        print(f"\n💾 Sauvegarde du résultat global dans {batch_output_file}...")
        
        with open(batch_output_file, 'w', encoding='utf-8') as f:
            json.dump(batch_summary, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Traitement terminé: {len(results)} fichiers traités, {total_warnings} avec PII")
        return batch_summary

# ──────────────────────────────────────────────────────────────────────────
# Fonctions utilitaires
# ──────────────────────────────────────────────────────────────────────────
def process_file(file_path: str, offline_mode: bool = False) -> Dict[str, Any]:
    """Traite un fichier et retourne le résultat JSON"""
    agent = AgentIA(llm if not offline_mode else None, offline_mode)
    return agent.process_file_with_reasoning(file_path)

def process_multiple_files(file_paths: List[str], offline_mode: bool = False) -> Dict[str, Any]:
    """Traite plusieurs fichiers et retourne le résultat JSON global"""
    agent = AgentIA(llm if not offline_mode else None, offline_mode)
    return agent.process_multiple_files_with_reasoning(file_paths)

def process_directory(directory_path: str, file_extensions: List[str] = None, offline_mode: bool = False) -> Dict[str, Any]:
    """Traite tous les fichiers d'un répertoire avec extensions spécifiées"""
    if file_extensions is None:
        file_extensions = ['.txt', '.py', '.md', '.json', '.csv', '.xml', '.html', '.log', '.pdf']
    
    file_paths = []
    
    # Parcourir le répertoire
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file.lower())
            
            if ext in file_extensions:
                file_paths.append(file_path)
    
    if not file_paths:
        print(f"⚠️ Aucun fichier trouvé dans {directory_path} avec les extensions {file_extensions}")
        return {"error": "Aucun fichier trouvé"}
    
    print(f"📁 Traitement du répertoire {directory_path}: {len(file_paths)} fichiers trouvés")
    return process_multiple_files(file_paths, offline_mode)

def process_file_patterns(patterns: List[str], offline_mode: bool = False) -> Dict[str, Any]:
    """Traite des fichiers selon des patterns (glob patterns)"""
    import glob
    
    file_paths = []
    
    for pattern in patterns:
        matched_files = glob.glob(pattern)
        file_paths.extend(matched_files)
    
    # Supprimer les doublons
    file_paths = list(set(file_paths))
    
    if not file_paths:
        print(f"⚠️ Aucun fichier trouvé avec les patterns {patterns}")
        return {"error": "Aucun fichier trouvé"}
    
    print(f"🔍 Traitement par patterns: {len(file_paths)} fichiers trouvés")
    return process_multiple_files(file_paths, offline_mode)

def process_file_to_json_string(file_path: str, offline_mode: bool = False) -> str:
    """Traite un fichier et retourne le JSON sous forme de string"""
    result = process_file(file_path, offline_mode)
    return json.dumps(result, indent=2, ensure_ascii=False)

def save_result_to_file(file_path: str, output_file: str, offline_mode: bool = False):
    """Traite un fichier et sauvegarde le résultat"""
    result = process_file(file_path, offline_mode)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Résultat sauvegardé dans : {output_file}")

def chat_mode():
    """Mode chat interactif avec l'agent IA"""
    print("🤖 Mode Chat Interactif - Agent IA NLP")
    print("=====================================")
    print("Tapez 'quit' pour quitter, 'help' pour l'aide")
    
    agent = AgentIA(llm, offline_mode=False)
    
    if not agent.agent:
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
- Listez les fichiers: "Quels fichiers sont disponibles?"
- Posez des questions: "Résume-moi ce document"
- Détection PII: "Y a-t-il des informations sensibles?"
- quit/exit: Quitter le chat

📄 Formats supportés: .txt, .py, .md, .json, .csv, .xml, .html, .log, .pdf
                """)
                continue
            
            if not user_input:
                continue
            
            print("\n🤖 Agent IA: ", end="")
            response = agent.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")

def test_agent():
    """Test de l'agent IA avec différents fichiers"""
    print("=== Test Agent IA NLP ===\n")
    
    # Test 1: Fichier sans PII
    print("1. Test fichier sans PII avec Agent IA")
    print("-" * 40)
    try:
        if os.path.exists("recit.txt"):
            agent = AgentIA(llm, offline_mode=False)
            
            if agent.agent:
                print("🤖 Test avec Agent IA...")
                result = agent.process_file_with_reasoning("recit.txt")
            else:
                print("⚠️ Agent IA non disponible, test en mode offline...")
                result = process_file("recit.txt", offline_mode=True)
            
            print(f"File path: {result['file_path']}")
            print(f"Resume: {result['resume'][:100]}...")
            print(f"Warning: {result['warning']}")
        else:
            print("Fichier recit.txt non trouvé")
    except Exception as e:
        print(f"Erreur: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Fichier avec PII
    print("2. Test fichier avec PII avec Agent IA")
    print("-" * 40)
    
    test_content = """
    Rapport de contact client.
    
    Nom : Marie Dupont
    Email : marie.dupont@email.com
    Téléphone : +33 6 12 34 56 78
    Carte : 4242 4242 4242 4242
    
    Demande de remboursement.
    """
    
    with open("test_pii.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        agent = AgentIA(llm, offline_mode=False)
        
        if agent.agent:
            print("🤖 Test avec Agent IA...")
            result = agent.process_file_with_reasoning("test_pii.txt")
        else:
            print("⚠️ Agent IA non disponible, test en mode offline...")
            result = process_file("test_pii.txt", offline_mode=True)
        
        print(f"File path: {result['file_path']}")
        print(f"Resume: {result['resume'][:100]}...")
        print(f"Warning: {result['warning']}")
        
        # Affichage du JSON complet
        print("\nJSON complet :")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        if os.path.exists("test_pii.txt"):
            os.remove("test_pii.txt")
    
    print("\n" + "="*60 + "\n")
    
    # Test 3: Traitement en lot
    print("3. Test traitement en lot")
    print("-" * 40)
    test_batch_processing()

def test_batch_processing():
    """Test du traitement en lot avec plusieurs fichiers"""
    print("=== Test Traitement en Lot ===\n")
    
    # Créer des fichiers de test
    test_files = {
        "test_batch_1.txt": "Ceci est un document de test simple sans informations sensibles.",
        "test_batch_2.txt": """
        Rapport client confidentiel
        Nom: Jean Dupont
        Email: jean.dupont@test.com
        Téléphone: +33 6 12 34 56 78
        """,
        "test_batch_3.txt": "Un autre document de test avec du contenu normal pour l'analyse."
    }
    
    # Créer les fichiers
    for filename, content in test_files.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    try:
        print("1. Test du traitement en lot de 3 fichiers")
        print("-" * 50)
        
        file_paths = list(test_files.keys())
        agent = AgentIA(llm, offline_mode=False)
        
        if agent.agent:
            print("🤖 Test avec Agent IA...")
            result = agent.process_multiple_files_with_reasoning(file_paths)
        else:
            print("⚠️ Agent IA non disponible, test en mode offline...")
            result = process_multiple_files(file_paths, offline_mode=True)
        
        print(f"Fichiers traités: {result['batch_info']['total_files']}")
        print(f"Fichiers avec PII: {result['batch_info']['files_with_pii']}")
        
        # Afficher un résumé
        for file_info in result['files']:
            pii_status = "⚠️ PII" if file_info['has_pii'] else "✅ Safe"
            print(f"  {file_info['file']}: {pii_status}")
            
    except Exception as e:
        print(f"Erreur lors du test: {e}")
    finally:
        # Nettoyer les fichiers de test
        for filename in test_files.keys():
            if os.path.exists(filename):
                os.remove(filename)
        
        # Nettoyer le fichier de résultat
        if os.path.exists("batch_analysis_3_files.json"):
            os.remove("batch_analysis_3_files.json")

# ──────────────────────────────────────────────────────────────────────────
# Interface en ligne de commande
# ──────────────────────────────────────────────────────────────────────────
def main():
    """Interface principale"""
    if len(sys.argv) < 2:
        print("Agent IA NLP - Analyse Intelligente et Détection PII")
        print("=========================================================")
        print("🤖 Agent IA autonome avec capacité de raisonnement")
        print("📄 Support PDF intégré (PyPDF2 + PyMuPDF)")
        print("🔄 Traitement en lot de multiples fichiers")
        print("\nUsage:")
        print("  python agent_nlp.py <fichier>                    # Analyse avec agent IA")
        print("  python agent_nlp.py <fichier> <sortie.json>      # Sauvegarde personnalisée")
        print("  python agent_nlp.py <fichier> --offline          # Mode offline (sans agent IA)")
        print("  python agent_nlp.py --batch <fichier1,fichier2>  # Traitement en lot")
        print("  python agent_nlp.py --directory <dossier>        # Traitement d'un dossier")
        print("  python agent_nlp.py --pattern <pattern>          # Traitement par pattern")
        print("  python agent_nlp.py --test                       # Tests")
        print("  python agent_nlp.py --chat                       # Mode chat interactif")
        print("\nExemples:")
        print("  python agent_nlp.py recit.txt                    # → recit_analysis.json")
        print("  python agent_nlp.py document.pdf                # → document_analysis.json")
        print("  python agent_nlp.py --batch recit.txt,rapport.txt # → batch_analysis_2_files.json")
        print("  python agent_nlp.py --directory ./documents      # → batch_analysis_X_files.json")
        print("  python agent_nlp.py --pattern \"*.txt\"           # → batch_analysis_X_files.json")
        print("\nFormats supportés:")
        print("  📄 Texte: .txt, .py, .md, .json, .csv, .xml, .html, .log")
        print("  📄 PDF: .pdf (extraction automatique du texte)")
        print("\nCapacités de l'Agent IA:")
        print("  🧠 Raisonnement autonome sur les tâches")
        print("  📊 Planification d'actions")
        print("  🔧 Utilisation d'outils spécialisés")
        print("  💭 Mémoire conversationnelle")
        print("  🔍 Analyse contextuelle avancée")
        print("  📄 Support PDF natif avec extraction de texte")
        print("  🔄 Traitement en lot de multiples fichiers")
        print("\nFormat de sortie JSON:")
        print('  Fichier unique: {"file_path": "...", "resume": "...", "warning": true/false}')
        print('  Traitement en lot: {"batch_info": {...}, "files": [...], "detailed_results": {...}}')
        return
    
    if sys.argv[1] == "--test":
        test_agent()
        return
    
    if sys.argv[1] == "--chat":
        chat_mode()
        return
    
    # Traitement en lot
    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("❌ Erreur: Veuillez spécifier les fichiers à traiter")
            print("Exemple: python agent_nlp.py --batch fichier1.txt,fichier2.txt")
            return
        
        file_paths = [path.strip() for path in sys.argv[2].split(',')]
        offline_mode = len(sys.argv) > 3 and sys.argv[3] == "--offline"
        
        try:
            print(f"🔄 Traitement en lot de {len(file_paths)} fichiers...")
            result = process_multiple_files(file_paths, offline_mode)
            print(f"✅ Traitement terminé! Résultat sauvegardé dans le fichier JSON")
        except Exception as e:
            print(f"❌ Erreur lors du traitement en lot: {e}")
        return
    
    # Traitement d'un dossier
    if sys.argv[1] == "--directory":
        if len(sys.argv) < 3:
            print("❌ Erreur: Veuillez spécifier le dossier à traiter")
            print("Exemple: python agent_nlp.py --directory ./documents")
            return
        
        directory_path = sys.argv[2]
        offline_mode = len(sys.argv) > 3 and sys.argv[3] == "--offline"
        
        try:
            print(f"📁 Traitement du dossier {directory_path}...")
            result = process_directory(directory_path, offline_mode=offline_mode)
            print(f"✅ Traitement terminé! Résultat sauvegardé dans le fichier JSON")
        except Exception as e:
            print(f"❌ Erreur lors du traitement du dossier: {e}")
        return
    
    # Traitement par pattern
    if sys.argv[1] == "--pattern":
        if len(sys.argv) < 3:
            print("❌ Erreur: Veuillez spécifier le pattern à traiter")
            print("Exemple: python agent_nlp.py --pattern \"*.txt\"")
            return
        
        patterns = [sys.argv[2]]
        offline_mode = len(sys.argv) > 3 and sys.argv[3] == "--offline"
        
        try:
            print(f"🔍 Traitement par pattern {patterns[0]}...")
            result = process_file_patterns(patterns, offline_mode=offline_mode)
            print(f"✅ Traitement terminé! Résultat sauvegardé dans le fichier JSON")
        except Exception as e:
            print(f"❌ Erreur lors du traitement par pattern: {e}")
        return
    
    # Traitement d'un fichier unique (comportement original)
    file_path = sys.argv[1]
    output_file = None
    offline_mode = False
    
    # Analyse des arguments
    if len(sys.argv) > 2:
        if sys.argv[2] == "--offline":
            offline_mode = True
        elif sys.argv[2].endswith('.json'):
            output_file = sys.argv[2]
        
        if len(sys.argv) > 3 and sys.argv[3] == "--offline":
            offline_mode = True
    
    try:
        if not offline_mode:
            print("🤖 Initialisation de l'Agent IA...")
            try:
                test_response = llm.invoke("Test")
                print("✅ Agent IA prêt")
            except:
                print("⚠️ Connexion Ollama échouée, passage en mode offline")
                offline_mode = True
        else:
            print("📋 Mode offline activé")
        
        print(f"📂 Traitement du fichier : {file_path}")
        print(f"🔧 Mode : {'Offline (Fallback)' if offline_mode else 'Agent IA'}")
        
        if output_file:
            save_result_to_file(file_path, output_file, offline_mode)
        else:
            # Sauvegarde automatique avec nom basé sur le fichier d'entrée
            result = process_file(file_path, offline_mode)
            json_output = json.dumps(result, indent=2, ensure_ascii=False)
            
            # Génération du nom de fichier de sortie
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = f"{base_name}_analysis.json"
            
            # Sauvegarde
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print("\n📋 Résultat JSON :")
            print(json_output)
            print(f"\n✅ Résultat sauvegardé dans : {output_file}")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    main()
