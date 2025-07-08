#!/usr/bin/env python3
"""
Interface Interactive Complète - Système MCP Multi-Agents
=========================================================

Interface terminal interactive complète pour :
- Tester le système MCP multi-agents
- Démonstration complète du workflow
- Gestion des fichiers et dossiers
- Interaction avec tous les agents (NLP, Vision, Audio, Security, File Manager)
- Authentification et sécurité
- Rapports détaillés et logs
- Interface utilisateur intuitive

Fonctionnalités :
- Scan et analyse de répertoires
- Détection PII avancée
- Traitement multi-modal (texte, image, audio)
- Chiffrement et sécurisation
- Recherche intelligente
- Gestion du vault sécurisé
- Statistiques et rapports
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import uuid
import getpass
import subprocess
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich.tree import Tree
from rich.columns import Columns
from rich.rule import Rule
import mimetypes

# Configuration Rich Console
console = Console()
error_console = Console(stderr=True, style="bold red")

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/interactive_demo.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────
# Modèles de données
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class FileAnalysis:
    """Résultat d'analyse d'un fichier"""
    file_path: str
    file_name: str
    file_type: str
    mime_type: str
    size: int
    hash_md5: str
    agent_used: str
    summary: str
    pii_detected: List[str]
    warning_level: str  # 'safe', 'warning', 'critical'
    processing_time: float
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class SessionData:
    """Données de session"""
    session_id: str
    user_id: str
    start_time: datetime
    current_directory: str
    files_analyzed: List[FileAnalysis]
    total_files: int
    sensitive_files: int
    security_actions: List[Dict[str, Any]]
    vault_status: str

# ──────────────────────────────────────────────────────────────────────────
# Simulateur MCP Multi-Agents
# ──────────────────────────────────────────────────────────────────────────

class MCPAgentSimulator:
    """Simulateur des agents MCP pour démonstration"""
    
    def __init__(self):
        self.agents = {
            'orchestrator': {'status': 'running', 'port': 8000},
            'nlp': {'status': 'running', 'port': 8001},
            'vision': {'status': 'running', 'port': 8002},
            'audio': {'status': 'running', 'port': 8003},
            'file_manager': {'status': 'running', 'port': 8004},
            'security': {'status': 'running', 'port': 8005}
        }
        
        # Patterns PII sophistiqués
        self.pii_patterns = {
            'EMAIL': r'[\w\.-]+@[\w\.-]+\.\w+',
            'PHONE': r'[\d\s\-\+\(\)]{10,}',
            'CREDIT_CARD': r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
            'IBAN': r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}[A-Z0-9]{1,16}\b',
            'SSN': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'PASSPORT': r'\b[A-Z]{2}\d{7}\b',
            'NATIONAL_ID': r'\b\d{13}\b'
        }
        
        # Types de fichiers sensibles
        self.sensitive_keywords = [
            'sensible', 'secret', 'confidentiel', 'prive', 'carte', 'bancaire',
            'iban', 'passeport', 'cni', 'ordonnance', 'medical', 'paie',
            'bulletin', 'facture', 'contrat', 'juridique', 'personnel'
        ]
        
        # Simulateur de réponses IA
        self.ai_responses = {
            'text': [
                "Document contenant des informations personnelles détectées",
                "Texte analysé avec détection automatique de contenu sensible",
                "Analyse NLP complète avec classification du contenu",
                "Document traité avec extraction d'entités nommées"
            ],
            'image': [
                "Image analysée avec OCR et détection d'objets sensibles",
                "Contenu visuel traité avec reconnaissance de formes",
                "Analyse d'image avec détection de documents officiels",
                "Traitement vision avec identification de données personnelles"
            ],
            'audio': [
                "Audio transcrit avec analyse de contenu vocal",
                "Fichier audio traité avec détection de conversation",
                "Transcription complète avec analyse sémantique",
                "Contenu audio analysé pour informations sensibles"
            ]
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Retourne le statut de tous les agents"""
        return self.agents.copy()
    
    def analyze_file(self, file_path: str) -> FileAnalysis:
        """Simule l'analyse d'un fichier par les agents MCP"""
        
        start_time = time.time()
        
        # Informations sur le fichier
        path_obj = Path(file_path)
        file_name = path_obj.name
        file_size = path_obj.stat().st_size if path_obj.exists() else 0
        
        # Détection du type de fichier
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'
        
        # Classification du type
        file_type = 'other'
        agent_used = 'nlp'
        
        extension = path_obj.suffix.lower()
        if extension in ['.txt', '.md', '.json', '.csv', '.pdf', '.docx']:
            file_type = 'text'
            agent_used = 'nlp'
        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            file_type = 'image'
            agent_used = 'vision'
        elif extension in ['.mp3', '.wav', '.m4a', '.ogg']:
            file_type = 'audio'
            agent_used = 'audio'
        
        # Simulation du temps de traitement
        processing_time = {
            'nlp': 0.5,
            'vision': 1.2,
            'audio': 2.0
        }.get(agent_used, 0.5)
        
        time.sleep(processing_time * 0.1)  # Simulation rapide
        
        # Génération du hash
        try:
            hash_md5 = hashlib.md5(file_path.encode()).hexdigest()[:8]
        except:
            hash_md5 = "unknown"
        
        # Détection PII et niveau de warning
        pii_detected = []
        warning_level = 'safe'
        
        # Analyse basée sur le nom du fichier
        file_name_lower = file_name.lower()
        for keyword in self.sensitive_keywords:
            if keyword in file_name_lower:
                pii_detected.append(keyword.upper())
                warning_level = 'warning' if warning_level == 'safe' else 'critical'
        
        # Simulation d'analyse de contenu
        if file_type == 'text' and path_obj.exists():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()[:1000]  # Lecture partielle
                    
                # Détection de patterns PII
                import re
                for pii_type, pattern in self.pii_patterns.items():
                    if re.search(pattern, content):
                        pii_detected.append(pii_type)
                        warning_level = 'critical'
            except:
                pass
        
        # Génération du résumé
        summary = f"Fichier {file_type} analysé par l'agent {agent_used}"
        if pii_detected:
            summary += f" - PII détectées: {', '.join(pii_detected)}"
        
        # Sélection d'une réponse IA
        ai_summary = self.ai_responses.get(file_type, ["Fichier analysé"])[0]
        
        end_time = time.time()
        
        return FileAnalysis(
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            mime_type=mime_type,
            size=file_size,
            hash_md5=hash_md5,
            agent_used=agent_used,
            summary=ai_summary,
            pii_detected=pii_detected,
            warning_level=warning_level,
            processing_time=end_time - start_time,
            confidence=0.95 if pii_detected else 0.85,
            metadata={
                'agent_version': '1.0.0',
                'analysis_method': f'{agent_used}_mcp',
                'timestamp': datetime.now().isoformat()
            }
        )

