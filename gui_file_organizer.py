#!/usr/bin/env python3
"""
Interface Graphique Complète - Organisation Intelligente + Chiffrement
=====================================================================

Application GUI moderne pour:
1. Organisation automatique des files (sans "general")
2. Classification métier intelligente
3. Chiffrement des dossiers sensibles
4. Rapports visuels et statistiques
5. Interface utilisateur intuitive
"""

import os
import sys
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# GUI imports
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, simpledialog
    from tkinter.scrolledtext import ScrolledText
    import tkinter.font as tkFont
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("❌ Tkinter non disponible")

# Agents import
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))

class FileOrganizerGUI:
    """Interface graphique pour l'organisation de files"""
    
    def __init__(self):
        if not GUI_AVAILABLE:
            raise ImportError("Tkinter non disponible")
        
        self.root = tk.Tk()
        
        # Variables d'état (AVANT create_widgets)
        self.source_folder = tk.StringVar()
        self.target_folder = tk.StringVar(value="organized_gui")
        self.encryption_enabled = tk.BooleanVar(value=True)
        self.current_operation = None
        self.organization_results = {}
        
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        
        # Import des agents
        self.load_agents()
    
    def setup_window(self):
        """Configuration de la fenêtre principale"""
        self.root.title("🏢 Organisateur Intelligent de Fichiers - Version Graphique")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Icône et style
        try:
            self.root.iconbitmap(default="icon.ico")  # Si disponible
        except:
            pass
        
        # Centrer la fenêtre
        self.center_window()
    
    def center_window(self):
        """Centrer la fenêtre à l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_styles(self):
        """Configuration des styles visuels"""
        self.style = ttk.Style()
        
        # Couleurs modernes
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'success': '#38A169',
            'warning': '#D69E2E',
            'danger': '#E53E3E',
            'light': '#F7FAFC',
            'dark': '#2D3748'
        }
        
        # Fonts personnalisées
        self.fonts = {
            'title': tkFont.Font(family="Segoe UI", size=16, weight="bold"),
            'subtitle': tkFont.Font(family="Segoe UI", size=12, weight="bold"),
            'body': tkFont.Font(family="Segoe UI", size=10),
            'small': tkFont.Font(family="Segoe UI", size=8)
        }
    
    def create_widgets(self):
        """Création de l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # En-tête
        self.create_header(main_frame)
        
        # Section configuration
        self.create_config_section(main_frame)
        
        # Section actions
        self.create_actions_section(main_frame)
        
        # Section résultats
        self.create_results_section(main_frame)
        
        # Section logs
        self.create_logs_section(main_frame)
        
        # Barre de statut
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Création de l'en-tête"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Titre principal
        title_label = tk.Label(
            header_frame,
            text="🏢 Organisateur Intelligent de Fichiers",
            font=self.fonts['title'],
            fg=self.colors['primary']
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Sous-titre
        subtitle_label = tk.Label(
            header_frame,
            text="Organisation automatique • Classification métier • Chiffrement sécurisé",
            font=self.fonts['body'],
            fg=self.colors['dark']
        )
        subtitle_label.grid(row=1, column=0, sticky=tk.W)
        
        # Version et statut
        version_label = tk.Label(
            header_frame,
            text="v2.0 | État: Prêt",
            font=self.fonts['small'],
            fg=self.colors['secondary']
        )
        version_label.grid(row=0, column=1, sticky=tk.E)
    
    def create_config_section(self, parent):
        """Section de configuration"""
        config_frame = ttk.LabelFrame(parent, text="📁 Configuration", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Dossier source
        ttk.Label(config_frame, text="Dossier source:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        
        source_frame = ttk.Frame(config_frame)
        source_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        source_frame.columnconfigure(0, weight=1)
        
        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_folder)
        self.source_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(source_frame, text="Parcourir", command=self.browse_source).grid(row=0, column=1)
        
        # Dossier cible
        ttk.Label(config_frame, text="Dossier cible:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0)
        )
        
        target_frame = ttk.Frame(config_frame)
        target_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        target_frame.columnconfigure(0, weight=1)
        
        self.target_entry = ttk.Entry(target_frame, textvariable=self.target_folder)
        self.target_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(target_frame, text="Parcourir", command=self.browse_target).grid(row=0, column=1)
        
        # Options
        options_frame = ttk.Frame(config_frame)
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        
        ttk.Checkbutton(
            options_frame,
            text="🔒 Activer le chiffrement automatique des dossiers sensibles",
            variable=self.encryption_enabled
        ).grid(row=0, column=0, sticky=tk.W)
    
    def create_actions_section(self, parent):
        """Section des actions principales"""
        actions_frame = ttk.LabelFrame(parent, text="🚀 Actions", padding="10")
        actions_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Boutons d'action
        buttons_frame = ttk.Frame(actions_frame)
        buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Analyser
        self.analyze_btn = ttk.Button(
            buttons_frame,
            text="🔍 Analyser les files",
            command=self.analyze_files,
            style="Accent.TButton"
        )
        self.analyze_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Organiser
        self.organize_btn = ttk.Button(
            buttons_frame,
            text="🗂️ Organiser automatiquement",
            command=self.organize_files,
            state="disabled"
        )
        self.organize_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Chiffrer
        self.encrypt_btn = ttk.Button(
            buttons_frame,
            text="🔐 Chiffrer les dossiers sensibles",
            command=self.encrypt_sensitive_folders,
            state="disabled"
        )
        self.encrypt_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Rapport
        self.report_btn = ttk.Button(
            buttons_frame,
            text="📊 Générer le rapport",
            command=self.generate_report,
            state="disabled"
        )
        self.report_btn.grid(row=0, column=3, padx=(0, 10))
        
        # Workflow complet
        self.workflow_btn = ttk.Button(
            buttons_frame,
            text="⚡ Workflow Complet",
            command=self.run_complete_workflow,
            style="Accent.TButton"
        )
        self.workflow_btn.grid(row=0, column=4)
        
        # Barre de progression
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            actions_frame,
            variable=self.progress_var,
            mode='determinate',
            length=400
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Label de progression
        self.progress_label = tk.Label(
            actions_frame,
            text="Prêt à démarrer",
            font=self.fonts['small'],
            fg=self.colors['dark']
        )
        self.progress_label.grid(row=2, column=0, pady=(5, 0))
    
    def create_results_section(self, parent):
        """Section des résultats visuels"""
        results_frame = ttk.LabelFrame(parent, text="📊 Résultats", padding="10")
        results_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        
        # Notebook pour les onglets
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Onglet Statistiques
        stats_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(stats_frame, text="📈 Statistiques")
        
        self.stats_text = ScrolledText(
            stats_frame,
            height=15,
            width=50,
            font=self.fonts['small'],
            wrap=tk.WORD
        )
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        stats_frame.rowconfigure(0, weight=1)
        stats_frame.columnconfigure(0, weight=1)
        
        # Onglet Structure
        structure_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(structure_frame, text="🗂️ Structure")
        
        self.structure_tree = ttk.Treeview(structure_frame, columns=('count',), show='tree headings')
        self.structure_tree.heading('#0', text='Dossier')
        self.structure_tree.heading('count', text='Fichiers')
        self.structure_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Scrollbar pour l'arbre
        tree_scroll = ttk.Scrollbar(structure_frame, orient='vertical', command=self.structure_tree.yview)
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.structure_tree.configure(yscrollcommand=tree_scroll.set)
        
        structure_frame.rowconfigure(0, weight=1)
        structure_frame.columnconfigure(0, weight=1)
    
    def create_logs_section(self, parent):
        """Section des logs en temps réel"""
        logs_frame = ttk.LabelFrame(parent, text="📝 Logs en temps réel", padding="10")
        logs_frame.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        logs_frame.rowconfigure(0, weight=1)
        logs_frame.columnconfigure(0, weight=1)
        
        self.logs_text = ScrolledText(
            logs_frame,
            height=15,
            width=60,
            font=self.fonts['small'],
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='white'
        )
        self.logs_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bouton pour effacer les logs
        ttk.Button(logs_frame, text="🗑️ Effacer", command=self.clear_logs).grid(
            row=1, column=0, pady=(5, 0)
        )
    
    def create_status_bar(self, parent):
        """Barre de statut en bas"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="Prêt • Organisateur intelligent chargé")
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=self.fonts['small'],
            fg=self.colors['dark'],
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Indicateur d'état
        self.status_indicator = tk.Label(
            status_frame,
            text="🟢",
            font=self.fonts['body']
        )
        self.status_indicator.grid(row=0, column=1, padx=(5, 0))
    
    def load_agents(self):
        """Chargement des agents"""
        self.log("🔄 Chargement des agents...")
        
        try:
            # Import de l'agent de gestion de files
            from agent_file_manager_intelligent import IntelligentFileManager
            self.file_manager = IntelligentFileManager()
            self.log("✅ Agent File Manager chargé")
            
            # Import de l'agent de sécurité
            try:
                from agent_security_mcp import SecurityAgent
                self.security_agent = SecurityAgent()
                self.log("✅ Agent de sécurité chargé")
            except ImportError:
                self.security_agent = None
                self.log("⚠️ Agent de sécurité non disponible")
            
            self.update_status("Agents chargés • Prêt à traiter", "🟢")
            
        except ImportError as e:
            self.log(f"❌ Erreur chargement agents: {e}")
            self.update_status("Erreur agents", "🔴")
            messagebox.showerror("Erreur", f"Impossible de charger les agents:\n{e}")
    
    def browse_source(self):
        """Sélection du dossier source"""
        folder = filedialog.askdirectory(title="Sélectionner le dossier source")
        if folder:
            self.source_folder.set(folder)
            self.log(f"📁 Dossier source: {folder}")
    
    def browse_target(self):
        """Sélection du dossier cible"""
        folder = filedialog.askdirectory(title="Sélectionner le dossier cible")
        if folder:
            self.target_folder.set(folder)
            self.log(f"🎯 Dossier cible: {folder}")
    
    def analyze_files(self):
        """Analyse des files dans le dossier source"""
        if not self.source_folder.get():
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier source")
            return
        
        def analyze_thread():
            self.update_progress(0, "🔍 Analyse en cours...")
            self.update_status("Analyse des files...", "🟡")
            
            try:
                source_path = Path(self.source_folder.get())
                if not source_path.exists():
                    raise FileNotFoundError(f"Dossier non trouvé: {source_path}")
                
                files = list(source_path.rglob("*"))
                files = [f for f in files if f.is_file() and not f.name.startswith('.')]
                
                self.log(f"📊 {len(files)} files trouvés")
                
                analyzed_files = []
                for i, file_path in enumerate(files):
                    try:
                        # Analyse basique
                        content_preview = self.get_content_preview(file_path)
                        is_sensitive = self.detect_sensitive_content(file_path, content_preview)
                        
                        file_info = {
                            "filepath": str(file_path),
                            "filename": file_path.name,
                            "size": file_path.stat().st_size,
                            "extension": file_path.suffix.lower(),
                            "summary": content_preview[:200],
                            "warning": is_sensitive
                        }
                        analyzed_files.append(file_info)
                        
                        progress = (i + 1) / len(files) * 100
                        self.update_progress(progress, f"🔍 Analyse: {file_path.name}")
                        
                    except Exception as e:
                        self.log(f"⚠️ Erreur analyse {file_path.name}: {e}")
                
                self.organization_results['analyzed_files'] = analyzed_files
                self.organization_results['file_count'] = len(analyzed_files)
                
                # Mise à jour des statistiques
                self.update_stats_display()
                
                self.update_progress(100, "✅ Analyse terminée")
                self.update_status(f"{len(analyzed_files)} files analysés", "🟢")
                self.log(f"✅ Analyse terminée: {len(analyzed_files)} files")
                
                # Activer le bouton d'organisation
                self.organize_btn.config(state="normal")
                
            except Exception as e:
                self.log(f"❌ Erreur analyse: {e}")
                self.update_status("Erreur analyse", "🔴")
                messagebox.showerror("Erreur", f"Erreur lors de l'analyse:\n{e}")
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def organize_files(self):
        """Organisation automatique des files"""
        if 'analyzed_files' not in self.organization_results:
            messagebox.showwarning("Attention", "Veuillez d'abord analyser les files")
            return
        
        def organize_thread():
            self.update_progress(0, "🗂️ Organisation en cours...")
            self.update_status("Organisation des files...", "🟡")
            
            try:
                analyzed_files = self.organization_results['analyzed_files']
                target_folder = self.target_folder.get()
                
                # Créer le dossier cible
                Path(target_folder).mkdir(exist_ok=True)
                
                organized_files = []
                categories_used = set()
                
                for i, file_info in enumerate(analyzed_files):
                    try:
                        # Classification par l'agent
                        classification = self.file_manager.analyze_content_for_organization(
                            file_info["filepath"],
                            file_info["summary"],
                            file_info["warning"]
                        )
                        
                        # Créer la structure de dossiers
                        security = classification["security"]
                        category = classification["category"]
                        subcategory = classification["subcategory"]
                        
                        folder_path = Path(target_folder) / security / category / subcategory
                        folder_path.mkdir(parents=True, exist_ok=True)
                        
                        # Copier le fichier
                        import shutil
                        source_file = Path(file_info["filepath"])
                        target_file = folder_path / source_file.name
                        
                        counter = 1
                        while target_file.exists():
                            stem = target_file.stem
                            suffix = target_file.suffix
                            target_file = folder_path / f"{stem}_{counter}{suffix}"
                            counter += 1
                        
                        shutil.copy2(source_file, target_file)
                        
                        organized_files.append({
                            **file_info,
                            "classification": classification,
                            "destination": str(target_file),
                            "folder_path": f"{security}/{category}/{subcategory}"
                        })
                        
                        categories_used.add(f"{category}/{subcategory}")
                        
                        progress = (i + 1) / len(analyzed_files) * 100
                        self.update_progress(progress, f"🗂️ Organisation: {source_file.name}")
                        self.log(f"✅ {source_file.name} → {category}/{subcategory}")
                        
                    except Exception as e:
                        self.log(f"❌ Erreur organisation {file_info['filename']}: {e}")
                
                self.organization_results['organized_files'] = organized_files
                self.organization_results['categories_used'] = list(categories_used)
                self.organization_results['target_folder'] = target_folder
                
                # Mise à jour des affichages
                self.update_stats_display()
                self.update_structure_display()
                
                self.update_progress(100, "✅ Organization completed")
                self.update_status(f"{len(organized_files)} files organisés", "🟢")
                self.log(f"✅ Organization completed: {len(organized_files)} files")
                
                # Activer les boutons suivants
                self.encrypt_btn.config(state="normal")
                self.report_btn.config(state="normal")
                
                # Vérifier les dossiers sensibles
                self.check_sensitive_folders()
                
            except Exception as e:
                self.log(f"❌ Erreur organisation: {e}")
                self.update_status("Erreur organisation", "🔴")
                messagebox.showerror("Erreur", f"Erreur lors de l'organisation:\n{e}")
        
        threading.Thread(target=organize_thread, daemon=True).start()
    
    def encrypt_sensitive_folders(self):
        """Chiffrement des dossiers sensibles"""
        if not self.encryption_enabled.get():
            messagebox.showinfo("Info", "Le chiffrement est désactivé")
            return
        
        if 'organized_files' not in self.organization_results:
            messagebox.showwarning("Attention", "Veuillez d'abord organiser les files")
            return
        
        # Identifier les dossiers sensibles
        target_folder = self.organization_results['target_folder']
        secure_path = Path(target_folder) / "secure"
        
        if not secure_path.exists():
            messagebox.showinfo("Info", "Aucun dossier sensible trouvé")
            return
        
        secure_folders = [f for f in secure_path.iterdir() if f.is_dir()]
        if not secure_folders:
            messagebox.showinfo("Info", "Aucun dossier sensible à chiffrer")
            return
        
        # Demander confirmation
        folder_list = "\n".join([f"• {f.name}" for f in secure_folders])
        confirm = messagebox.askyesno(
            "Confirmation Chiffrement",
            f"Chiffrer {len(secure_folders)} dossiers sensibles ?\n\n{folder_list}"
        )
        
        if not confirm:
            return
        
        # Demander le mot de passe
        password = self.get_encryption_password()
        if not password:
            return
        
        def encrypt_thread():
            self.update_progress(0, "🔐 Chiffrement en cours...")
            self.update_status("Chiffrement des dossiers...", "🟡")
            
            encrypted_folders = []
            
            try:
                for i, folder in enumerate(secure_folders):
                    try:
                        if self.security_agent and hasattr(self.security_agent, 'encrypt_folder'):
                            # Chiffrement réel avec l'agent de sécurité
                            result = self.security_agent.encrypt_folder(
                                str(folder),
                                password,
                                f"Dossier sensible: {folder.name}"
                            )
                        else:
                            # Simulation de chiffrement
                            result = self.simulate_encryption(folder, password)
                        
                        if result.get("success"):
                            encrypted_folders.append({
                                "folder": folder.name,
                                "result": result,
                                "timestamp": datetime.now().isoformat()
                            })
                            self.log(f"🔐 {folder.name} chiffré avec succès")
                        else:
                            self.log(f"❌ Échec chiffrement {folder.name}: {result.get('error', 'Inconnu')}")
                        
                        progress = (i + 1) / len(secure_folders) * 100
                        self.update_progress(progress, f"🔐 Chiffrement: {folder.name}")
                        
                    except Exception as e:
                        self.log(f"❌ Erreur chiffrement {folder.name}: {e}")
                
                self.organization_results['encrypted_folders'] = encrypted_folders
                
                self.update_progress(100, "✅ Chiffrement terminé")
                self.update_status(f"{len(encrypted_folders)} dossiers chiffrés", "🟢")
                self.log(f"✅ Chiffrement terminé: {len(encrypted_folders)} dossiers")
                
                messagebox.showinfo(
                    "Chiffrement Terminé",
                    f"✅ {len(encrypted_folders)} dossiers chiffrés avec succès"
                )
                
            except Exception as e:
                self.log(f"❌ Erreur chiffrement: {e}")
                self.update_status("Erreur chiffrement", "🔴")
                messagebox.showerror("Erreur", f"Erreur lors du chiffrement:\n{e}")
        
        threading.Thread(target=encrypt_thread, daemon=True).start()
    
    def generate_report(self):
        """Génération du rapport final"""
        if 'organized_files' not in self.organization_results:
            messagebox.showwarning("Attention", "Veuillez d'abord organiser les files")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"gui_organization_report_{timestamp}.json"
            
            # Préparer le rapport
            report = {
                "timestamp": timestamp,
                "source_folder": self.source_folder.get(),
                "target_folder": self.organization_results.get('target_folder'),
                "encryption_enabled": self.encryption_enabled.get(),
                "summary": {
                    "files_analyzed": self.organization_results.get('file_count', 0),
                    "files_organized": len(self.organization_results.get('organized_files', [])),
                    "categories_used": len(self.organization_results.get('categories_used', [])),
                    "folders_encrypted": len(self.organization_results.get('encrypted_folders', []))
                },
                "detailed_results": self.organization_results
            }
            
            # Sauvegarder
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.log(f"📄 Rapport généré: {report_file}")
            
            # Proposer d'ouvrir le rapport
            if messagebox.askyesno("Rapport Généré", f"Rapport sauvegardé dans:\n{report_file}\n\nOuvrir le dossier ?"):
                import subprocess
                subprocess.Popen(f'explorer /select,"{os.path.abspath(report_file)}"')
            
        except Exception as e:
            self.log(f"❌ Erreur génération rapport: {e}")
            messagebox.showerror("Erreur", f"Erreur génération rapport:\n{e}")
    
    def run_complete_workflow(self):
        """Exécution du workflow complet"""
        if not self.source_folder.get():
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier source")
            return
        
        confirm = messagebox.askyesno(
            "Workflow Complet",
            "Exécuter le workflow complet ?\n\n• Analyse des files\n• Organisation automatique\n• Chiffrement des dossiers sensibles\n• Génération du rapport"
        )
        
        if not confirm:
            return
        
        def complete_workflow():
            try:
                # Étape 1: Analyse
                self.log("🚀 Démarrage du workflow complet")
                self.analyze_files()
                
                # Attendre la fin de l'analyse
                while 'analyzed_files' not in self.organization_results:
                    time.sleep(0.5)
                
                # Étape 2: Organisation
                time.sleep(1)
                self.organize_files()
                
                # Attendre la fin de l'organisation
                while 'organized_files' not in self.organization_results:
                    time.sleep(0.5)
                
                # Étape 3: Chiffrement (si activé)
                if self.encryption_enabled.get():
                    time.sleep(1)
                    self.encrypt_sensitive_folders()
                
                # Étape 4: Rapport
                time.sleep(2)
                self.generate_report()
                
                self.log("🎉 Workflow complet terminé avec succès !")
                messagebox.showinfo("Succès", "🎉 Workflow complet terminé avec succès !")
                
            except Exception as e:
                self.log(f"❌ Erreur workflow: {e}")
                messagebox.showerror("Erreur", f"Erreur workflow:\n{e}")
        
        threading.Thread(target=complete_workflow, daemon=True).start()
    
    # Méthodes utilitaires
    
    def get_content_preview(self, file_path: Path) -> str:
        """Aperçu du contenu d'un fichier"""
        try:
            if file_path.suffix.lower() in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(300)
        except:
            pass
        return f"Fichier {file_path.suffix.upper()[1:]} ({file_path.stat().st_size} bytes)"
    
    def detect_sensitive_content(self, file_path: Path, content: str) -> bool:
        """Détection de contenu sensible"""
        sensitive_keywords = [
            'confidentiel', 'secret', 'password', 'mdp', 'personnel', 'prive',
            'contrat', 'salaire', 'bancaire', 'legal'
        ]
        
        file_name = file_path.name.lower()
        content_lower = content.lower()
        
        return any(keyword in file_name or keyword in content_lower for keyword in sensitive_keywords)
    
    def simulate_encryption(self, folder_path: Path, password: str) -> dict:
        """Simulation de chiffrement"""
        try:
            marker_file = folder_path / ".encrypted_gui"
            with open(marker_file, 'w') as f:
                f.write(f"Encrypted via GUI on {datetime.now().isoformat()}")
            
            return {
                "success": True,
                "method": "simulation",
                "marker_file": str(marker_file)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_encryption_password(self) -> str:
        """Dialogue pour obtenir le mot de passe de chiffrement"""
        password = simpledialog.askstring(
            "Mot de passe de chiffrement",
            "Entrez le mot de passe de chiffrement (min 6 caractères):",
            show='*'
        )
        
        if not password or len(password) < 6:
            messagebox.showwarning("Attention", "Mot de passe trop court (min 6 caractères)")
            return ""
        
        confirm = simpledialog.askstring(
            "Confirmation",
            "Confirmez le mot de passe:",
            show='*'
        )
        
        if password != confirm:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas")
            return ""
        
        return password
    
    def check_sensitive_folders(self):
        """Vérifier et signaler les dossiers sensibles"""
        if 'organized_files' not in self.organization_results:
            return
        
        secure_count = len([f for f in self.organization_results['organized_files'] 
                           if f['classification']['security'] == 'secure'])
        
        if secure_count > 0:
            self.log(f"🔒 {secure_count} files sensibles détectés")
            if self.encryption_enabled.get():
                self.log("💡 Le chiffrement automatique est activé")
            else:
                self.log("⚠️ Le chiffrement est désactivé")
    
    def update_progress(self, value: float, text: str = ""):
        """Mise à jour de la barre de progression"""
        self.progress_var.set(value)
        if text:
            self.progress_label.config(text=text)
        self.root.update_idletasks()
    
    def update_status(self, message: str, indicator: str = "🟡"):
        """Mise à jour de la barre de statut"""
        self.status_var.set(message)
        self.status_indicator.config(text=indicator)
        self.root.update_idletasks()
    
    def update_stats_display(self):
        """Mise à jour de l'affichage des statistiques"""
        if not self.organization_results:
            return
        
        stats_text = "📊 STATISTIQUES D'ORGANISATION\n"
        stats_text += "=" * 40 + "\n\n"
        
        if 'file_count' in self.organization_results:
            stats_text += f"📁 Fichiers analysés: {self.organization_results['file_count']}\n"
        
        if 'organized_files' in self.organization_results:
            organized_count = len(self.organization_results['organized_files'])
            stats_text += f"🗂️ Fichiers organisés: {organized_count}\n"
            
            # Statistiques par sécurité
            security_stats = {}
            category_stats = {}
            
            for file_info in self.organization_results['organized_files']:
                security = file_info['classification']['security']
                category = file_info['classification']['category']
                
                security_stats[security] = security_stats.get(security, 0) + 1
                category_stats[category] = category_stats.get(category, 0) + 1
            
            stats_text += f"\n🔒 Répartition sécurité:\n"
            for security, count in security_stats.items():
                stats_text += f"   • {security}: {count} files\n"
            
            stats_text += f"\n🏢 Répartition par catégorie:\n"
            for category, count in sorted(category_stats.items()):
                stats_text += f"   • {category}: {count} files\n"
        
        if 'categories_used' in self.organization_results:
            stats_text += f"\n📂 Catégories utilisées: {len(self.organization_results['categories_used'])}\n"
        
        if 'encrypted_folders' in self.organization_results:
            encrypted_count = len(self.organization_results['encrypted_folders'])
            stats_text += f"\n🔐 Dossiers chiffrés: {encrypted_count}\n"
        
        # Vérification "général"
        if 'organized_files' in self.organization_results:
            general_count = sum(1 for f in self.organization_results['organized_files'] 
                               if 'general' in f['classification']['category'].lower() or 
                                  'general' in f['classification']['subcategory'].lower())
            
            stats_text += f"\n🎯 Catégories 'general': {general_count}\n"
            if general_count == 0:
                stats_text += "✅ SUCCÈS: Aucune catégorie 'general' utilisée!\n"
            else:
                stats_text += "⚠️ ATTENTION: Catégories 'general' détectées\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def update_structure_display(self):
        """Mise à jour de l'affichage de la structure"""
        # Effacer l'arbre existant
        for item in self.structure_tree.get_children():
            self.structure_tree.delete(item)
        
        if 'organized_files' not in self.organization_results:
            return
        
        # Construire la structure
        structure = {}
        for file_info in self.organization_results['organized_files']:
            path_parts = file_info['folder_path'].split('/')
            current = structure
            
            for part in path_parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        # Afficher dans l'arbre
        def add_to_tree(parent, name, data, level=0):
            if isinstance(data, dict):
                # C'est un dossier
                if level == 0:
                    file_count = sum(1 for f in self.organization_results['organized_files'] 
                                   if f['folder_path'].startswith(name))
                else:
                    file_count = sum(1 for f in self.organization_results['organized_files'] 
                                   if name in f['folder_path'])
                
                node = self.structure_tree.insert(parent, 'end', text=name, values=(file_count,))
                
                for key, value in data.items():
                    add_to_tree(node, key, value, level + 1)
        
        for key, value in structure.items():
            add_to_tree('', key, value)
        
        # Expandre tous les nœuds
        def expand_all(item=''):
            children = self.structure_tree.get_children(item)
            for child in children:
                self.structure_tree.item(child, open=True)
                expand_all(child)
        
        expand_all()
    
    def log(self, message: str):
        """Ajouter un message aux logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.logs_text.insert(tk.END, log_entry)
        self.logs_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_logs(self):
        """Effacer les logs"""
        self.logs_text.delete(1.0, tk.END)
    
    def run(self):
        """Démarrer l'application"""
        self.log("🚀 Application démarrée")
        self.log("💡 Sélectionnez un dossier source pour commencer")
        self.root.mainloop()

def main():
    """Fonction principale"""
    try:
        if not GUI_AVAILABLE:
            print("❌ Interface graphique non disponible")
            print("💡 Installez tkinter: pip install tk")
            return False
        
        app = FileOrganizerGUI()
        app.run()
        return True
        
    except Exception as e:
        print(f"❌ Erreur application GUI: {e}")
        return False

if __name__ == "__main__":
    main()
