#!/usr/bin/env python3
"""
Interface desktop simplifiée avec tkinter standard
Compatible avec toutes les installations Python Windows
"""
import os
import sys
import json
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog

def check_mcp_system():
    """Vérifier si le système MCP est disponible"""
    try:
        from simple_mcp_system import MCPSystem
        return True
    except ImportError:
        return False

class SimpleDesktopApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Système Multi-Agent - KACM Qualcomm")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Configuration du style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#2b2b2b', foreground='white')
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#2b2b2b', foreground='white')
        self.style.configure('Custom.TFrame', background='#2b2b2b')
        
        # Variables
        self.current_directory = tk.StringVar()
        self.search_query = tk.StringVar()
        self.mcp_system = None
        
        # Initialiser le système MCP
        self.init_mcp_system()
        
        # Créer l'interface
        self.create_widgets()
        
    def init_mcp_system(self):
        """Initialiser le système MCP"""
        try:
            if check_mcp_system():
                from simple_mcp_system import MCPSystem
                
                config = {
                    "vault_password": "mon_secret_ultra_securise_2024",
                    "encryption_key": "ma_cle_de_chiffrement_ultra_securisee_2024"
                }
                
                self.mcp_system = MCPSystem(config)
                self.mcp_system.start()
                print("✅ Système MCP initialisé")
            else:
                print("❌ Système MCP non disponible")
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation MCP: {e}")
            
    def create_widgets(self):
        """Créer l'interface utilisateur"""
        # Titre principal
        title_frame = ttk.Frame(self.root, style='Custom.TFrame')
        title_frame.pack(fill='x', pady=10)
        
        title_label = ttk.Label(
            title_frame,
            text="🤖 Système Multi-Agent - KACM Qualcomm",
            style='Title.TLabel'
        )
        title_label.pack()
        
        # Frame principal avec scrollbar
        main_frame = ttk.Frame(self.root, style='Custom.TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sélection du dossier
        folder_frame = ttk.LabelFrame(main_frame, text="📁 Dossier à analyser", style='Custom.TFrame')
        folder_frame.pack(fill='x', pady=10)
        
        folder_input_frame = ttk.Frame(folder_frame, style='Custom.TFrame')
        folder_input_frame.pack(fill='x', padx=10, pady=10)
        
        self.folder_entry = ttk.Entry(folder_input_frame, textvariable=self.current_directory, width=50)
        self.folder_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        browse_button = ttk.Button(folder_input_frame, text="Parcourir", command=self.browse_folder)
        browse_button.pack(side='right', padx=5)
        
        analyze_button = ttk.Button(folder_frame, text="🚀 Analyser le Dossier", command=self.analyze_folder)
        analyze_button.pack(pady=10)
        
        # Recherche intelligente
        search_frame = ttk.LabelFrame(main_frame, text="🔍 Recherche intelligente", style='Custom.TFrame')
        search_frame.pack(fill='x', pady=10)
        
        search_input_frame = ttk.Frame(search_frame, style='Custom.TFrame')
        search_input_frame.pack(fill='x', padx=10, pady=10)
        
        self.search_entry = ttk.Entry(search_input_frame, textvariable=self.search_query, width=50)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        search_button = ttk.Button(search_input_frame, text="🤖 Rechercher", command=self.smart_search)
        search_button.pack(side='right', padx=5)
        
        # Exemples de recherche
        examples_frame = ttk.Frame(search_frame, style='Custom.TFrame')
        examples_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(examples_frame, text="Exemples:", style='Header.TLabel').pack(anchor='w')
        
        examples = [
            "trouve moi le scan de ma carte vitale",
            "donne moi le pdf de cours d'histoire",
            "où est ma photo d'identité",
            "liste les factures"
        ]
        
        for example in examples:
            example_btn = ttk.Button(examples_frame, text=f"'{example}'", 
                                   command=lambda e=example: self.search_query.set(e))
            example_btn.pack(side='left', padx=5, pady=2)
        
        # Zone de résultats avec onglets
        results_frame = ttk.LabelFrame(main_frame, text="📊 Résultats", style='Custom.TFrame')
        results_frame.pack(fill='both', expand=True, pady=10)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Onglet analyse
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="📄 Fichiers Analysés")
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, wrap=tk.WORD, height=15)
        self.analysis_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Onglet recherche
        search_results_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_results_frame, text="🔍 Résultats de Recherche")
        
        self.results_text = scrolledtext.ScrolledText(search_results_frame, wrap=tk.WORD, height=15)
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Onglet logs
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📋 Logs Système")
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD, height=15)
        self.logs_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Barre de statut
        status_frame = ttk.Frame(self.root, style='Custom.TFrame')
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="🟢 Système prêt", style='Header.TLabel')
        self.status_label.pack(side='left')
        
        # Bouton d'aide
        help_button = ttk.Button(status_frame, text="❓ Aide", command=self.show_help)
        help_button.pack(side='right')
        
        # Initialiser avec le dossier demo
        self.current_directory.set("demo_files")
        
        # Ajouter un message de bienvenue
        welcome_msg = """🎉 Bienvenue dans le Système Multi-Agent KACM Qualcomm!

🚀 Pour commencer:
1. Sélectionnez un dossier ou utilisez 'demo_files' par défaut
2. Cliquez sur 'Analyser le Dossier' pour analyser tous les fichiers
3. Utilisez la recherche intelligente pour trouver des fichiers spécifiques

🔐 Mot de passe du vault: mon_secret_ultra_securise_2024

💡 Astuce: Essayez les exemples de recherche pour découvrir les fonctionnalités!
"""
        self.logs_text.insert('1.0', welcome_msg)
        
    def browse_folder(self):
        """Sélectionner un dossier"""
        folder = filedialog.askdirectory(title="Sélectionner le dossier à analyser")
        if folder:
            self.current_directory.set(folder)
            self.log_message(f"📁 Dossier sélectionné: {folder}")
            
    def analyze_folder(self):
        """Analyser le dossier sélectionné"""
        directory = self.current_directory.get()
        if not directory:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier")
            return
        
        if not os.path.exists(directory):
            messagebox.showerror("Erreur", f"Le dossier {directory} n'existe pas")
            return
        
        # Effacer les résultats précédents
        self.analysis_text.delete('1.0', tk.END)
        self.status_label.config(text="⏳ Analyse en cours...")
        
        # Passer à l'onglet analyse
        self.notebook.select(0)
        
        def analyze_thread():
            try:
                self.analysis_text.insert(tk.END, f"🔍 Analyse du dossier: {directory}\n\n")
                
                if self.mcp_system:
                    # Utiliser le système MCP
                    result = self.mcp_system.call_tool("Orchestrator", "process_directory", {"directory": directory})
                    
                    if result.get("success"):
                        files_processed = result.get("files_processed", 0)
                        sensitive_files = result.get("sensitive_files", 0)
                        processing_time = result.get("processing_time", 0)
                        
                        analysis_text = f"""✅ Analyse terminée!
                        
📊 Statistiques:
• Fichiers traités: {files_processed}
• Fichiers sensibles: {sensitive_files}
• Temps de traitement: {processing_time:.2f}s

🔒 Sécurité:
Les fichiers contenant des données sensibles ont été automatiquement chiffrés dans le vault.

📁 Détails des fichiers:
"""
                        
                        self.analysis_text.insert(tk.END, analysis_text)
                        
                        # Ajouter les détails des fichiers
                        for file_info in result.get("files", []):
                            file_line = f"• {file_info['name']}\n"
                            file_line += f"  - Type: {file_info['type']}\n"
                            file_line += f"  - Statut: {'🔒 Chiffré (sensible)' if file_info['sensitive'] else '📄 Public'}\n"
                            if file_info.get('summary'):
                                file_line += f"  - Résumé: {file_info['summary']}\n"
                            file_line += "\n"
                            self.analysis_text.insert(tk.END, file_line)
                        
                        self.status_label.config(text="✅ Analyse terminée")
                        self.log_message(f"✅ Analyse terminée: {files_processed} fichiers traités")
                        
                    else:
                        error_msg = result.get("error", "Erreur inconnue")
                        self.analysis_text.insert(tk.END, f"❌ Erreur lors de l'analyse: {error_msg}")
                        self.status_label.config(text="❌ Erreur lors de l'analyse")
                        self.log_message(f"❌ Erreur: {error_msg}")
                else:
                    # Mode simulation sans MCP
                    self.analysis_text.insert(tk.END, "⚠️ Mode simulation (MCP non disponible)\n")
                    self.analysis_text.insert(tk.END, "Analyse simulée des fichiers...\n\n")
                    
                    # Simuler l'analyse
                    files = list(Path(directory).glob("*"))
                    for file_path in files:
                        if file_path.is_file():
                            self.analysis_text.insert(tk.END, f"• {file_path.name} - Analysé\n")
                    
                    self.status_label.config(text="✅ Analyse simulée terminée")
                    
            except Exception as e:
                error_msg = f"❌ Erreur lors de l'analyse: {str(e)}"
                self.analysis_text.insert(tk.END, error_msg)
                self.status_label.config(text="❌ Erreur")
                self.log_message(error_msg)
                
        # Lancer l'analyse dans un thread séparé
        threading.Thread(target=analyze_thread, daemon=True).start()
        
    def smart_search(self):
        """Recherche intelligente"""
        query = self.search_query.get().strip()
        if not query:
            messagebox.showerror("Erreur", "Veuillez saisir une requête")
            return
        
        # Effacer les résultats précédents
        self.results_text.delete('1.0', tk.END)
        self.status_label.config(text="🔍 Recherche en cours...")
        
        # Passer à l'onglet recherche
        self.notebook.select(1)
        
        def search_thread():
            try:
                self.results_text.insert(tk.END, f"🔍 Recherche: {query}\n\n")
                
                if self.mcp_system:
                    # Utiliser le système MCP
                    result = self.mcp_system.call_tool("Orchestrator", "smart_search", {"query": query})
                    
                    if result.get("success"):
                        results = result.get("results", [])
                        
                        if results:
                            search_text = f"🎯 {len(results)} résultat(s) trouvé(s):\n\n"
                            self.results_text.insert(tk.END, search_text)
                            
                            for i, file_result in enumerate(results, 1):
                                is_encrypted = file_result.get("encrypted", False)
                                confidence = file_result.get("confidence", 0)
                                
                                result_text = f"{i}. {file_result['name']}\n"
                                result_text += f"   📊 Pertinence: {confidence:.1f}%\n"
                                result_text += f"   🔒 Statut: {'Chiffré' if is_encrypted else 'Public'}\n"
                                result_text += f"   📄 Résumé: {file_result.get('summary', 'N/A')}\n\n"
                                
                                self.results_text.insert(tk.END, result_text)
                                
                                # Si le fichier est chiffré, proposer le déchiffrement
                                if is_encrypted:
                                    self.results_text.insert(tk.END, f"   🔐 Authentification requise\n")
                                    
                                    # Créer un bouton pour déchiffrer
                                    decrypt_btn = ttk.Button(
                                        self.results_text.master,
                                        text=f"🔓 Déchiffrer {file_result['name']}",
                                        command=lambda fr=file_result: self.decrypt_file(fr)
                                    )
                                    
                                    # Insérer le bouton dans le texte
                                    self.results_text.insert(tk.END, "\n")
                                    self.results_text.window_create(tk.END, window=decrypt_btn)
                                    self.results_text.insert(tk.END, "\n\n")
                            
                            self.status_label.config(text="✅ Recherche terminée")
                            self.log_message(f"✅ Recherche terminée: {len(results)} résultat(s)")
                            
                        else:
                            self.results_text.insert(tk.END, "❌ Aucun résultat trouvé")
                            self.status_label.config(text="❌ Aucun résultat")
                            self.log_message("❌ Aucun résultat trouvé")
                    
                    else:
                        error_msg = result.get("error", "Erreur inconnue")
                        self.results_text.insert(tk.END, f"❌ Erreur lors de la recherche: {error_msg}")
                        self.status_label.config(text="❌ Erreur")
                        self.log_message(f"❌ Erreur de recherche: {error_msg}")
                else:
                    # Mode simulation
                    self.results_text.insert(tk.END, "⚠️ Mode simulation (MCP non disponible)\n")
                    self.results_text.insert(tk.END, f"Recherche simulée pour: {query}\n\n")
                    
                    # Recherche simulée basique
                    if "carte vitale" in query.lower():
                        self.results_text.insert(tk.END, "🎯 Résultat trouvé:\n")
                        self.results_text.insert(tk.END, "• carte_vitale_scan.jpg (🔒 Chiffré)\n")
                        self.results_text.insert(tk.END, "  Fichier sensible contenant des données personnelles\n")
                    elif "histoire" in query.lower():
                        self.results_text.insert(tk.END, "🎯 Résultat trouvé:\n")
                        self.results_text.insert(tk.END, "• cours_histoire.pdf (📄 Public)\n")
                        self.results_text.insert(tk.END, "  Document éducatif accessible\n")
                    else:
                        self.results_text.insert(tk.END, "❌ Aucun résultat trouvé (mode simulation)")
                    
                    self.status_label.config(text="✅ Recherche simulée terminée")
                    
            except Exception as e:
                error_msg = f"❌ Erreur lors de la recherche: {str(e)}"
                self.results_text.insert(tk.END, error_msg)
                self.status_label.config(text="❌ Erreur")
                self.log_message(error_msg)
                
        # Lancer la recherche dans un thread séparé
        threading.Thread(target=search_thread, daemon=True).start()
        
    def decrypt_file(self, file_result):
        """Déchiffrer un fichier"""
        # Demander le mot de passe
        password = simpledialog.askstring(
            "Authentification",
            f"🔐 Fichier: {file_result['name']}\n\nVeuillez saisir le mot de passe:",
            show='*'
        )
        
        if not password:
            return
        
        try:
            if self.mcp_system:
                decrypt_result = self.mcp_system.call_tool("Security", "decrypt_file", {
                    "file_id": file_result['id'],
                    "password": password
                })
                
                if decrypt_result.get("success"):
                    messagebox.showinfo("Succès", f"✅ Fichier déchiffré avec succès!\n\nEmplacement: {decrypt_result.get('decrypted_path', 'N/A')}")
                    self.log_message(f"✅ Fichier déchiffré: {file_result['name']}")
                else:
                    messagebox.showerror("Erreur", "❌ Mot de passe incorrect")
                    self.log_message("❌ Échec du déchiffrement: mot de passe incorrect")
            else:
                messagebox.showinfo("Simulation", "⚠️ Mode simulation - Déchiffrement simulé")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Erreur lors du déchiffrement: {str(e)}")
            self.log_message(f"❌ Erreur de déchiffrement: {str(e)}")
            
    def show_help(self):
        """Afficher l'aide"""
        help_text = """🆘 Aide - Système Multi-Agent KACM Qualcomm

🚀 Démarrage:
1. Sélectionnez un dossier avec 'Parcourir' ou utilisez 'demo_files'
2. Cliquez sur 'Analyser le Dossier' pour démarrer l'analyse
3. Utilisez la recherche intelligente pour trouver des fichiers

🔍 Recherche Intelligente:
• Tapez votre requête en langage naturel
• Exemples: "trouve ma carte vitale", "donne moi les factures"
• Les fichiers sensibles nécessitent une authentification

🔐 Sécurité:
• Mot de passe du vault: mon_secret_ultra_securise_2024
• Les fichiers sensibles sont automatiquement chiffrés
• Authentification requise pour accéder aux fichiers chiffrés

📊 Onglets:
• Fichiers Analysés: Résultats de l'analyse du dossier
• Résultats de Recherche: Résultats de la recherche intelligente
• Logs Système: Historique des actions

🎯 Fonctionnalités:
• Analyse automatique multi-format (texte, image, audio)
• Détection PII et chiffrement automatique
• Recherche sémantique intelligente
• Interface desktop intuitive

❓ Support:
Pour plus d'informations, consultez README_FINAL.md
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Aide")
        help_window.geometry("600x500")
        help_window.configure(bg='#2b2b2b')
        
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        help_text_widget.insert('1.0', help_text)
        help_text_widget.config(state='disabled')
        
    def log_message(self, message):
        """Ajouter un message aux logs"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.logs_text.insert(tk.END, log_entry)
        self.logs_text.see(tk.END)
        
    def on_closing(self):
        """Gérer la fermeture de l'application"""
        if self.mcp_system:
            self.mcp_system.stop()
            self.log_message("🔴 Système MCP arrêté")
        self.root.destroy()
        
    def run(self):
        """Lancer l'application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Fonction principale"""
    print("🚀 Démarrage de l'interface desktop simplifiée...")
    
    # Vérifier tkinter
    try:
        import tkinter as tk
        from tkinter import simpledialog
        print("✅ tkinter disponible")
    except ImportError:
        print("❌ tkinter non disponible")
        print("Utilisez 'python demo_console.py' pour la démonstration console")
        return False
    
    try:
        # Créer et lancer l'application
        app = SimpleDesktopApp()
        app.run()
        print("✅ Application fermée normalement")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
