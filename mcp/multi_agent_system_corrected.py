#!/usr/bin/env python3
"""
Système Multi-Agents Corrigé - Détection complète de tous les fichiers
======================================================================

Système qui détecte et traite TOUS les types de fichiers :
- Texte : .txt, .pdf, .md, .json, .csv, .xml, .html, .log, .py, .js, .css, .docx, .rtf
- Images : .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp, .svg, .ico
- Audio : .mp3, .wav, .m4a, .ogg, .flac, .aac, .mp4, .avi, .mov, .mkv
- Documents : .pdf, .doc, .docx, .ppt, .pptx, .xls, .xlsx
- Archives : .zip, .rar, .7z, .tar, .gz
- Autres : détection automatique par mime-type

Utilise l'orchestrateur MCP pour distribuer le travail aux agents spécialisés.
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import mimetypes
import hashlib
import uuid

# Import conditionnel de python-magic
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/multi_agent_system.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────
# Modèles de données
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class FileInfo:
    """Information complète sur un fichier"""
    file_path: str
    file_name: str
    file_type: str  # 'text', 'image', 'audio', 'document', 'archive', 'other'
    mime_type: str
    size: int
    extension: str
    hash_md5: str
    agent_type: str  # quel agent doit traiter ce fichier
    priority: int = 1

@dataclass
class ProcessingResult:
    """Résultat de traitement d'un fichier"""
    file_path: str
    file_name: str
    summary: str
    warning: bool
    agent_type: str
    processing_time: float
    file_type: str
    mime_type: str
    size: int
    hash_md5: str
    pii_detected: List[str] = None
    metadata: Dict[str, Any] = None

# ──────────────────────────────────────────────────────────────────────────
# Détecteur de fichiers universel
# ──────────────────────────────────────────────────────────────────────────

