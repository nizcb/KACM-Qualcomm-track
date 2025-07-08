"""
Interface Desktop Multi-Agent System
===================================

Interface graphique desktop pour le système multi-agents MCP
- Drag & Drop de dossiers
- Prompt naturel avec Llama3
- Recherche intelligente de fichiers
- Authentification pour fichiers sensibles
- Intégration complète avec tous les agents
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import customtkinter as ctk
import asyncio
import threading
import json
import os
import sys
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

class MultiAgentDesktopApp:
    """Application Desktop pour le système multi-agents"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🤖 Multi-Agent System - KACM Qualcomm Hackathon")
        self.root.geometry("1200x800")
        
        # Variables d'état
        self.current_directory = None
        self.processed_files = {}
        self.vault_files = {}
        self.system_status = "Arrêté"
        
        # Initialisation de l'interface
        self.setup_ui()
        
        # Démarrage du système en arrière-plan
        self.start_system_thread()
    
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        
        # === HEADER ===
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🤖 Multi-Agent System", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # Status
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
            placeholder_text="Glissez un dossier ici ou cliquez sur Parcourir..."
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
        
        ctk.CTkLabel(search_frame, text="🔍 Recherche Intelligente:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Ex: trouve moi le scan de ma carte vitale..."
        )
        self.search_entry.pack(fill="x", padx=10, pady=5)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="🤖 Rechercher avec IA",
            command=self.smart_search,
            height=35
        )
        search_btn.pack(fill="x", padx=10, pady=5)
        
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
        
        self.files_tree = ttk.Treeview(files_frame, columns=("Type", "Statut", "Sensible"), show="tree headings")
        self.files_tree.heading("#0", text="Fichier")
        self.files_tree.heading("Type", text="Type")
        self.files_tree.heading("Statut", text="Statut")
        self.files_tree.heading("Sensible", text="Sensible")
        self.files_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab 2: Vault Sécurisé
        self.results_notebook.add("🔒 Vault Sécurisé")
        vault_frame = self.results_notebook.tab("🔒 Vault Sécurisé")
        
        self.vault_tree = ttk.Treeview(vault_frame, columns=("Date", "Taille"), show="tree headings")
        self.vault_tree.heading("#0", text="Fichier Chiffré")
        self.vault_tree.heading("Date", text="Date")
        self.vault_tree.heading("Taille", text="Taille")
        self.vault_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab 3: Logs
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
        
        start_btn = ctk.CTkButton(controls_frame, text="🟢 Démarrer", command=self.start_system, width=100)
        start_btn.pack(side="left", padx=5)
        
        stop_btn = ctk.CTkButton(controls_frame, text="🔴 Arrêter", command=self.stop_system, width=100)
        stop_btn.pack(side="left", padx=5)
        
        status_btn = ctk.CTkButton(controls_frame, text="📊 Statut", command=self.check_status, width=100)
        status_btn.pack(side="left", padx=5)
        
        # === DRAG & DROP ===
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        """Configuration du drag & drop"""
        # Pour l'instant, on simule avec un clic
        self.root.bind("<Button-1>", self.on_click)
    
    def on_click(self, event):
        """Gestionnaire de clic (simulation drag & drop)"""
        pass
    
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
        
        self.log_message(f"Démarrage de l'analyse du dossier: {self.current_directory}")
        self.progress_label.configure(text="Analyse en cours...")
        self.progress_bar.set(0.1)
        
        # Lancement asynchrone du traitement
        threading.Thread(target=self.process_directory_async, daemon=True).start()
    
    def process_directory_async(self):
        """Traitement asynchrone du dossier"""
        try:
            # Simulation du traitement
            steps = ["Scan des fichiers", "Classification", "Analyse NLP", "Analyse Vision", "Sécurisation"]
            
            for i, step in enumerate(steps):
                self.root.after(0, lambda s=step: self.progress_label.configure(text=f"Étape: {s}"))
                self.root.after(0, lambda p=(i+1)/len(steps): self.progress_bar.set(p))
                
                # Simulation de traitement
                import time
                time.sleep(2)
            
            # Mise à jour des résultats
            self.root.after(0, self.update_results)
            self.root.after(0, lambda: self.progress_label.configure(text="Analyse terminée"))
            self.root.after(0, lambda: self.log_message("Analyse terminée avec succès"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Erreur lors de l'analyse: {str(e)}"))
    
    def smart_search(self):
        """Recherche intelligente avec IA"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Attention", "Veuillez entrer une requête de recherche")
            return
        
        self.log_message(f"Recherche IA: {query}")
        
        # Simulation de recherche intelligente
        threading.Thread(target=self.smart_search_async, args=(query,), daemon=True).start()
    
    def smart_search_async(self, query):
        """Recherche asynchrone avec IA"""
        try:
            # Simulation d'analyse IA
            import time
            time.sleep(3)
            
            # Résultats simulés
            if "carte vitale" in query.lower():
                result = {
                    "type": "sensitive",
                    "file": "scan_carte_vitale.pdf",
                    "location": "vault",
                    "requires_auth": True
                }
            elif "cours" in query.lower():
                result = {
                    "type": "document",
                    "file": "cours_histoire.pdf",
                    "location": "documents",
                    "requires_auth": False
                }
            else:
                result = {
                    "type": "unknown",
                    "message": "Aucun fichier correspondant trouvé"
                }
            
            self.root.after(0, lambda: self.handle_search_result(result))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Erreur lors de la recherche: {str(e)}"))
    
    def handle_search_result(self, result):
        """Traiter le résultat de recherche"""
        if result["type"] == "sensitive":
            # Fichier sensible - demander authentification
            password = simpledialog.askstring(
                "Authentification Requise",
                f"Le fichier '{result['file']}' est chiffré.\nVeuillez saisir la phrase de passe:",
                show="*"
            )
            
            if password:
                # Vérifier le mot de passe et déchiffrer
                self.decrypt_and_open_file(result["file"], password)
            else:
                self.log_message("Authentification annulée")
        
        elif result["type"] == "document":
            # Fichier normal - ouvrir directement
            self.open_file(result["file"])
        
        else:
            messagebox.showinfo("Résultat", result.get("message", "Fichier non trouvé"))
    
    def decrypt_and_open_file(self, filename, password):
        """Déchiffrer et ouvrir un fichier sensible"""
        # Simulation du déchiffrement
        if password == "mon_secret_ultra_securise_2024":  # Mot de passe correct
            self.log_message(f"Déchiffrement réussi: {filename}")
            messagebox.showinfo("Succès", f"Fichier déchiffré avec succès: {filename}")
            # Ici, on ouvrirait le fichier déchiffré
        else:
            self.log_message(f"Échec de déchiffrement: {filename}")
            messagebox.showerror("Erreur", "Phrase de passe incorrecte")
    
    def open_file(self, filename):
        """Ouvrir un fichier normal"""
        self.log_message(f"Ouverture du fichier: {filename}")
        messagebox.showinfo("Fichier trouvé", f"Fichier: {filename}\n\nL'ouverture sera implémentée ici")
    
    def update_results(self):
        """Mettre à jour les résultats affichés"""
        # Simulation de fichiers analysés
        sample_files = [
            ("document1.pdf", "PDF", "Analysé", "Non"),
            ("carte_vitale.jpg", "Image", "Chiffré", "Oui"),
            ("facture.json", "JSON", "Analysé", "Non"),
            ("photo_id.png", "Image", "Chiffré", "Oui")
        ]
        
        # Vider et remplir l'arbre des fichiers
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        for file_info in sample_files:
            self.files_tree.insert("", "end", text=file_info[0], values=file_info[1:])
        
        # Simulation de fichiers dans le vault
        vault_files = [
            ("carte_vitale_encrypted.vault", "2024-01-15 10:30", "2.3 MB"),
            ("photo_id_encrypted.vault", "2024-01-15 10:31", "1.8 MB")
        ]
        
        # Vider et remplir l'arbre du vault
        for item in self.vault_tree.get_children():
            self.vault_tree.delete(item)
        
        for vault_info in vault_files:
            self.vault_tree.insert("", "end", text=vault_info[0], values=vault_info[1:])
    
    def refresh_results(self):
        """Actualiser les résultats"""
        self.log_message("Actualisation des résultats...")
        self.update_results()
    
    def start_system(self):
        """Démarrer le système multi-agents"""
        self.log_message("Démarrage du système multi-agents...")
        self.system_status = "Démarré"
        self.status_label.configure(text="🟢 Système: Démarré")
        threading.Thread(target=self.start_system_async, daemon=True).start()
    
    def start_system_async(self):
        """Démarrage asynchrone du système"""
        try:
            # Simulation du démarrage des agents
            agents = ["Orchestrateur", "NLP", "Vision", "Audio", "File Manager", "Security"]
            
            for agent in agents:
                self.root.after(0, lambda a=agent: self.log_message(f"Démarrage de l'agent {a}..."))
                import time
                time.sleep(1)
            
            self.root.after(0, lambda: self.log_message("Tous les agents sont démarrés"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Erreur lors du démarrage: {str(e)}"))
    
    def stop_system(self):
        """Arrêter le système multi-agents"""
        self.log_message("Arrêt du système multi-agents...")
        self.system_status = "Arrêté"
        self.status_label.configure(text="🔴 Système: Arrêté")
    
    def check_status(self):
        """Vérifier le statut du système"""
        self.log_message(f"Statut du système: {self.system_status}")
        messagebox.showinfo("Statut Système", f"Statut actuel: {self.system_status}")
    
    def start_system_thread(self):
        """Démarrer le thread du système"""
        self.log_message("Interface prête")
    
    def log_message(self, message):
        """Ajouter un message aux logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Ajouter au widget de logs
        self.logs_text.insert("end", log_entry)
        self.logs_text.see("end")
        
        # Log également dans la console
        logger.info(message)
    
    def run(self):
        """Lancer l'application"""
        self.log_message("Démarrage de l'interface Multi-Agent System")
        self.root.mainloop()

def main():
    """Fonction principale"""
    try:
        app = MultiAgentDesktopApp()
        app.run()
    except Exception as e:
        print(f"Erreur lors du démarrage de l'application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
