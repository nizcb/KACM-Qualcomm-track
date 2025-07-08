#!/usr/bin/env python3
"""
Interface Interactive Complète - Système MCP Multi-Agents
=========================================================

Interface terminal interactive complète pour démonstrer le système MCP multi-agents :

🔐 AUTHENTIFICATION
- Système d'authentification sécurisé
- Gestion des utilisateurs avec différents niveaux d'accès

🎯 FONCTIONNALITÉS PRINCIPALES
- Scan et analyse de répertoires complets
- Détection automatique de tous types de fichiers
- Traitement par agents spécialisés (NLP, Vision, Audio)
- Détection PII et classification sécurisée
- Gestion du vault sécurisé
- Rapports détaillés avec statistiques

🤖 AGENTS INTÉGRÉS
- Agent NLP : Texte, documents, JSON, CSV
- Agent Vision : Images, photos, documents scannés
- Agent Audio : Sons, musique, enregistrements
- Agent Security : Chiffrement, vault, authentification
- Agent Orchestrator : Coordination et workflow

🎨 INTERFACE AVANCÉE
- Menus interactifs avec Rich
- Barres de progression
- Tableaux de données
- Alertes et notifications colorées
- Navigation intuitive

Identifiants de démonstration :
- Utilisateur : admin
- Mot de passe : demo123
"""

import os
import sys
import time
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import getpass

# Rich pour l'interface avancée
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.columns import Columns

# Imports du système multi-agents
from multi_agent_system_corrected import (
    MultiAgentSystem, 
    DirectoryScanner, 
    UniversalFileDetector,
    ProcessingResult
)

# Configuration globale
console = Console()

# Base de données des utilisateurs (pour la démo)
USERS_DB = {
    "admin": {
        "password": "demo123",
        "role": "administrator",
        "access_level": "full",
        "name": "Administrateur Système"
    },
    "user": {
        "password": "user123", 
        "role": "user",
        "access_level": "limited",
        "name": "Utilisateur Standard"
    },
    "demo": {
        "password": "demo",
        "role": "guest",
        "access_level": "readonly",
        "name": "Invité Démonstration"
    }
}

# ──────────────────────────────────────────────────────────────────────────
# Système d'authentification
# ──────────────────────────────────────────────────────────────────────────

class AuthSystem:
    """Système d'authentification sécurisé"""
    
    def __init__(self):
        self.current_user = None
        self.session_start = None
        self.max_attempts = 3
        self.lockout_time = 300  # 5 minutes
        self.failed_attempts = {}
    
    def hash_password(self, password: str) -> str:
        """Hash simple pour la démo"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authentification utilisateur"""
        if username in USERS_DB:
            stored_pass = USERS_DB[username]["password"]
            if password == stored_pass:  # Comparaison directe pour la démo
                self.current_user = {
                    "username": username,
                    "role": USERS_DB[username]["role"],
                    "access_level": USERS_DB[username]["access_level"],
                    "name": USERS_DB[username]["name"]
                }
                self.session_start = datetime.now()
                return True
        return False
    
    def login_screen(self) -> bool:
        """Écran de connexion interactif"""
        console.clear()
        
        # Bannière d'accueil
        welcome_panel = Panel(
            Text("🔐 SYSTÈME MCP MULTI-AGENTS", style="bold blue", justify="center") +
            Text("\n\nInterface Interactive Complète", style="italic", justify="center") +
            Text("\n\nVeuillez vous authentifier pour accéder au système", justify="center"),
            title="🏢 Authentification Requise",
            border_style="blue"
        )
        console.print(welcome_panel)
        console.print()
        
        # Affichage des comptes disponibles
        accounts_table = Table(title="📋 Comptes Disponibles (Démonstration)")
        accounts_table.add_column("Utilisateur", style="cyan")
        accounts_table.add_column("Mot de passe", style="yellow")
        accounts_table.add_column("Rôle", style="green")
        accounts_table.add_column("Accès", style="magenta")
        
        for username, info in USERS_DB.items():
            accounts_table.add_row(
                username,
                info["password"],
                info["role"],
                info["access_level"]
            )
        
        console.print(accounts_table)
        console.print()
        
        # Processus de connexion
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            try:
                username = Prompt.ask("👤 Nom d'utilisateur", default="admin")
                password = getpass.getpass("🔑 Mot de passe: ")
                
                if self.authenticate(username, password):
                    console.print(f"✅ Connexion réussie! Bienvenue {self.current_user['name']}", style="green")
                    time.sleep(2)
                    return True
                else:
                    attempts += 1
                    remaining = max_attempts - attempts
                    if remaining > 0:
                        console.print(f"❌ Identifiants incorrects. {remaining} tentatives restantes", style="red")
                    else:
                        console.print("🔒 Trop de tentatives échouées. Accès bloqué.", style="red")
                        
            except KeyboardInterrupt:
                console.print("\n👋 Connexion annulée")
                return False
        
        return False
    
    def get_user_info(self) -> Dict[str, Any]:
        """Retourne les informations de l'utilisateur connecté"""
        return self.current_user or {}
    
    def has_permission(self, action: str) -> bool:
        """Vérification des permissions"""
        if not self.current_user:
            return False
        
        access_level = self.current_user.get("access_level", "none")
        
        if access_level == "full":
            return True
        elif access_level == "limited":
            return action in ["scan", "analyze", "view_reports"]
        elif access_level == "readonly":
            return action in ["view_reports"]
        
        return False