class UniversalFileDetector:
    """Détecteur universel de fichiers - Supporte TOUS les types"""
    
    def __init__(self):
        # Extensions supportées (liste complète)
        self.supported_extensions = {
            # Fichiers texte → Agent NLP
            'text': [
                '.txt', '.md', '.log', '.cfg', '.conf', '.ini', '.yml', '.yaml',
                '.json', '.xml', '.csv', '.tsv', '.sql', '.py', '.js', '.html',
                '.css', '.php', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.kt',
                '.swift', '.sh', '.bat', '.ps1', '.vbs', '.r', '.m', '.scala'
            ],
            # Fichiers image → Agent Vision
            'image': [
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
                '.svg', '.ico', '.pcx', '.tga', '.psd', '.raw', '.cr2', '.nef',
                '.orf', '.arw', '.dng', '.heic', '.heif', '.avif'
            ],
            # Fichiers audio/vidéo → Agent Audio
            'audio': [
                '.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma', '.opus',
                '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v',
                '.3gp', '.ogv', '.ts', '.mts', '.vob', '.asf', '.rm', '.rmvb'
            ],
            # Documents → Agent NLP (traitement spécialisé)
            'document': [
                '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
                '.odt', '.ods', '.odp', '.rtf', '.pages', '.numbers', '.key',
                '.epub', '.mobi', '.azw', '.azw3', '.fb2', '.lit'
            ],
            # Archives → Agent NLP (liste du contenu)
            'archive': [
                '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lzma',
                '.cab', '.iso', '.dmg', '.pkg', '.deb', '.rpm', '.msi', '.exe'
            ]
        }
        
        # Agents responsables de chaque type
        self.type_to_agent = {
            'text': 'nlp',
            'image': 'vision',
            'audio': 'audio',
            'document': 'nlp',  # NLP peut traiter les documents
            'archive': 'nlp',   # NLP peut lister le contenu
            'other': 'nlp'      # NLP par défaut
        }
        
        # Initialisation de python-magic pour détection mime-type
        if MAGIC_AVAILABLE:
            try:
                self.magic_mime = magic.Magic(mime=True)
                self.magic_available = True
                logger.info("✅ python-magic disponible pour détection mime-type")
            except Exception as e:
                self.magic_available = False
                logger.warning(f"⚠️ python-magic erreur: {e}")
        else:
            self.magic_available = False
            logger.warning("⚠️ python-magic non disponible, utilisation de mimetypes")
    
    def get_file_hash(self, file_path: str) -> str:
        """Calcule le hash MD5 d'un fichier"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Erreur calcul hash pour {file_path}: {e}")
            return "unknown"
    
    def detect_mime_type(self, file_path: str) -> str:
        """Détecte le type MIME d'un fichier"""
        try:
            if self.magic_available:
                return self.magic_mime.from_file(file_path)
            else:
                mime_type, _ = mimetypes.guess_type(file_path)
                return mime_type or "application/octet-stream"
        except Exception as e:
            logger.error(f"Erreur détection mime-type pour {file_path}: {e}")
            return "application/octet-stream"
    
    def classify_file(self, file_path: str) -> Optional[FileInfo]:
        """
        Classifie un fichier et détermine l'agent approprié
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            FileInfo si le fichier peut être traité, None sinon
        """
        try:
            path_obj = Path(file_path)
            
            if not path_obj.exists() or not path_obj.is_file():
                return None
            
            # Informations de base
            file_name = path_obj.name
            extension = path_obj.suffix.lower()
            file_size = path_obj.stat().st_size
            
            # Détection du type de fichier
            file_type = 'other'  # par défaut
            for category, extensions in self.supported_extensions.items():
                if extension in extensions:
                    file_type = category
                    break
            
            # Si extension inconnue, essayer de détecter par mime-type
            if file_type == 'other':
                mime_type = self.detect_mime_type(file_path)
                if mime_type.startswith('text/'):
                    file_type = 'text'
                elif mime_type.startswith('image/'):
                    file_type = 'image'
                elif mime_type.startswith('audio/') or mime_type.startswith('video/'):
                    file_type = 'audio'
                elif mime_type in ['application/pdf', 'application/msword']:
                    file_type = 'document'
                elif mime_type.startswith('application/zip') or 'archive' in mime_type:
                    file_type = 'archive'
            else:
                mime_type = self.detect_mime_type(file_path)
            
            # Déterminer l'agent responsable
            agent_type = self.type_to_agent.get(file_type, 'nlp')
            
            # Calcul du hash
            file_hash = self.get_file_hash(file_path)
            
            # Priorité (fichiers sensibles en premier)
            priority = 1
            if any(keyword in file_name.lower() for keyword in ['sensible', 'secret', 'confidentiel', 'prive']):
                priority = 3
            elif file_type in ['document', 'text']:
                priority = 2
            
            return FileInfo(
                file_path=file_path,
                file_name=file_name,
                file_type=file_type,
                mime_type=mime_type,
                size=file_size,
                extension=extension,
                hash_md5=file_hash,
                agent_type=agent_type,
                priority=priority
            )
            
        except Exception as e:
            logger.error(f"Erreur classification fichier {file_path}: {e}")
            return None

# ──────────────────────────────────────────────────────────────────────────
# Scanner de répertoires
# ──────────────────────────────────────────────────────────────────────────

class DirectoryScanner:
    """Scanner de répertoires - Trouve TOUS les fichiers"""
    
    def __init__(self):
        self.detector = UniversalFileDetector()
        self.excluded_dirs = {'.git', '__pycache__', '.vscode', 'node_modules', '.DS_Store'}
        self.excluded_files = {'.gitignore', '.env', 'Thumbs.db', '.DS_Store'}
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[FileInfo]:
        """
        Scanne un répertoire et retourne tous les fichiers détectés
        
        Args:
            directory: Répertoire à scanner
            recursive: Scanner récursivement les sous-répertoires
            
        Returns:
            Liste des fichiers détectés avec leurs informations
        """
        files_found = []
        directory_path = Path(directory)
        
        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"❌ Répertoire inexistant: {directory}")
            return files_found
        
        logger.info(f"🔍 Scan du répertoire: {directory}")
        
        try:
            # Fonction de scan récursif
            def scan_recursive(path: Path):
                try:
                    for item in path.iterdir():
                        # Ignorer les répertoires exclus
                        if item.is_dir() and item.name in self.excluded_dirs:
                            continue
                        
                        # Ignorer les fichiers exclus
                        if item.is_file() and item.name in self.excluded_files:
                            continue
                        
                        if item.is_file():
                            # Traiter le fichier
                            file_info = self.detector.classify_file(str(item))
                            if file_info:
                                files_found.append(file_info)
                                logger.debug(f"✅ Fichier détecté: {item.name} -> {file_info.file_type} -> {file_info.agent_type}")
                        
                        elif item.is_dir() and recursive:
                            # Scanner récursivement
                            scan_recursive(item)
                            
                except PermissionError as e:
                    logger.warning(f"⚠️ Accès refusé: {path}")
                except Exception as e:
                    logger.error(f"❌ Erreur scan {path}: {e}")
            
            # Lancer le scan
            scan_recursive(directory_path)
            
            # Trier par priorité (fichiers sensibles en premier)
            files_found.sort(key=lambda f: (-f.priority, f.file_name))
            
            logger.info(f"🎯 Scan terminé: {len(files_found)} fichiers détectés")
            
            # Statistiques par type
            stats = {}
            for file_info in files_found:
                stats[file_info.file_type] = stats.get(file_info.file_type, 0) + 1
            
            logger.info(f"📊 Répartition par type: {stats}")
            
            return files_found
            
        except Exception as e:
            logger.error(f"❌ Erreur générale lors du scan: {e}")
            return files_found

