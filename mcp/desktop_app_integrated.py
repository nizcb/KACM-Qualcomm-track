"""
Interface Desktop Intégrée avec API
==================================

Version améliorée de l'interface desktop qui communique
directement avec l'API FastAPI du système multi-agents.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import customtkinter as ctk
import asyncio
import threading
import json
import os
import sys
import requests
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Configuration CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiAgentDesktopAppIntegrated:
    """Application Desktop intégrée avec API FastAPI"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🤖 Multi-Agent System - KACM Qualcomm Hackathon")
        self.root.geometry("1400x900")
        
        # Configuration API
        self.api_base_url = "http://localhost:8000"
        self.api_process = None
        self.api_running = False
        
        # Variables d'état
        self.current_directory = None
        self.processed_files = {}
        self.vault_files = {}
        self.system_status = "Arrêté"
        
        # Initialisation de l'interface
        self.setup_ui()
        
        # Démarrage automatique de l'API
        self.start_api_server()
        
        # Vérification périodique de l'API
        self.check_api_status()
    
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        
        # === HEADER ===
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🤖 Multi-Agent System - KACM Qualcomm", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # Status API
        self.api_status_label = ctk.CTkLabel(
            header_frame,
            text="🔴 API: Démarrage...",
            font=ctk.CTkFont(size=14)
        )
        self.api_status_label.pack(side="right", padx=10, pady=10)
        
        # Status System
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="🔴 Système: Arrêté",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(side="right", padx=10, pady=10)
        
        # === MAIN CONTAINER ===
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # === LEFT PANEL: DIRECTORY & ACTIONS ===
        left_panel = ctk.CTkFrame(main_container)
        left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Directory Selection
        dir_frame = ctk.CTkFrame(left_panel)
        dir_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(dir_frame, text="📁 Dossier à analyser:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        dir_select_frame = ctk.CTkFrame(dir_frame)
        dir_select_frame.pack(fill="x", padx=10, pady=5)
        
        self.dir_path_var = tk.StringVar()
        self.dir_entry = ctk.CTkEntry(
            dir_select_frame,
            textvariable=self.dir_path_var,
            placeholder_text="Sélectionnez un dossier à analyser...",
            width=400
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        browse_btn = ctk.CTkButton(
            dir_select_frame,
            text="📂 Parcourir",
            command=self.browse_directory,
            width=100
        )
        browse_btn.pack(side="right", padx=5)
        
        # Process Button
        self.process_btn = ctk.CTkButton(
            dir_frame,
            text="🚀 Analyser le Dossier",
            command=self.process_directory,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.process_btn.pack(fill="x", padx=10, pady=10)
        
        # === SMART SEARCH ===
        search_frame = ctk.CTkFrame(left_panel)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(search_frame, text="🔍 Recherche Intelligente avec IA:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        search_input_frame = ctk.CTkFrame(search_frame)
        search_input_frame.pack(fill="x", padx=10, pady=5)
        
        self.search_entry = ctk.CTkEntry(
            search_input_frame,
            placeholder_text="Ex: trouve moi le scan de ma carte vitale...",
            width=400
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        search_btn = ctk.CTkButton(
            search_input_frame,
            text="🤖 Rechercher",
            command=self.smart_search,
            width=120
        )
        search_btn.pack(side="right", padx=5)
        
        # Exemples de recherche
        examples_frame = ctk.CTkFrame(search_frame)
        examples_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(examples_frame, text="💡 Exemples:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=2)
        
        examples = [
            "trouve moi le scan de ma carte vitale",
            "donne moi le pdf de cours d'histoire",
            "où est ma photo d'identité",
            "liste les factures de ce mois"
        ]
        
        for example in examples:
            btn = ctk.CTkButton(
                examples_frame,
                text=f"• {example}",
                command=lambda e=example: self.search_entry.insert(0, e),
                width=20,
                height=25,
                font=ctk.CTkFont(size=11)
            )
            btn.pack(anchor="w", padx=5, pady=1)
        
        # === PROGRESS ===
        progress_frame = ctk.CTkFrame(left_panel)
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(progress_frame, text="📊 Progression:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="Prêt")
        self.progress_label.pack(anchor="w", padx=10, pady=2)
        
        # === RIGHT PANEL: RESULTS ===
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Results Header
        results_header = ctk.CTkFrame(right_panel)
        results_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(results_header, text="📋 Résultats:", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=10, pady=5)
        
        refresh_btn = ctk.CTkButton(
            results_header,
            text="🔄 Actualiser",
            command=self.refresh_results,
            width=100
        )
        refresh_btn.pack(side="right", padx=10, pady=5)
        
        # Results Notebook (Tabs)
        self.results_notebook = ctk.CTkTabview(right_panel)
        self.results_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tab 1: Fichiers Analysés
        self.results_notebook.add("📄 Fichiers Analysés")
        files_frame = self.results_notebook.tab("📄 Fichiers Analysés")
        
        # Créer un frame avec scrollbar pour le treeview
        tree_frame = ctk.CTkFrame(files_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.files_tree = ttk.Treeview(
            tree_frame, 
            columns=("Type", "Agent", "Statut", "Sensible", "Taille"), 
            show="tree headings"
        )
        self.files_tree.heading("#0", text="Fichier")
        self.files_tree.heading("Type", text="Type")
        self.files_tree.heading("Agent", text="Agent")
        self.files_tree.heading("Statut", text="Statut")
        self.files_tree.heading("Sensible", text="Sensible")
        self.files_tree.heading("Taille", text="Taille")
        
        # Ajuster la largeur des colonnes
        self.files_tree.column("#0", width=200)
        self.files_tree.column("Type", width=80)
        self.files_tree.column("Agent", width=100)
        self.files_tree.column("Statut", width=100)
        self.files_tree.column("Sensible", width=80)
        self.files_tree.column("Taille", width=80)
        
        self.files_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Double-clic pour ouvrir le fichier
        self.files_tree.bind("<Double-1>", self.on_file_double_click)
        
        # Tab 2: Vault Sécurisé
        self.results_notebook.add("🔒 Vault Sécurisé")
        vault_frame = self.results_notebook.tab("🔒 Vault Sécurisé")
        
        vault_tree_frame = ctk.CTkFrame(vault_frame)
        vault_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.vault_tree = ttk.Treeview(
            vault_tree_frame, 
            columns=("Date", "Taille", "Actions"), 
            show="tree headings"
        )
        self.vault_tree.heading("#0", text="Fichier Chiffré")
        self.vault_tree.heading("Date", text="Date")
        self.vault_tree.heading("Taille", text="Taille")
        self.vault_tree.heading("Actions", text="Actions")
        
        self.vault_tree.column("#0", width=200)
        self.vault_tree.column("Date", width=150)
        self.vault_tree.column("Taille", width=100)
        self.vault_tree.column("Actions", width=100)
        
        self.vault_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Double-clic pour déchiffrer
        self.vault_tree.bind("<Double-1>", self.on_vault_double_click)
        
        # Tab 3: Recherche
        self.results_notebook.add("🔍 Résultats de Recherche")
        search_results_frame = self.results_notebook.tab("🔍 Résultats de Recherche")
        
        self.search_results_text = ctk.CTkTextbox(search_results_frame)
        self.search_results_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab 4: Logs
        self.results_notebook.add("📝 Logs")
        logs_frame = self.results_notebook.tab("📝 Logs")
        
        self.logs_text = ctk.CTkTextbox(logs_frame)
        self.logs_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # === BOTTOM PANEL: ACTIONS ===
        bottom_panel = ctk.CTkFrame(self.root)
        bottom_panel.pack(fill="x", padx=10, pady=5)
        
        # System Controls
        system_frame = ctk.CTkFrame(bottom_panel)
        system_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(system_frame, text="⚙️ Contrôles Système:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        controls_frame = ctk.CTkFrame(system_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        start_btn = ctk.CTkButton(controls_frame, text="🟢 Démarrer Agents", command=self.start_system, width=120)
        start_btn.pack(side="left", padx=5)
        
        stop_btn = ctk.CTkButton(controls_frame, text="🔴 Arrêter Agents", command=self.stop_system, width=120)
        stop_btn.pack(side="left", padx=5)
        
        status_btn = ctk.CTkButton(controls_frame, text="📊 Statut", command=self.check_status, width=100)
        status_btn.pack(side="left", padx=5)
        
        # API Controls
        api_frame = ctk.CTkFrame(bottom_panel)
        api_frame.pack(side="right", fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(api_frame, text="🌐 API:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        api_controls_frame = ctk.CTkFrame(api_frame)
        api_controls_frame.pack(fill="x", padx=10, pady=5)
        
        api_docs_btn = ctk.CTkButton(api_controls_frame, text="📚 Docs API", command=self.open_api_docs, width=100)
        api_docs_btn.pack(side="left", padx=5)
        
        restart_api_btn = ctk.CTkButton(api_controls_frame, text="🔄 Restart API", command=self.restart_api, width=100)
        restart_api_btn.pack(side="left", padx=5)
    
    def start_api_server(self):
        """Démarrer le serveur API"""
        self.log_message("Démarrage du serveur API...")
        
        def start_api():
            try:
                # Commande pour démarrer l'API
                api_script = Path(__file__).parent / "api_server.py"
                
                # Utiliser WSL si disponible
                if os.name == 'nt':  # Windows
                    cmd = [
                        "wsl", "-e", "bash", "-c",
                        f"cd /mnt/c/Users/chaki/Desktop/hackathon/KACM-Qualcomm-track/mcp && python3 api_server.py"
                    ]
                else:
                    cmd = ["python3", str(api_script)]
                
                self.api_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.log_message("Serveur API démarré")
                self.api_running = True
                
            except Exception as e:
                self.log_message(f"Erreur lors du démarrage de l'API: {e}")
        
        # Démarrer dans un thread séparé
        threading.Thread(target=start_api, daemon=True).start()
    
    def check_api_status(self):
        """Vérifier le statut de l'API"""
        def check():
            try:
                response = requests.get(f"{self.api_base_url}/health", timeout=5)
                if response.status_code == 200:
                    self.root.after(0, lambda: self.api_status_label.configure(text="🟢 API: Connectée"))
                    self.api_running = True
                else:
                    self.root.after(0, lambda: self.api_status_label.configure(text="🔴 API: Erreur"))
                    self.api_running = False
            except:
                self.root.after(0, lambda: self.api_status_label.configure(text="🔴 API: Déconnectée"))
                self.api_running = False
        
        # Vérifier toutes les 10 secondes
        threading.Thread(target=check, daemon=True).start()
        self.root.after(10000, self.check_api_status)
    
    def api_request(self, endpoint, method="GET", data=None):
        """Effectuer une requête API"""
        if not self.api_running:
            raise Exception("API non disponible")
        
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"Méthode {method} non supportée")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur API: {e}")
    
    def browse_directory(self):
        """Parcourir et sélectionner un dossier"""
        directory = filedialog.askdirectory(title="Sélectionner un dossier à analyser")
        if directory:
            self.dir_path_var.set(directory)
            self.current_directory = directory
            self.log_message(f"Dossier sélectionné: {directory}")
    
    def process_directory(self):
        """Analyser le dossier sélectionné"""
        if not self.current_directory:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier d'abord")
            return
        
        if not self.api_running:
            messagebox.showerror("Erreur", "API non disponible. Veuillez redémarrer l'API.")
            return
        
        self.log_message(f"Démarrage de l'analyse du dossier: {self.current_directory}")
        self.progress_label.configure(text="Analyse en cours...")
        self.progress_bar.set(0.1)
        self.process_btn.configure(state="disabled")
        
        # Lancement asynchrone du traitement
        threading.Thread(target=self.process_directory_async, daemon=True).start()
    
    def process_directory_async(self):
        """Traitement asynchrone du dossier"""
        try:
            # Appel API
            data = {
                "directory_path": self.current_directory,
                "recursive": True
            }
            
            result = self.api_request("/process/directory", "POST", data)
            
            if result.get("success"):
                self.processed_files = {
                    result["session_id"]: result
                }
                
                # Mise à jour de l'interface
                self.root.after(0, self.update_files_display)
                self.root.after(0, lambda: self.progress_bar.set(1.0))
                self.root.after(0, lambda: self.progress_label.configure(text="Analyse terminée"))
                self.root.after(0, lambda: self.log_message(f"Analyse terminée: {result['processed_files']} fichiers traités"))
            else:
                self.root.after(0, lambda: self.log_message("Erreur lors de l'analyse"))
        
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Erreur lors de l'analyse: {str(e)}"))
        
        finally:
            self.root.after(0, lambda: self.process_btn.configure(state="normal"))
    
    def smart_search(self):
        """Recherche intelligente avec IA"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Attention", "Veuillez entrer une requête de recherche")
            return
        
        if not self.api_running:
            messagebox.showerror("Erreur", "API non disponible. Veuillez redémarrer l'API.")
            return
        
        self.log_message(f"Recherche IA: {query}")
        self.search_results_text.delete("1.0", "end")
        self.search_results_text.insert("1.0", "🔍 Recherche en cours...\n")
        
        # Basculer vers l'onglet des résultats
        self.results_notebook.set("🔍 Résultats de Recherche")
        
        # Lancement asynchrone de la recherche
        threading.Thread(target=self.smart_search_async, args=(query,), daemon=True).start()
    
    def smart_search_async(self, query):
        """Recherche asynchrone avec IA"""
        try:
            # Appel API
            data = {
                "query": query,
                "search_type": "semantic",
                "include_vault": True
            }
            
            result = self.api_request("/search/smart", "POST", data)
            
            if result.get("success"):
                self.root.after(0, lambda: self.display_search_results(result))
            else:
                self.root.after(0, lambda: self.log_message("Aucun résultat trouvé"))
        
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Erreur lors de la recherche: {str(e)}"))
    
    def display_search_results(self, result):
        """Afficher les résultats de recherche"""
        self.search_results_text.delete("1.0", "end")
        
        content = f"🔍 Résultats pour: {result['query']}\n"
        content += f"⏱️ Temps de recherche: {result['search_time']:.2f}s\n"
        content += f"📊 Nombre de résultats: {result['total_results']}\n\n"
        
        for i, res in enumerate(result['results'], 1):
            content += f"{'='*50}\n"
            content += f"📄 Résultat {i}: {res.get('filename', 'N/A')}\n"
            content += f"📂 Type: {res.get('type', 'N/A')}\n"
            content += f"📍 Emplacement: {res.get('location', 'N/A')}\n"
            
            if res.get('requires_auth'):
                content += f"🔒 Authentification requise: OUI\n"
                content += f"🔑 Vault ID: {res.get('vault_id', 'N/A')}\n"
            else:
                content += f"🔒 Authentification requise: NON\n"
            
            if 'confidence' in res:
                content += f"🎯 Confiance: {res['confidence']:.2%}\n"
            
            content += f"\n"
        
        self.search_results_text.insert("1.0", content)
        
        # Si le fichier nécessite une authentification
        if result['results'] and result['results'][0].get('requires_auth'):
            self.root.after(1000, lambda: self.prompt_for_decryption(result['results'][0]))
    
    def prompt_for_decryption(self, file_info):
        """Demander le déchiffrement d'un fichier"""
        if messagebox.askyesno("Fichier Chiffré", f"Le fichier '{file_info['filename']}' est chiffré.\nVoulez-vous le déchiffrer?"):
            password = simpledialog.askstring(
                "Authentification",
                "Veuillez saisir la phrase de passe:",
                show="*"
            )
            
            if password:
                self.decrypt_file(file_info['vault_id'], password)
    
    def decrypt_file(self, vault_id, password):
        """Déchiffrer un fichier"""
        try:
            data = {
                "file_path": f"vault:{vault_id}",
                "action": "decrypt",
                "password": password
            }
            
            result = self.api_request("/file/decrypt", "POST", data)
            
            if result.get("success"):
                self.log_message(f"Déchiffrement réussi: {result['message']}")
                
                # Proposer d'ouvrir le fichier
                if messagebox.askyesno("Déchiffrement Réussi", f"{result['message']}\n\nVoulez-vous ouvrir le fichier?"):
                    self.open_file(result['result_path'])
            else:
                messagebox.showerror("Erreur", "Échec du déchiffrement")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du déchiffrement: {str(e)}")
    
    def open_file(self, file_path):
        """Ouvrir un fichier"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            else:  # Linux/Mac
                subprocess.run(['xdg-open', file_path])
            
            self.log_message(f"Fichier ouvert: {file_path}")
        
        except Exception as e:
            self.log_message(f"Erreur lors de l'ouverture: {str(e)}")
    
    def update_files_display(self):
        """Mettre à jour l'affichage des fichiers"""
        # Vider l'arbre
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        # Remplir avec les nouveaux résultats
        for session_id, session_data in self.processed_files.items():
            for file_result in session_data.get('results', []):
                filename = Path(file_result['filename']).name
                file_type = file_result.get('extension', 'N/A')
                agent_type = file_result.get('agent_type', 'N/A')
                status = "Chiffré" if file_result.get('is_sensitive') else "Analysé"
                sensitive = "Oui" if file_result.get('is_sensitive') else "Non"
                size = self.format_size(file_result.get('size', 0))
                
                self.files_tree.insert("", "end", 
                                     text=filename, 
                                     values=(file_type, agent_type, status, sensitive, size))
        
        # Mettre à jour le vault
        self.update_vault_display()
    
    def update_vault_display(self):
        """Mettre à jour l'affichage du vault"""
        try:
            vault_data = self.api_request("/vault/list")
            
            # Vider l'arbre du vault
            for item in self.vault_tree.get_children():
                self.vault_tree.delete(item)
            
            # Remplir avec les fichiers du vault
            for vault_id, vault_info in vault_data.get('files', {}).items():
                filename = vault_info.get('filename', 'N/A')
                date = vault_info.get('encrypted_at', 'N/A')
                if date != 'N/A':
                    date = datetime.fromisoformat(date).strftime("%Y-%m-%d %H:%M")
                size = self.format_size(vault_info.get('size', 0))
                
                self.vault_tree.insert("", "end", 
                                     text=filename, 
                                     values=(date, size, "🔓 Déchiffrer"))
        
        except Exception as e:
            self.log_message(f"Erreur lors de la mise à jour du vault: {str(e)}")
    
    def format_size(self, size_bytes):
        """Formater la taille en octets"""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB"
    
    def on_file_double_click(self, event):
        """Gestionnaire de double-clic sur fichier"""
        selection = self.files_tree.selection()
        if selection:
            item = self.files_tree.item(selection[0])
            filename = item['text']
            sensitive = item['values'][3] == "Oui"
            
            if sensitive:
                messagebox.showinfo("Fichier Sensible", f"Le fichier '{filename}' est dans le vault sécurisé.\nUtilisez l'onglet Vault pour le déchiffrer.")
            else:
                messagebox.showinfo("Fichier", f"Fichier: {filename}\nOuverture non implémentée dans la démo.")
    
    def on_vault_double_click(self, event):
        """Gestionnaire de double-clic sur fichier du vault"""
        selection = self.vault_tree.selection()
        if selection:
            item = self.vault_tree.item(selection[0])
            filename = item['text']
            
            password = simpledialog.askstring(
                "Déchiffrement",
                f"Déchiffrer le fichier '{filename}'.\nVeuillez saisir la phrase de passe:",
                show="*"
            )
            
            if password:
                # Ici on devrait récupérer le vault_id correspondant
                # Pour la démo, on utilise un ID simulé
                vault_id = "sample_vault_id"
                self.decrypt_file(vault_id, password)
    
    def refresh_results(self):
        """Actualiser les résultats"""
        self.log_message("Actualisation des résultats...")
        self.update_files_display()
    
    def start_system(self):
        """Démarrer le système multi-agents"""
        if not self.api_running:
            messagebox.showerror("Erreur", "API non disponible. Veuillez redémarrer l'API.")
            return
        
        self.log_message("Démarrage du système multi-agents...")
        
        threading.Thread(target=self.start_system_async, daemon=True).start()
    
    def start_system_async(self):
        """Démarrage asynchrone du système"""
        try:
            result = self.api_request("/system/start", "POST")
            
            if result.get("success"):
                self.root.after(0, lambda: self.status_label.configure(text="🟢 Système: Démarré"))
                self.root.after(0, lambda: self.log_message("Système multi-agents démarré"))
            else:
                self.root.after(0, lambda: self.log_message("Erreur lors du démarrage"))
        
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Erreur lors du démarrage: {str(e)}"))
    
    def stop_system(self):
        """Arrêter le système multi-agents"""
        if not self.api_running:
            messagebox.showwarning("Attention", "API non disponible.")
            return
        
        self.log_message("Arrêt du système multi-agents...")
        
        threading.Thread(target=self.stop_system_async, daemon=True).start()
    
    def stop_system_async(self):
        """Arrêt asynchrone du système"""
        try:
            result = self.api_request("/system/stop", "POST")
            
            if result.get("success"):
                self.root.after(0, lambda: self.status_label.configure(text="🔴 Système: Arrêté"))
                self.root.after(0, lambda: self.log_message("Système multi-agents arrêté"))
            else:
                self.root.after(0, lambda: self.log_message("Erreur lors de l'arrêt"))
        
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Erreur lors de l'arrêt: {str(e)}"))
    
    def check_status(self):
        """Vérifier le statut du système"""
        if not self.api_running:
            messagebox.showwarning("Attention", "API non disponible.")
            return
        
        threading.Thread(target=self.check_status_async, daemon=True).start()
    
    def check_status_async(self):
        """Vérification asynchrone du statut"""
        try:
            result = self.api_request("/system/status")
            
            status_text = f"Statut: {result['status']}\n"
            status_text += f"Uptime: {result['uptime']:.2f}s\n"
            status_text += f"Dernière activité: {result['last_activity']}\n\n"
            status_text += "Agents:\n"
            
            for agent_name, agent_info in result['agents'].items():
                status_text += f"  • {agent_name}: {agent_info['status']} (port {agent_info['port']})\n"
            
            self.root.after(0, lambda: messagebox.showinfo("Statut Système", status_text))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors de la vérification: {str(e)}"))
    
    def open_api_docs(self):
        """Ouvrir la documentation API"""
        import webbrowser
        webbrowser.open(f"{self.api_base_url}/docs")
    
    def restart_api(self):
        """Redémarrer l'API"""
        if self.api_process:
            self.api_process.terminate()
        
        self.start_api_server()
    
    def log_message(self, message):
        """Ajouter un message aux logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Ajouter au widget de logs
        self.logs_text.insert("end", log_entry)
        self.logs_text.see("end")
        
        # Log également dans la console
        logger.info(message)
    
    def on_closing(self):
        """Gestionnaire de fermeture de l'application"""
        if self.api_process:
            self.api_process.terminate()
        
        self.root.destroy()
    
    def run(self):
        """Lancer l'application"""
        self.log_message("Démarrage de l'interface Multi-Agent System intégrée")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Fonction principale"""
    try:
        app = MultiAgentDesktopAppIntegrated()
        app.run()
    except Exception as e:
        print(f"Erreur lors du démarrage de l'application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