# ──────────────────────────────────────────────────────────────────────────
# Interface principale
# ──────────────────────────────────────────────────────────────────────────

class InteractiveInterface:
    """Interface interactive complète"""
    
    def __init__(self):
        self.auth = AuthSystem()
        self.multi_agent_system = MultiAgentSystem()
        self.scanner = DirectoryScanner()
        self.session_reports = []
        self.current_directory = None
        self.vault_locked = True
        
    def show_banner(self):
        """Affiche la bannière principale"""
        console.clear()
        
        banner = Text("🎯 SYSTÈME MCP MULTI-AGENTS", style="bold blue")
        subtitle = Text("Interface Interactive Complète v2.0", style="italic")
        
        user_info = self.auth.get_user_info()
        user_text = Text(f"👤 Connecté: {user_info.get('name', 'Inconnu')} ({user_info.get('role', 'N/A')})", style="green")
        
        panel = Panel(
            Align.center(banner + Text("\n") + subtitle + Text("\n\n") + user_text),
            border_style="blue"
        )
        
        console.print(panel)
        console.print()
    
    def show_main_menu(self):
        """Affiche le menu principal"""
        self.show_banner()
        
        menu_options = [
            "📁 Scanner un répertoire",
            "🔍 Analyser des fichiers",
            "📊 Voir les rapports",
            "🔐 Gérer le vault sécurisé",
            "🤖 Status des agents",
            "⚙️ Configuration système",
            "📋 Historique des sessions",
            "🚪 Déconnexion"
        ]
        
        menu_table = Table(title="🎛️ Menu Principal")
        menu_table.add_column("N°", style="cyan", width=3)
        menu_table.add_column("Option", style="white")
        menu_table.add_column("Description", style="dim")
        
        descriptions = [
            "Scanner et détecter tous les fichiers d'un répertoire",
            "Analyser des fichiers avec les agents spécialisés",
            "Consulter les rapports d'analyse et statistiques",
            "Accéder aux fichiers sécurisés et sensibles",
            "Vérifier l'état et les performances des agents",
            "Modifier les paramètres du système",
            "Consulter l'historique des analyses",
            "Se déconnecter du système"
        ]
        
        for i, (option, desc) in enumerate(zip(menu_options, descriptions), 1):
            menu_table.add_row(str(i), option, desc)
        
        console.print(menu_table)
        console.print()
    
    def directory_scanner_interface(self):
        """Interface de scan de répertoires"""
        console.clear()
        
        panel = Panel(
            "📁 Scanner un répertoire\n\n" +
            "Cette fonction va scanner récursivement un répertoire et détecter tous les fichiers supportés.\n" +
            "Les fichiers seront classifiés automatiquement par type et assignés aux agents appropriés.",
            title="🔍 Scanner de Répertoires",
            border_style="green"
        )
        console.print(panel)
        console.print()
        
        # Suggestions de répertoires
        suggestions = [
            "mcp/test_files",
            "agents/vision/test_images", 
            ".",
            "Répertoire personnalisé"
        ]
        
        console.print("📋 Répertoires suggérés:")
        for i, suggestion in enumerate(suggestions, 1):
            console.print(f"  {i}. {suggestion}")
        console.print()
        
        choice = Prompt.ask("Choisir un répertoire", choices=["1", "2", "3", "4"], default="1")
        
        if choice == "1":
            directory = "mcp/test_files"
        elif choice == "2":
            directory = "agents/vision/test_images"
        elif choice == "3":
            directory = "."
        else:
            directory = Prompt.ask("Chemin du répertoire personnalisé")
        
        self.current_directory = directory
        
        # Scan avec barre de progression
        console.print(f"\n🔍 Scan du répertoire: {directory}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Scan en cours...", total=100)
            
            # Simulation du scan
            for i in range(100):
                time.sleep(0.02)
                progress.update(task, advance=1)
                
                if i == 25:
                    progress.update(task, description="Détection des fichiers...")
                elif i == 50:
                    progress.update(task, description="Classification par type...")
                elif i == 75:
                    progress.update(task, description="Assignation aux agents...")
        
        # Résultats du scan
        try:
            files_found = self.scanner.scan_directory(directory)
            
            if files_found:
                console.print(f"\n✅ Scan terminé: {len(files_found)} fichiers détectés")
                
                # Tableau des résultats
                results_table = Table(title="📊 Résultats du Scan")
                results_table.add_column("Fichier", style="cyan")
                results_table.add_column("Type", style="yellow")
                results_table.add_column("Taille", style="green")
                results_table.add_column("Agent", style="magenta")
                results_table.add_column("Priorité", style="red")
                
                for file_info in files_found[:10]:  # Limiter l'affichage
                    size_mb = file_info.size / (1024 * 1024)
                    size_str = f"{size_mb:.2f} MB" if size_mb > 1 else f"{file_info.size} B"
                    
                    priority_str = "🔴 Haute" if file_info.priority == 3 else "🟡 Normale" if file_info.priority == 2 else "🟢 Basse"
                    
                    results_table.add_row(
                        file_info.file_name,
                        file_info.file_type,
                        size_str,
                        file_info.agent_type,
                        priority_str
                    )
                
                console.print(results_table)
                
                # Statistiques
                stats = {}
                for file_info in files_found:
                    stats[file_info.file_type] = stats.get(file_info.file_type, 0) + 1
                
                console.print("\n📈 Statistiques par type:")
                for file_type, count in stats.items():
                    console.print(f"  {file_type}: {count} fichiers")
                
                # Proposition d'analyse
                if Confirm.ask("\n🤖 Lancer l'analyse avec les agents?"):
                    self.analyze_files_interface(files_found)
                
            else:
                console.print("❌ Aucun fichier détecté dans ce répertoire")
                
        except Exception as e:
            console.print(f"❌ Erreur lors du scan: {e}")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def analyze_files_interface(self, files_found=None):
        """Interface d'analyse des fichiers"""
        console.clear()
        
        panel = Panel(
            "🤖 Analyse des fichiers avec les agents spécialisés\n\n" +
            "Les agents vont analyser chaque fichier selon leur spécialité:\n" +
            "• Agent NLP: Détection PII, résumé de texte\n" +
            "• Agent Vision: OCR, détection d'objets sensibles\n" +
            "• Agent Audio: Transcription, analyse de contenu",
            title="🔬 Analyse Multi-Agents",
            border_style="blue"
        )
        console.print(panel)
        console.print()
        
        if not files_found:
            if not self.current_directory:
                console.print("❌ Aucun répertoire scanné. Veuillez d'abord scanner un répertoire.")
                input("Appuyez sur Entrée pour continuer...")
                return
            
            files_found = self.scanner.scan_directory(self.current_directory)
        
        if not files_found:
            console.print("❌ Aucun fichier à analyser")
            input("Appuyez sur Entrée pour continuer...")
            return
        
        console.print(f"📊 Analyse de {len(files_found)} fichiers...")
        
        # Analyse avec barre de progression
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Analyse en cours...", total=len(files_found))
            
            for i, file_info in enumerate(files_found):
                progress.update(task, description=f"Analyse: {file_info.file_name}")
                
                # Simulation de l'analyse
                result = self.multi_agent_system.agent_system.simulate_agent_processing(file_info)
                results.append(result)
                
                progress.update(task, advance=1)
                time.sleep(0.1)  # Simulation du temps de traitement
        
        # Affichage des résultats
        console.print("\n✅ Analyse terminée!")
        
        # Tableau des résultats
        results_table = Table(title="🎯 Résultats de l'Analyse")
        results_table.add_column("Fichier", style="cyan")
        results_table.add_column("Agent", style="blue")
        results_table.add_column("Status", style="yellow")
        results_table.add_column("Résumé", style="white")
        results_table.add_column("Temps", style="green")
        
        files_with_warnings = []
        
        for result in results:
            status = "⚠️ SENSIBLE" if result.warning else "✅ SÛRE"
            if result.warning:
                files_with_warnings.append(result.file_name)
            
            summary_short = result.summary[:50] + "..." if len(result.summary) > 50 else result.summary
            
            results_table.add_row(
                result.file_name,
                result.agent_type,
                status,
                summary_short,
                f"{result.processing_time:.2f}s"
            )
        
        console.print(results_table)
        
        # Alertes sécurisées
        if files_with_warnings:
            console.print("\n⚠️ ALERTES SÉCURISÉES:")
            for filename in files_with_warnings:
                console.print(f"  🔴 {filename} - Contenu sensible détecté")
        
        # Sauvegarde du rapport
        report = {
            "timestamp": datetime.now().isoformat(),
            "directory": self.current_directory,
            "files_analyzed": len(results),
            "files_with_warnings": len(files_with_warnings),
            "results": [vars(result) for result in results]
        }
        
        self.session_reports.append(report)
        
        console.print(f"\n📋 Rapport sauvegardé ({len(self.session_reports)} rapports au total)")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def show_reports_interface(self):
        """Interface d'affichage des rapports"""
        console.clear()
        
        panel = Panel(
            "📊 Rapports d'analyse et statistiques\n\n" +
            "Consultez les rapports détaillés des analyses précédentes,\n" +
            "les statistiques de sécurité et les tendances détectées.",
            title="📈 Centre de Rapports",
            border_style="yellow"
        )
        console.print(panel)
        console.print()
        
        if not self.session_reports:
            console.print("❌ Aucun rapport disponible. Effectuez d'abord une analyse.")
            input("Appuyez sur Entrée pour continuer...")
            return
        
        # Tableau des rapports
        reports_table = Table(title="📋 Rapports Disponibles")
        reports_table.add_column("N°", style="cyan")
        reports_table.add_column("Date/Heure", style="green")
        reports_table.add_column("Répertoire", style="yellow")
        reports_table.add_column("Fichiers", style="blue")
        reports_table.add_column("Alertes", style="red")
        
        for i, report in enumerate(self.session_reports, 1):
            timestamp = datetime.fromisoformat(report["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            reports_table.add_row(
                str(i),
                timestamp,
                report["directory"],
                str(report["files_analyzed"]),
                str(report["files_with_warnings"])
            )
        
        console.print(reports_table)
        
        # Sélection d'un rapport
        choice = Prompt.ask(f"\nChoisir un rapport à consulter (1-{len(self.session_reports)})", default="1")
        
        try:
            report_index = int(choice) - 1
            if 0 <= report_index < len(self.session_reports):
                selected_report = self.session_reports[report_index]
                
                # Affichage du rapport détaillé
                console.print(f"\n📄 Rapport détaillé - {selected_report['directory']}")
                
                # Statistiques générales
                stats_table = Table(title="📊 Statistiques Générales")
                stats_table.add_column("Métrique", style="cyan")
                stats_table.add_column("Valeur", style="yellow")
                
                stats_table.add_row("Fichiers analysés", str(selected_report["files_analyzed"]))
                stats_table.add_row("Fichiers avec alertes", str(selected_report["files_with_warnings"]))
                stats_table.add_row("Taux d'alertes", f"{(selected_report['files_with_warnings'] / selected_report['files_analyzed']) * 100:.1f}%")
                
                console.print(stats_table)
                
                # Détails par fichier
                if Confirm.ask("\nAfficher les détails par fichier?"):
                    details_table = Table(title="🔍 Détails par Fichier")
                    details_table.add_column("Fichier", style="cyan")
                    details_table.add_column("Status", style="yellow")
                    details_table.add_column("Agent", style="blue")
                    details_table.add_column("Résumé", style="white")
                    
                    for result in selected_report["results"]:
                        status = "⚠️ SENSIBLE" if result.get("warning", False) else "✅ SÛRE"
                        details_table.add_row(
                            result.get("file_name", "N/A"),
                            status,
                            result.get("agent_type", "N/A"),
                            result.get("summary", "N/A")[:60] + "..."
                        )
                    
                    console.print(details_table)
                
        except ValueError:
            console.print("❌ Numéro de rapport invalide")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def vault_management_interface(self):
        """Interface de gestion du vault sécurisé"""
        console.clear()
        
        panel = Panel(
            "🔐 Gestion du Vault Sécurisé\n\n" +
            "Le vault contient tous les fichiers sensibles détectés par les agents.\n" +
            "Accès restreint selon les permissions utilisateur.",
            title="🏦 Vault Sécurisé",
            border_style="red"
        )
        console.print(panel)
        console.print()
        
        # Vérification des permissions
        if not self.auth.has_permission("vault_access"):
            console.print("❌ Accès refusé. Permissions insuffisantes pour accéder au vault.")
            input("Appuyez sur Entrée pour continuer...")
            return
        
        # Status du vault
        vault_status = "🔒 Verrouillé" if self.vault_locked else "🔓 Déverrouillé"
        console.print(f"Status du vault: {vault_status}")
        
        if self.vault_locked:
            if Confirm.ask("Déverrouiller le vault?"):
                vault_password = getpass.getpass("Mot de passe du vault: ")
                if vault_password == "vault123":  # Mot de passe de démo
                    self.vault_locked = False
                    console.print("✅ Vault déverrouillé")
                else:
                    console.print("❌ Mot de passe incorrect")
                    input("Appuyez sur Entrée pour continuer...")
                    return
        
        # Simulation du contenu du vault
        vault_files = [
            {"name": "document_sensible.txt", "type": "text", "risk": "High", "pii": ["EMAIL", "PHONE"]},
            {"name": "Carte_bancaire_Visa.jpg", "type": "image", "risk": "Critical", "pii": ["CARD"]},
            {"name": "passeport_scan.pdf", "type": "document", "risk": "Critical", "pii": ["ID_DOCUMENT"]},
        ]
        
        vault_table = Table(title="🔒 Contenu du Vault")
        vault_table.add_column("Fichier", style="cyan")
        vault_table.add_column("Type", style="yellow")
        vault_table.add_column("Risque", style="red")
        vault_table.add_column("PII Détectées", style="magenta")
        
        for file_info in vault_files:
            risk_color = "red" if file_info["risk"] == "Critical" else "yellow"
            vault_table.add_row(
                file_info["name"],
                file_info["type"],
                Text(file_info["risk"], style=risk_color),
                ", ".join(file_info["pii"])
            )
        
        console.print(vault_table)
        
        # Options du vault
        console.print("\n🛠️ Options disponibles:")
        console.print("1. Exporter les fichiers (chiffrés)")
        console.print("2. Générer un rapport de sécurité")
        console.print("3. Configurer les alertes")
        console.print("4. Verrouiller le vault")
        
        choice = Prompt.ask("Choisir une option", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            console.print("📦 Export des fichiers chiffrés en cours...")
            time.sleep(2)
            console.print("✅ Export terminé: vault_export_encrypted.zip")
        elif choice == "2":
            console.print("📊 Génération du rapport de sécurité...")
            time.sleep(1)
            console.print("✅ Rapport généré: security_report.pdf")
        elif choice == "3":
            console.print("🔔 Configuration des alertes...")
            console.print("✅ Alertes configurées pour les nouveaux fichiers critiques")
        elif choice == "4":
            self.vault_locked = True
            console.print("🔒 Vault verrouillé")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def agents_status_interface(self):
        """Interface de status des agents"""
        console.clear()
        
        panel = Panel(
            "🤖 Status et Performance des Agents\n\n" +
            "Surveillez l'état, les performances et la santé de tous les agents du système.",
            title="📊 Centre de Contrôle des Agents",
            border_style="cyan"
        )
        console.print(panel)
        console.print()
        
        # Simulation du status des agents
        agents_data = [
            {"name": "Agent NLP", "status": "✅ Actif", "load": "75%", "processed": "1,234", "errors": "0"},
            {"name": "Agent Vision", "status": "✅ Actif", "load": "45%", "processed": "567", "errors": "2"},
            {"name": "Agent Audio", "status": "🟡 Ralenti", "load": "90%", "processed": "89", "errors": "1"},
            {"name": "Agent Security", "status": "✅ Actif", "load": "30%", "processed": "2,156", "errors": "0"},
            {"name": "Agent Orchestrator", "status": "✅ Actif", "load": "60%", "processed": "3,046", "errors": "0"},
        ]
        
        status_table = Table(title="🤖 Status des Agents")
        status_table.add_column("Agent", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Charge", style="yellow")
        status_table.add_column("Traités", style="blue")
        status_table.add_column("Erreurs", style="red")
        
        for agent in agents_data:
            status_table.add_row(
                agent["name"],
                agent["status"],
                agent["load"],
                agent["processed"],
                agent["errors"]
            )
        
        console.print(status_table)
        
        # Métriques de performance
        console.print("\n📈 Métriques de Performance:")
        
        metrics_table = Table()
        metrics_table.add_column("Métrique", style="cyan")
        metrics_table.add_column("Valeur", style="yellow")
        metrics_table.add_column("Tendance", style="green")
        
        metrics_table.add_row("Débit moyen", "156 fichiers/min", "📈 +12%")
        metrics_table.add_row("Temps de réponse", "0.8s", "📈 -5%")
        metrics_table.add_row("Précision PII", "98.7%", "📈 +2%")
        metrics_table.add_row("Utilisation CPU", "65%", "📉 -8%")
        metrics_table.add_row("Utilisation RAM", "4.2GB", "📈 +15%")
        
        console.print(metrics_table)
        
        # Actions disponibles
        console.print("\n🛠️ Actions disponibles:")
        console.print("1. Redémarrer un agent")
        console.print("2. Ajuster la charge")
        console.print("3. Voir les logs détaillés")
        console.print("4. Exporter les métriques")
        
        choice = Prompt.ask("Choisir une action", choices=["1", "2", "3", "4"], default="3")
        
        if choice == "1":
            agent_choice = Prompt.ask("Quel agent redémarrer?", choices=["nlp", "vision", "audio", "security", "orchestrator"])
            console.print(f"🔄 Redémarrage de l'Agent {agent_choice.upper()}...")
            time.sleep(2)
            console.print("✅ Agent redémarré avec succès")
        elif choice == "2":
            console.print("⚙️ Ajustement automatique de la charge...")
            time.sleep(1)
            console.print("✅ Charge optimisée")
        elif choice == "3":
            console.print("📋 Logs des dernières 24h:")
            logs = [
                "2025-01-08 10:30:15 - Agent NLP: Fichier traité avec succès",
                "2025-01-08 10:30:12 - Agent Vision: Détection PII dans image",
                "2025-01-08 10:30:08 - Agent Audio: Transcription terminée",
                "2025-01-08 10:30:05 - Agent Security: Fichier chiffré et stocké",
            ]
            for log in logs:
                console.print(f"  {log}")
        elif choice == "4":
            console.print("📊 Export des métriques...")
            time.sleep(1)
            console.print("✅ Métriques exportées: agents_metrics.json")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def run(self):
        """Boucle principale de l'interface"""
        
        # Écran de connexion
        if not self.auth.login_screen():
            return
        
        # Boucle principale
        while True:
            try:
                self.show_main_menu()
                
                choice = Prompt.ask("Choisir une option", choices=["1", "2", "3", "4", "5", "6", "7", "8"], default="1")
                
                if choice == "1":
                    self.directory_scanner_interface()
                elif choice == "2":
                    self.analyze_files_interface()
                elif choice == "3":
                    self.show_reports_interface()
                elif choice == "4":
                    self.vault_management_interface()
                elif choice == "5":
                    self.agents_status_interface()
                elif choice == "6":
                    console.print("⚙️ Configuration système - Fonctionnalité en développement")
                    input("Appuyez sur Entrée pour continuer...")
                elif choice == "7":
                    console.print("📋 Historique des sessions - Fonctionnalité en développement")
                    input("Appuyez sur Entrée pour continuer...")
                elif choice == "8":
                    console.print("👋 Déconnexion...")
                    time.sleep(1)
                    break
                
            except KeyboardInterrupt:
                console.print("\n👋 Arrêt du programme")
                break
            except Exception as e:
                console.print(f"❌ Erreur: {e}")
                input("Appuyez sur Entrée pour continuer...")

# ──────────────────────────────────────────────────────────────────────────
# Point d'entrée principal
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        interface = InteractiveInterface()
        interface.run()
    except KeyboardInterrupt:
        console.print("\n👋 Au revoir!")
    except Exception as e:
        console.print(f"❌ Erreur fatale: {e}")