# ──────────────────────────────────────────────────────────────────────────
# Simulateur d'agents (pour tests)
# ──────────────────────────────────────────────────────────────────────────

class MockAgentSystem:
    """Système d'agents simulé pour les tests"""
    
    def __init__(self):
        self.processing_time = {
            'nlp': 0.5,     # Agent NLP rapide
            'vision': 1.0,  # Agent Vision plus lent
            'audio': 2.0    # Agent Audio le plus lent
        }
        
        # Patterns PII pour simulation
        self.pii_patterns = {
            'EMAIL': r'[\w\.-]+@[\w\.-]+\.\w+',
            'PHONE': r'[\d\s\-\+]{10,}',
            'CARD': r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
            'IBAN': r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}[A-Z0-9]{1,16}\b'
        }
    
    def simulate_agent_processing(self, file_info: FileInfo) -> ProcessingResult:
        """Simule le traitement d'un fichier par un agent"""
        
        start_time = time.time()
        
        # Simulation du temps de traitement
        processing_time = self.processing_time.get(file_info.agent_type, 0.5)
        time.sleep(processing_time * 0.1)  # Réduit pour les tests
        
        # Génération d'un résumé basique
        summary = f"Fichier {file_info.file_type} analysé: {file_info.file_name}"
        
        # Détection PII simulée (basée sur le nom de fichier)
        warning = False
        pii_detected = []
        
        if any(keyword in file_info.file_name.lower() for keyword in 
               ['sensible', 'secret', 'confidentiel', 'prive', 'carte', 'iban', 'passeport']):
            warning = True
            pii_detected = ['SENSITIVE_CONTENT']
        
        # Métadonnées additionnelles
        metadata = {
            'agent_version': '1.0.0',
            'processing_method': f'{file_info.agent_type}_mock',
            'confidence': 0.85,
            'file_hash': file_info.hash_md5
        }
        
        end_time = time.time()
        
        return ProcessingResult(
            file_path=file_info.file_path,
            file_name=file_info.file_name,
            summary=summary,
            warning=warning,
            agent_type=file_info.agent_type,
            processing_time=end_time - start_time,
            file_type=file_info.file_type,
            mime_type=file_info.mime_type,
            size=file_info.size,
            hash_md5=file_info.hash_md5,
            pii_detected=pii_detected,
            metadata=metadata
        )

# ──────────────────────────────────────────────────────────────────────────
# Système principal
# ──────────────────────────────────────────────────────────────────────────

