#!/usr/bin/env python3
"""
Interface Interactive MCP - Version Corrigée
============================================

Interface interactive simplifiée et corrigée pour tester le système MCP multi-agents.
Détecte TOUS les fichiers et les traite correctement.
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib
import mimetypes
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text

# Configuration Rich Console
console = Console()

@dataclass
class FileAnalysis:
    """Résultat d'analyse d'un fichier"""
    file_path: str
    file_name: str
    file_type: str
    size: int
    agent_used: str
    summary: str
    pii_detected: List[str]
    warning_level: str
    processing_time: float

class SimpleMCPDemo:
    """Démonstration MCP simplifiée et corrigée"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.files_analyzed = []
        
        # Types de fichiers supportés
        self.file_types = {
            '.txt': ('text', 'nlp'),
            '.md': ('text', 'nlp'),
            '.json': ('text', 'nlp'),
            '.csv': ('text', 'nlp'),
            '.pdf': ('document', 'nlp'),
            '.docx': ('document', 'nlp'),
            '.doc': ('document', 'nlp'),
            '.jpg': ('image', 'vision'),
            '.jpeg': ('image', 'vision'),
            '.png': ('image', 'vision'),
            '.gif': ('image', 'vision'),
            '.bmp': ('image', 'vision'),
            '.mp3': ('audio', 'audio'),
            '.wav': ('audio', 'audio'),
            '.m4a': ('audio', 'audio'),
            '.ogg': ('audio', 'audio')
        }
        
        # Mots-clés sensibles
        self.sensitive_keywords = [
            'sensible', 'secret', 'confidentiel', 'prive', 'carte', 'bancaire',
            'iban', 'passeport', 'cni', 'ordonnance', 'medical', 'paie',
            'bulletin', 'visa', 'mastercard', 'amex'
        ]
    
    def show_header(self):
        """Affiche l'en-tête"""
        console.clear()
        header = Text("🎯 SYSTÈME MCP MULTI-AGENTS - DÉMONSTRATION INTERACTIVE", style="bold blue")
        console.print(Panel(header, style="blue"))
        console.print(f"Session: {self.session_id}\n")
    
    def scan_directory(self, directory: str) -> List[str]:
        """Scanne un répertoire et retourne tous les fichiers"""
        files_found = []
        
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                console.print(f"❌ Répertoire inexistant: {directory}", style="red")
                return files_found
            
            console.print(f"🔍 Scan du répertoire: {directory}")
            
            # Scan récursif
            for item in dir_path.rglob('*'):
                if item.is_file():
                    extension = item.suffix.lower()
                    if extension in self.file_types:
                        files_found.append(str(item))
                        console.print(f"  ✅ Fichier détecté: {item.name} ({extension})")
            
            console.print(f"📊 Total: {len(files_found)} fichiers détectés\n")
            return files_found
            
        except Exception as e:
            console.print(f"❌ Erreur lors du scan: {e}", style="red")
            return files_found
    
    def analyze_file(self, file_path: str) -> FileAnalysis:
        """Analyse un fichier"""
        
        start_time = time.time()
        
        # Informations de base
        path_obj = Path(file_path)
        file_name = path_obj.name
        file_size = path_obj.stat().st_size if path_obj.exists() else 0
        extension = path_obj.suffix.lower()
        
        # Détermination du type et de l'agent
        if extension in self.file_types:
            file_type, agent_used = self.file_types[extension]
        else:
            file_type, agent_used = 'other', 'nlp'
        
        # Simulation du traitement
        processing_times = {'nlp': 0.3, 'vision': 0.8, 'audio': 1.5}
        time.sleep(processing_times.get(agent_used, 0.3) * 0.1)  # Simulation rapide
        
        # Détection PII basée sur le nom de fichier
        pii_detected = []
        warning_level = 'safe'
        
        file_name_lower = file_name.lower()
        for keyword in self.sensitive_keywords:
            if keyword in file_name_lower:
                pii_detected.append(keyword.upper())
                warning_level = 'critical'
        
        # Analyse du contenu pour les fichiers texte
        if file_type == 'text' and path_obj.exists():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()[:500]  # Lecture partielle
                    
                # Détection simple de patterns
                import re
                patterns = {
                    'EMAIL': r'[\w\.-]+@[\w\.-]+\.\w+',
                    'PHONE': r'[\d\s\-\+\(\)]{10,}',
                    'CARD': r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'
                }
                
                for pii_type, pattern in patterns.items():
                    if re.search(pattern, content):
                        pii_detected.append(pii_type)
                        warning_level = 'critical'
                        
            except Exception:
                pass
        
        # Génération du résumé
        summary = f"Fichier {file_type} analysé par l'agent {agent_used}"
        if pii_detected:
            summary += f" - PII détectées: {', '.join(pii_detected)}"
        
        end_time = time.time()
        
        return FileAnalysis(
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            size=file_size,
            agent_used=agent_used,
            summary=summary,
            pii_detected=pii_detected,
            warning_level=warning_level,
            processing_time=end_time - start_time
        )
    
    def process_directory(self, directory: str):
        """Traite un répertoire complet"""
        
        self.show_header()
        
        # 1. Scan du répertoire
        files_found = self.scan_directory(directory)
        
        if not files_found:
            console.print("❌ Aucun fichier supporté trouvé", style="red")
            return
        
        # 2. Analyse des fichiers
        console.print("🔄 Analyse des fichiers en cours...\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Analyse...", total=len(files_found))
            
            for file_path in files_found:
                analysis = self.analyze_file(file_path)
                self.files_analyzed.append(analysis)
                
                progress.update(task, advance=1, description=f"Analyse: {analysis.file_name}")
        
        # 3. Affichage des résultats
        self.show_results()
    
    def show_results(self):
        """Affiche les résultats"""
        
        console.print("\n📊 RÉSULTATS D'ANALYSE", style="bold cyan")
        
        # Statistiques
        total_files = len(self.files_analyzed)
        sensitive_files = len([f for f in self.files_analyzed if f.warning_level != 'safe'])
        safe_files = total_files - sensitive_files
        
        stats_table = Table(title="📈 Statistiques")
        stats_table.add_column("Métrique", style="cyan")
        stats_table.add_column("Valeur", style="white")
        
        stats_table.add_row("Total des fichiers", str(total_files))
        stats_table.add_row("Fichiers sensibles", str(sensitive_files))
        stats_table.add_row("Fichiers sûrs", str(safe_files))
        
        console.print(stats_table)
        
        # Répartition par type
        type_counts = {}
        agent_counts = {}
        
        for analysis in self.files_analyzed:
            type_counts[analysis.file_type] = type_counts.get(analysis.file_type, 0) + 1
            agent_counts[analysis.agent_used] = agent_counts.get(analysis.agent_used, 0) + 1
        
        console.print("\n📋 Répartition par type:")
        for file_type, count in type_counts.items():
            console.print(f"  {file_type}: {count} fichiers")
        
        console.print("\n🤖 Répartition par agent:")
        for agent, count in agent_counts.items():
            console.print(f"  Agent {agent}: {count} fichiers")
        
        # Fichiers détaillés
        console.print("\n📄 Détails des fichiers:")
        
        details_table = Table()
        details_table.add_column("Fichier", style="cyan")
        details_table.add_column("Type", style="white")
        details_table.add_column("Agent", style="yellow")
        details_table.add_column("Statut", style="green")
        details_table.add_column("PII", style="red")
        
        for analysis in self.files_analyzed:
            status = "⚠️ SENSIBLE" if analysis.warning_level != 'safe' else "✅ SAFE"
            pii_text = ", ".join(analysis.pii_detected) if analysis.pii_detected else "Aucune"
            
            details_table.add_row(
                analysis.file_name,
                analysis.file_type,
                analysis.agent_used,
                status,
                pii_text
            )
        
        console.print(details_table)
        
        # Fichiers sensibles
        sensitive_files = [f for f in self.files_analyzed if f.warning_level != 'safe']
        if sensitive_files:
            console.print("\n⚠️ FICHIERS SENSIBLES DÉTECTÉS:", style="bold red")
            for analysis in sensitive_files:
                console.print(f"  • {analysis.file_name} - {analysis.summary}")
    
    def save_report(self):
        """Sauvegarde le rapport"""
        
        report_data = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'total_files': len(self.files_analyzed),
            'sensitive_files': len([f for f in self.files_analyzed if f.warning_level != 'safe']),
            'analysis_results': [
                {
                    'file_name': a.file_name,
                    'file_type': a.file_type,
                    'agent_used': a.agent_used,
                    'warning_level': a.warning_level,
                    'pii_detected': a.pii_detected,
                    'summary': a.summary,
                    'processing_time': a.processing_time
                }
                for a in self.files_analyzed
            ]
        }
        
        report_file = f"rapport_mcp_{self.session_id}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            console.print(f"\n✅ Rapport sauvegardé: {report_file}", style="green")
            
        except Exception as e:
            console.print(f"❌ Erreur sauvegarde: {e}", style="red")
    
    def run(self):
        """Lance la démonstration"""
        
        try:
            self.show_header()
            
            console.print("🎯 DÉMONSTRATION SYSTÈME MCP MULTI-AGENTS", style="bold green")
            console.print("=" * 60)
            
            # Répertoires disponibles
            available_dirs = [
                "test_files",
                ".",
                "../agents/vision/test_images"
            ]
            
            console.print("\n📁 Répertoires disponibles:")
            for i, dir_path in enumerate(available_dirs, 1):
                exists = "✅" if Path(dir_path).exists() else "❌"
                console.print(f"{i}. {exists} {dir_path}")
            
            console.print(f"{len(available_dirs) + 1}. Spécifier un répertoire")
            
            choice = Prompt.ask("Sélectionnez un répertoire", choices=[str(i) for i in range(1, len(available_dirs) + 2)])
            
            if choice == str(len(available_dirs) + 1):
                directory = Prompt.ask("Chemin du répertoire")
            else:
                directory = available_dirs[int(choice) - 1]
            
            # Traitement du répertoire
            self.process_directory(directory)
            
            # Sauvegarde du rapport
            if Confirm.ask("\nSauvegarder le rapport?"):
                self.save_report()
            
            console.print("\n🎉 Démonstration terminée!", style="bold green")
            
        except KeyboardInterrupt:
            console.print("\n👋 Démonstration interrompue", style="yellow")
        except Exception as e:
            console.print(f"❌ Erreur: {e}", style="red")

if __name__ == "__main__":
    demo = SimpleMCPDemo()
    demo.run()