# ──────────────────────────────────────────────────────────────────────────
# Scanner de fichiers avancé
# ──────────────────────────────────────────────────────────────────────────

class AdvancedFileScanner:
    """Scanner de fichiers avancé avec filtres"""
    
    def __init__(self):
        self.supported_extensions = {
            '.txt', '.md', '.json', '.csv', '.xml', '.html', '.log',
            '.pdf', '.docx', '.doc', '.rtf', '.odt',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
            '.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac',
            '.mp4', '.avi', '.mov', '.mkv', '.wmv'
        }
        
        self.excluded_dirs = {
            '.git', '__pycache__', '.vscode', 'node_modules', '.pytest_cache',
            '.DS_Store', 'Thumbs.db', '.env', '.venv', 'venv', 'env'
        }
    
    def scan_directory(self, directory: str, max_files: int = 100) -> List[str]:
        """Scanne un répertoire et retourne les fichiers supportés"""
        
        files_found = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return files_found
        
        try:
            for item in directory_path.rglob('*'):
                # Ignorer les répertoires exclus
                if any(excluded in item.parts for excluded in self.excluded_dirs):
                    continue
                
                # Vérifier si c'est un fichier supporté
                if item.is_file() and item.suffix.lower() in self.supported_extensions:
                    files_found.append(str(item))
                    
                    # Limite pour éviter les scans trop longs
                    if len(files_found) >= max_files:
                        break
            
            return files_found
            
        except Exception as e:
            logger.error(f"Erreur lors du scan: {e}")
            return files_found

# ──────────────────────────────────────────────────────────────────────────
# Interface Interactive Principale
# ──────────────────────────────────────────────────────────────────────────