class MultiAgentSystem:
    """Système Multi-Agents Complet"""
    
    def __init__(self):
        self.scanner = DirectoryScanner()
        self.agent_system = MockAgentSystem()
        self.session_id = str(uuid.uuid4())[:8]
        self.results = []
    
    def process_directory(self, directory: str) -> Dict[str, Any]:
        """
        Traite un répertoire complet avec tous les agents
        
        Args:
            directory: Répertoire à traiter
            
        Returns:
            Rapport complet du traitement
        """
        start_time = time.time()
        
        logger.info(f"🚀 Début traitement répertoire: {directory}")
        
        # 1. Scanner le répertoire
        files_found = self.scanner.scan_directory(directory)
        
        if not files_found:
            logger.warning("❌ Aucun fichier détecté")
            return {
                'session_id': self.session_id,
                'directory': directory,
                'total_files': 0,
                'results': [],
                'error': 'Aucun fichier détecté'
            }
        
        # 2. Traiter chaque fichier
        results = []
        for file_info in files_found:
            logger.info(f"🔄 Traitement: {file_info.file_name} -> Agent {file_info.agent_type}")
            
            try:
                result = self.agent_system.simulate_agent_processing(file_info)
                results.append(result)
                
                # Affichage du résultat
                status = "⚠️ SENSIBLE" if result.warning else "✅ SAFE"
                logger.info(f"   {status} - {result.summary}")
                
            except Exception as e:
                logger.error(f"❌ Erreur traitement {file_info.file_name}: {e}")
        
        end_time = time.time()
        
        # 3. Génération du rapport
        files_by_type = {}
        files_by_agent = {}
        files_with_warnings = []
        
        for result in results:
            # Statistiques par type
            files_by_type[result.file_type] = files_by_type.get(result.file_type, 0) + 1
            files_by_agent[result.agent_type] = files_by_agent.get(result.agent_type, 0) + 1
            
            # Fichiers avec warnings
            if result.warning:
                files_with_warnings.append(result.file_name)
        
        report = {
            'session_id': self.session_id,
            'directory': directory,
            'start_time': datetime.fromtimestamp(start_time).isoformat(),
            'end_time': datetime.fromtimestamp(end_time).isoformat(),
            'total_processing_time': end_time - start_time,
            'total_files': len(files_found),
            'files_processed': len(results),
            'files_by_type': files_by_type,
            'files_by_agent': files_by_agent,
            'files_with_warnings': len(files_with_warnings),
            'warning_files': files_with_warnings,
            'results': results
        }
        
        logger.info(f"✅ Traitement terminé: {len(results)} fichiers traités en {end_time - start_time:.2f}s")
        
        return report

# ──────────────────────────────────────────────────────────────────────────
# Interface interactive
# ──────────────────────────────────────────────────────────────────────────

def interactive_demo():
    """Démonstration interactive du système"""
    
    print("=" * 80)
    print("🎯 SYSTÈME MULTI-AGENTS CORRIGÉ - DÉTECTION COMPLÈTE")
    print("=" * 80)
    print()
    
    # Initialisation du système
    system = MultiAgentSystem()
    
    while True:
        print("\n📁 Répertoires disponibles:")
        print("1. test_files (répertoire de test)")
        print("2. Spécifier un répertoire personnalisé")
        print("3. Quitter")
        
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == "1":
            directory = "test_files"
        elif choice == "2":
            directory = input("Chemin du répertoire: ").strip()
        elif choice == "3":
            print("👋 Au revoir!")
            break
        else:
            print("❌ Choix invalide")
            continue
        
        # Traitement du répertoire
        print(f"\n🔍 Traitement du répertoire: {directory}")
        print("-" * 60)
        
        try:
            report = system.process_directory(directory)
            
            # Affichage du rapport
            print(f"\n📊 RAPPORT DE TRAITEMENT")
            print(f"Session: {report['session_id']}")
            print(f"Répertoire: {report['directory']}")
            print(f"Fichiers détectés: {report['total_files']}")
            print(f"Fichiers traités: {report['files_processed']}")
            print(f"Temps total: {report['total_processing_time']:.2f}s")
            print(f"Fichiers avec warnings: {report['files_with_warnings']}")
            
            print(f"\n📈 Répartition par type:")
            for file_type, count in report['files_by_type'].items():
                print(f"  {file_type}: {count} fichiers")
            
            print(f"\n🤖 Répartition par agent:")
            for agent_type, count in report['files_by_agent'].items():
                print(f"  Agent {agent_type}: {count} fichiers")
            
            if report['warning_files']:
                print(f"\n⚠️ Fichiers sensibles détectés:")
                for filename in report['warning_files']:
                    print(f"  - {filename}")
            
            print(f"\n📋 Détails des fichiers:")
            for result in report['results']:
                status = "⚠️ SENSIBLE" if result.warning else "✅ SAFE"
                print(f"  {status} [{result.file_type}] {result.file_name} - Agent {result.agent_type}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        input("\nAppuyez sur Entrée pour continuer...")

# ──────────────────────────────────────────────────────────────────────────
# Point d'entrée principal
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        interactive_demo()
    except KeyboardInterrupt:
        print("\n👋 Arrêt du programme")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        print(f"❌ Erreur fatale: {e}")