class InteractiveDemo:
    """Interface interactive complète pour le système MCP"""
    
    def __init__(self):
        self.session = SessionData(
            session_id=str(uuid.uuid4())[:8],
            user_id="demo_user",
            start_time=datetime.now(),
            current_directory=".",
            files_analyzed=[],
            total_files=0,
            sensitive_files=0,
            security_actions=[],
            vault_status="locked"
        )
        
        self.mcp_simulator = MCPAgentSimulator()
        self.file_scanner = AdvancedFileScanner()
        self.authenticated = False
        self.demo_mode = True
    
    def show_header(self):
        """Affiche l'en-tête du système"""
        console.clear()
        
        header = Text("🎯 SYSTÈME MCP MULTI-AGENTS - INTERFACE INTERACTIVE COMPLÈTE", style="bold blue")
        console.print(Panel(header, style="blue"))
        
        # Informations de session
        session_info = f"""
Session ID: {self.session.session_id}
Utilisateur: {self.session.user_id}
Démarrage: {self.session.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Répertoire: {self.session.current_directory}
Statut Vault: {self.session.vault_status}
        """
        console.print(Panel(session_info.strip(), title="Informations de Session", style="green"))
    
    def show_agent_status(self):
        """Affiche le statut des agents MCP"""
        
        table = Table(title="🤖 Statut des Agents MCP")
        table.add_column("Agent", style="cyan")
        table.add_column("Statut", style="green")
        table.add_column("Port", style="yellow")
        table.add_column("Fonction", style="white")
        
        agent_functions = {
            'orchestrator': 'Coordination générale',
            'nlp': 'Traitement du langage naturel',
            'vision': 'Analyse d\'images et OCR',
            'audio': 'Traitement audio et transcription',
            'file_manager': 'Gestion des fichiers',
            'security': 'Sécurité et chiffrement'
        }
        
        for agent_name, agent_info in self.mcp_simulator.get_agent_status().items():
            status_emoji = "✅" if agent_info['status'] == 'running' else "❌"
            table.add_row(
                agent_name,
                f"{status_emoji} {agent_info['status']}",
                str(agent_info['port']),
                agent_functions.get(agent_name, "Fonction inconnue")
            )
        
        console.print(table)
    
    def authenticate_user(self):
        """Authentification utilisateur"""
        
        console.print("\n🔐 Authentification requise", style="bold yellow")
        
        username = Prompt.ask("Nom d'utilisateur", default="demo")
        password = Prompt.ask("Mot de passe", password=True, default="demo")
        
        # Simulation d'authentification
        if username == "demo" and password == "demo":
            self.authenticated = True
            self.session.user_id = username
            console.print("✅ Authentification réussie", style="green")
            self.session.vault_status = "unlocked"
            return True
        else:
            console.print("❌ Échec d'authentification", style="red")
            return False
    
    def select_directory(self):
        """Sélection du répertoire à analyser"""
        
        console.print("\n📁 Sélection du répertoire à analyser", style="bold cyan")
        
        # Répertoires suggérés
        suggested_dirs = [
            "test_files",
            "mcp/test_files", 
            "agents/vision/test_images",
            "."
        ]
        
        console.print("Répertoires suggérés :")
        for i, dir_path in enumerate(suggested_dirs, 1):
            status = "✅" if Path(dir_path).exists() else "❌"
            console.print(f"{i}. {status} {dir_path}")
        
        console.print(f"{len(suggested_dirs) + 1}. Spécifier un répertoire personnalisé")
        
        choice = Prompt.ask("Votre choix", choices=[str(i) for i in range(1, len(suggested_dirs) + 2)])
        
        if choice == str(len(suggested_dirs) + 1):
            directory = Prompt.ask("Chemin du répertoire")
        else:
            directory = suggested_dirs[int(choice) - 1]
        
        if Path(directory).exists():
            self.session.current_directory = directory
            console.print(f"✅ Répertoire sélectionné: {directory}", style="green")
            return True
        else:
            console.print(f"❌ Répertoire inexistant: {directory}", style="red")
            return False
    
    def scan_and_analyze(self):
        """Scan et analyse des fichiers"""
        
        console.print(f"\n🔍 Scan du répertoire: {self.session.current_directory}", style="bold yellow")
        
        # Scan des fichiers
        with console.status("[spinner] Scan en cours..."):
            files_found = self.file_scanner.scan_directory(self.session.current_directory)
        
        if not files_found:
            console.print("❌ Aucun fichier trouvé", style="red")
            return
        
        console.print(f"📊 {len(files_found)} fichiers détectés", style="green")
        
        # Analyse des fichiers avec barre de progression
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Analyse des fichiers...", total=len(files_found))
            
            for file_path in files_found:
                # Analyse du fichier
                analysis = self.mcp_simulator.analyze_file(file_path)
                self.session.files_analyzed.append(analysis)
                
                # Mise à jour des statistiques
                if analysis.warning_level in ['warning', 'critical']:
                    self.session.sensitive_files += 1
                
                progress.update(task, advance=1, description=f"Analyse: {analysis.file_name}")
        
        self.session.total_files = len(files_found)
        console.print("✅ Analyse terminée", style="green")
    
    def show_analysis_results(self):
        """Affiche les résultats d'analyse"""
        
        if not self.session.files_analyzed:
            console.print("❌ Aucune analyse disponible", style="red")
            return
        
        console.print("\n📊 Résultats d'Analyse", style="bold cyan")
        
        # Statistiques générales
        stats_table = Table(title="📈 Statistiques Générales")
        stats_table.add_column("Métrique", style="cyan")
        stats_table.add_column("Valeur", style="white")
        
        # Calcul des statistiques
        file_types = {}
        agents_used = {}
        warning_levels = {'safe': 0, 'warning': 0, 'critical': 0}
        
        for analysis in self.session.files_analyzed:
            file_types[analysis.file_type] = file_types.get(analysis.file_type, 0) + 1
            agents_used[analysis.agent_used] = agents_used.get(analysis.agent_used, 0) + 1
            warning_levels[analysis.warning_level] += 1
        
        stats_table.add_row("Total des fichiers", str(self.session.total_files))
        stats_table.add_row("Fichiers analysés", str(len(self.session.files_analyzed)))
        stats_table.add_row("Fichiers sensibles", str(self.session.sensitive_files))
        stats_table.add_row("Fichiers sûrs", str(warning_levels['safe']))
        stats_table.add_row("Avertissements", str(warning_levels['warning']))
        stats_table.add_row("Critiques", str(warning_levels['critical']))
        
        console.print(stats_table)
        
        # Répartition par type
        if file_types:
            console.print("\n📋 Répartition par type:")
            for file_type, count in file_types.items():
                console.print(f"  {file_type}: {count} fichiers")
        
        # Répartition par agent
        if agents_used:
            console.print("\n🤖 Répartition par agent:")
            for agent, count in agents_used.items():
                console.print(f"  Agent {agent}: {count} fichiers")
        
        # Fichiers sensibles détaillés
        sensitive_files = [f for f in self.session.files_analyzed if f.warning_level != 'safe']
        if sensitive_files:
            console.print("\n⚠️ Fichiers sensibles détectés:", style="bold yellow")
            
            sensitive_table = Table()
            sensitive_table.add_column("Fichier", style="cyan")
            sensitive_table.add_column("Type", style="white")
            sensitive_table.add_column("Niveau", style="yellow")
            sensitive_table.add_column("PII Détectées", style="red")
            
            for analysis in sensitive_files:
                level_style = "yellow" if analysis.warning_level == 'warning' else "red"
                pii_text = ", ".join(analysis.pii_detected) if analysis.pii_detected else "N/A"
                
                sensitive_table.add_row(
                    analysis.file_name,
                    analysis.file_type,
                    analysis.warning_level,
                    pii_text
                )
            
            console.print(sensitive_table)
    
    def show_detailed_file_analysis(self):
        """Affiche l'analyse détaillée d'un fichier"""
        
        if not self.session.files_analyzed:
            console.print("❌ Aucune analyse disponible", style="red")
            return
        
        console.print("\n🔍 Analyse Détaillée", style="bold cyan")
        
        # Liste des fichiers
        for i, analysis in enumerate(self.session.files_analyzed, 1):
            status = "⚠️" if analysis.warning_level != 'safe' else "✅"
            console.print(f"{i}. {status} {analysis.file_name} ({analysis.file_type})")
        
        try:
            choice = int(Prompt.ask("Sélectionnez un fichier", choices=[str(i) for i in range(1, len(self.session.files_analyzed) + 1)]))
            analysis = self.session.files_analyzed[choice - 1]
            
            # Affichage détaillé
            details = f"""
Fichier: {analysis.file_name}
Chemin: {analysis.file_path}
Type: {analysis.file_type}
MIME Type: {analysis.mime_type}
Taille: {analysis.size} octets
Hash MD5: {analysis.hash_md5}
Agent utilisé: {analysis.agent_used}
Niveau de warning: {analysis.warning_level}
Confiance: {analysis.confidence:.2%}
Temps de traitement: {analysis.processing_time:.2f}s

Résumé: {analysis.summary}

PII détectées: {', '.join(analysis.pii_detected) if analysis.pii_detected else 'Aucune'}

Métadonnées:
{json.dumps(analysis.metadata, indent=2)}
            """
            
            console.print(Panel(details.strip(), title=f"Analyse de {analysis.file_name}", style="blue"))
            
        except (ValueError, IndexError):
            console.print("❌ Sélection invalide", style="red")
    
    def security_actions(self):
        """Actions de sécurité"""
        
        console.print("\n🔐 Actions de Sécurité", style="bold red")
        
        if not self.authenticated:
            console.print("❌ Authentification requise", style="red")
            return
        
        # Options de sécurité
        actions = [
            "Chiffrer les fichiers sensibles",
            "Déplacer vers le vault sécurisé",
            "Générer un rapport de sécurité",
            "Purger les fichiers critiques",
            "Créer une sauvegarde sécurisée"
        ]
        
        console.print("Actions disponibles :")
        for i, action in enumerate(actions, 1):
            console.print(f"{i}. {action}")
        
        choice = Prompt.ask("Sélectionnez une action", choices=[str(i) for i in range(1, len(actions) + 1)])
        
        action_chosen = actions[int(choice) - 1]
        
        # Simulation de l'action
        with console.status(f"[spinner] Exécution: {action_chosen}..."):
            time.sleep(2)  # Simulation
        
        # Enregistrement de l'action
        security_action = {
            'action': action_chosen,
            'timestamp': datetime.now().isoformat(),
            'user': self.session.user_id,
            'files_affected': len([f for f in self.session.files_analyzed if f.warning_level != 'safe'])
        }
        
        self.session.security_actions.append(security_action)
        console.print(f"✅ Action exécutée: {action_chosen}", style="green")
    
    def generate_report(self):
        """Génère un rapport complet"""
        
        console.print("\n📋 Génération du Rapport", style="bold cyan")
        
        # Données du rapport
        report_data = {
            'session_info': asdict(self.session),
            'analysis_summary': {
                'total_files': self.session.total_files,
                'files_analyzed': len(self.session.files_analyzed),
                'sensitive_files': self.session.sensitive_files,
                'safe_files': len([f for f in self.session.files_analyzed if f.warning_level == 'safe'])
            },
            'security_summary': {
                'actions_performed': len(self.session.security_actions),
                'vault_status': self.session.vault_status,
                'authentication_status': self.authenticated
            },
            'detailed_analysis': [asdict(analysis) for analysis in self.session.files_analyzed]
        }
        
        # Sauvegarde du rapport
        report_filename = f"rapport_mcp_{self.session.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            console.print(f"✅ Rapport sauvegardé: {report_filename}", style="green")
            
            # Affichage du résumé
            console.print("\n📊 Résumé du Rapport:", style="bold")
            console.print(f"  Session: {self.session.session_id}")
            console.print(f"  Fichiers analysés: {len(self.session.files_analyzed)}")
            console.print(f"  Fichiers sensibles: {self.session.sensitive_files}")
            console.print(f"  Actions de sécurité: {len(self.session.security_actions)}")
            
        except Exception as e:
            console.print(f"❌ Erreur lors de la sauvegarde: {e}", style="red")
    
    def main_menu(self):
        """Menu principal"""
        
        while True:
            self.show_header()
            
            menu_options = [
                "🔍 Scanner et analyser un répertoire",
                "📊 Afficher les résultats d'analyse",
                "🔍 Analyse détaillée d'un fichier",
                "🔐 Actions de sécurité",
                "🤖 Statut des agents MCP",
                "📋 Générer un rapport",
                "🔑 Changer d'utilisateur",
                "❌ Quitter"
            ]
            
            console.print("\n🎯 Menu Principal", style="bold cyan")
            for i, option in enumerate(menu_options, 1):
                console.print(f"{i}. {option}")
            
            choice = Prompt.ask("Votre choix", choices=[str(i) for i in range(1, len(menu_options) + 1)])
            
            if choice == "1":
                if self.select_directory():
                    self.scan_and_analyze()
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choice == "2":
                self.show_analysis_results()
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choice == "3":
                self.show_detailed_file_analysis()
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choice == "4":
                self.security_actions()
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choice == "5":
                self.show_agent_status()
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choice == "6":
                self.generate_report()
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choice == "7":
                self.authenticated = False
                if not self.authenticate_user():
                    continue
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choice == "8":
                console.print("\n👋 Au revoir!", style="bold green")
                break
    
    def run(self):
        """Lance l'interface interactive"""
        
        try:
            console.print("🚀 Démarrage de l'interface interactive MCP", style="bold green")
            
            # Authentification
            if not self.authenticate_user():
                return
            
            # Menu principal
            self.main_menu()
            
        except KeyboardInterrupt:
            console.print("\n\n👋 Arrêt du programme", style="bold yellow")
        except Exception as e:
            error_console.print(f"❌ Erreur fatale: {e}")
            logger.error(f"Erreur fatale: {e}")

# ──────────────────────────────────────────────────────────────────────────
# Point d'entrée principal
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        # Création du répertoire de logs
        Path("logs").mkdir(exist_ok=True)
        
        # Lancement de l'interface
        demo = InteractiveDemo()
        demo.run()
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)
