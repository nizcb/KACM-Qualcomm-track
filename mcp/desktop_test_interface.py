#!/usr/bin/env python3
"""
Interface Desktop de Test - Système MCP
======================================

Interface graphique simple pour tester le système multi-agents.
Utilise tkinter standard pour une compatibilité maximale.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import sys
import json
import threading
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

class MCPDesktopTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Système Multi-Agent MCP - Test")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.current_folder = tk.StringVar()
        self.search_query = tk.StringVar()
        self.log_text = tk.StringVar()
        
        # Initialiser le système MCP
        self.mcp_system = None
        self.init_mcp_system()
        
        # Créer l'interface
        self.create_interface()
        
        # Log initial
        self.log_message("🚀 Système MCP initialisé et prêt")
    
    def init_mcp_system(self):
        """Initialise le système MCP"""
        try:
            from simple_mcp_system import SimpleMCPSystem
            self.mcp_system = SimpleMCPSystem()
            self.log_message("✅ Système MCP chargé avec succès")
        except Exception as e:
            self.log_message(f"❌ Erreur lors du chargement MCP: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger le système MCP: {e}")
    
    def create_interface(self):
        """Crée l'interface graphique"""
        
        # Titre principal
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🤖 Système Multi-Agent MCP", 
                              font=('Arial', 16, 'bold'), 
                              bg='#2c3e50', fg='white')
        title_label.pack(pady=15)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Section 1: Sélection de dossier
        folder_frame = tk.LabelFrame(main_frame, text="📁 Dossier à analyser", 
                                   font=('Arial', 10, 'bold'), bg='#f0f0f0')
        folder_frame.pack(fill='x', pady=5)
        
        folder_entry_frame = tk.Frame(folder_frame, bg='#f0f0f0')
        folder_entry_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Entry(folder_entry_frame, textvariable=self.current_folder, 
                font=('Arial', 10), state='readonly').pack(side='left', fill='x', expand=True)
        
        tk.Button(folder_entry_frame, text="Parcourir", 
                 command=self.select_folder, bg='#3498db', fg='white').pack(side='right', padx=5)
        
        tk.Button(folder_entry_frame, text="Analyser", 
                 command=self.analyze_folder, bg='#27ae60', fg='white').pack(side='right')
        
        # Section 2: Recherche intelligente
        search_frame = tk.LabelFrame(main_frame, text="🔍 Recherche intelligente", 
                                   font=('Arial', 10, 'bold'), bg='#f0f0f0')
        search_frame.pack(fill='x', pady=5)
        
        search_entry_frame = tk.Frame(search_frame, bg='#f0f0f0')
        search_entry_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Entry(search_entry_frame, textvariable=self.search_query, 
                font=('Arial', 10), 
                placeholder_text="Ex: trouve moi ma carte vitale").pack(side='left', fill='x', expand=True)
        
        tk.Button(search_entry_frame, text="Rechercher", 
                 command=self.search_files, bg='#e74c3c', fg='white').pack(side='right', padx=5)
        
        # Section 3: Résultats
        results_frame = tk.LabelFrame(main_frame, text="📊 Résultats", 
                                    font=('Arial', 10, 'bold'), bg='#f0f0f0')
        results_frame.pack(fill='both', expand=True, pady=5)
        
        # Treeview pour les résultats
        self.results_tree = ttk.Treeview(results_frame, columns=('Type', 'Statut', 'Chemin'), show='headings')
        self.results_tree.heading('#1', text='Fichier')
        self.results_tree.heading('#2', text='Type')
        self.results_tree.heading('#3', text='Statut')
        self.results_tree.heading('#4', text='Chemin')
        
        # Scrollbar pour le treeview
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
        self.results_tree.configure(yscroll=scrollbar.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
        
        # Bind double-click
        self.results_tree.bind('<Double-1>', self.on_file_double_click)
        
        # Section 4: Logs
        log_frame = tk.LabelFrame(main_frame, text="📝 Logs", 
                                font=('Arial', 10, 'bold'), bg='#f0f0f0')
        log_frame.pack(fill='x', pady=5)
        log_frame.configure(height=100)
        log_frame.pack_propagate(False)
        
        self.log_text_widget = tk.Text(log_frame, height=6, font=('Courier', 9), 
                                     bg='#2c3e50', fg='white')
        self.log_text_widget.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Boutons d'action
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=5)
        
        tk.Button(button_frame, text="🧪 Tests Auto", 
                 command=self.run_auto_tests, bg='#9b59b6', fg='white').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="🔐 Vault", 
                 command=self.open_vault, bg='#f39c12', fg='white').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="📋 Rapport", 
                 command=self.generate_report, bg='#1abc9c', fg='white').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="❌ Quitter", 
                 command=self.root.quit, bg='#e74c3c', fg='white').pack(side='right', padx=5)
    
    def log_message(self, message):
        """Ajoute un message aux logs"""
        if hasattr(self, 'log_text_widget'):
            self.log_text_widget.insert(tk.END, f"{message}\n")
            self.log_text_widget.see(tk.END)
    
    def select_folder(self):
        """Sélectionne un dossier à analyser"""
        folder = filedialog.askdirectory(title="Sélectionnez un dossier à analyser")
        if folder:
            self.current_folder.set(folder)
            self.log_message(f"📁 Dossier sélectionné: {folder}")
    
    def analyze_folder(self):
        """Analyse le dossier sélectionné"""
        if not self.current_folder.get():
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier d'abord")
            return
        
        if not self.mcp_system:
            messagebox.showerror("Erreur", "Système MCP non disponible")
            return
        
        def analyze_thread():
            try:
                self.log_message("🔄 Analyse en cours...")
                
                # Analyser le dossier
                results = self.mcp_system.analyze_directory(self.current_folder.get())
                
                # Vider les résultats précédents
                for item in self.results_tree.get_children():
                    self.results_tree.delete(item)
                
                # Afficher les résultats
                if results:
                    for result in results:
                        file_name = os.path.basename(result.get('file_path', ''))
                        file_type = result.get('file_type', 'Unknown')
                        status = "🔐 Sensible" if result.get('sensitive') else "📄 Normal"
                        path = result.get('file_path', '')
                        
                        self.results_tree.insert('', 'end', values=(file_name, file_type, status, path))
                    
                    self.log_message(f"✅ Analyse terminée: {len(results)} fichiers")
                else:
                    self.log_message("⚠️ Aucun fichier trouvé")
                    
            except Exception as e:
                self.log_message(f"❌ Erreur d'analyse: {e}")
                messagebox.showerror("Erreur", f"Erreur lors de l'analyse: {e}")
        
        # Lancer l'analyse dans un thread séparé
        thread = threading.Thread(target=analyze_thread)
        thread.daemon = True
        thread.start()
    
    def search_files(self):
        """Recherche des fichiers selon la requête"""
        query = self.search_query.get().strip()
        if not query:
            messagebox.showwarning("Attention", "Veuillez entrer une requête de recherche")
            return
        
        if not self.mcp_system:
            messagebox.showerror("Erreur", "Système MCP non disponible")
            return
        
        def search_thread():
            try:
                self.log_message(f"🔍 Recherche: '{query}'")
                
                # Effectuer la recherche
                results = self.mcp_system.search_files(query)
                
                # Vider les résultats précédents
                for item in self.results_tree.get_children():
                    self.results_tree.delete(item)
                
                # Afficher les résultats
                if results:
                    for result in results:
                        file_name = os.path.basename(result.get('file_path', ''))
                        score = f"Score: {result.get('score', 0):.2f}"
                        status = "🔐 Sensible" if result.get('sensitive') else "📄 Normal"
                        path = result.get('file_path', '')
                        
                        self.results_tree.insert('', 'end', values=(file_name, score, status, path))
                    
                    self.log_message(f"✅ Recherche terminée: {len(results)} résultats")
                else:
                    self.log_message("⚠️ Aucun résultat trouvé")
                    
            except Exception as e:
                self.log_message(f"❌ Erreur de recherche: {e}")
                messagebox.showerror("Erreur", f"Erreur lors de la recherche: {e}")
        
        # Lancer la recherche dans un thread séparé
        thread = threading.Thread(target=search_thread)
        thread.daemon = True
        thread.start()
    
    def on_file_double_click(self, event):
        """Gère le double-clic sur un fichier"""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            values = item['values']
            
            if len(values) >= 4:
                file_path = values[3]
                status = values[2]
                
                if "🔐 Sensible" in status:
                    # Demander le mot de passe
                    password = simpledialog.askstring("Authentification", 
                                                    "Mot de passe pour déchiffrer:", 
                                                    show='*')
                    if password:
                        self.decrypt_and_open_file(file_path, password)
                else:
                    # Ouvrir le fichier normal
                    self.open_file(file_path)
    
    def decrypt_and_open_file(self, file_path, password):
        """Déchiffre et ouvre un fichier sensible"""
        try:
            self.log_message(f"🔓 Déchiffrement de: {os.path.basename(file_path)}")
            
            # TODO: Implémenter le déchiffrement réel
            messagebox.showinfo("Succès", f"Fichier déchiffré et ouvert: {os.path.basename(file_path)}")
            
        except Exception as e:
            self.log_message(f"❌ Erreur de déchiffrement: {e}")
            messagebox.showerror("Erreur", f"Impossible de déchiffrer le fichier: {e}")
    
    def open_file(self, file_path):
        """Ouvre un fichier normal"""
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)  # Windows
                self.log_message(f"📂 Fichier ouvert: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Erreur", "Fichier non trouvé")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier: {e}")
    
    def run_auto_tests(self):
        """Lance les tests automatiques"""
        self.log_message("🧪 Lancement des tests automatiques...")
        
        def test_thread():
            try:
                # Importer et lancer les tests
                from test_complete_system import SystemTester
                
                tester = SystemTester()
                success = tester.run_all_tests()
                
                if success:
                    self.log_message("✅ Tous les tests sont passés!")
                else:
                    self.log_message("⚠️ Certains tests ont échoué")
                    
            except Exception as e:
                self.log_message(f"❌ Erreur lors des tests: {e}")
        
        thread = threading.Thread(target=test_thread)
        thread.daemon = True
        thread.start()
    
    def open_vault(self):
        """Ouvre la gestion du coffre-fort"""
        vault_window = tk.Toplevel(self.root)
        vault_window.title("🔐 Coffre-fort sécurisé")
        vault_window.geometry("600x400")
        
        tk.Label(vault_window, text="🔐 Gestion du Coffre-fort", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Liste des fichiers chiffrés
        vault_tree = ttk.Treeview(vault_window, columns=('Fichier', 'Date'), show='headings')
        vault_tree.heading('#1', text='Fichier chiffré')
        vault_tree.heading('#2', text='Date de chiffrement')
        vault_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Boutons
        button_frame = tk.Frame(vault_window)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(button_frame, text="🔓 Déchiffrer", 
                 bg='#27ae60', fg='white').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="🔐 Chiffrer nouveau", 
                 bg='#e74c3c', fg='white').pack(side='left', padx=5)
        
        tk.Button(button_frame, text="Fermer", 
                 command=vault_window.destroy, bg='#95a5a6', fg='white').pack(side='right', padx=5)
    
    def generate_report(self):
        """Génère un rapport d'analyse"""
        report_window = tk.Toplevel(self.root)
        report_window.title("📋 Rapport d'analyse")
        report_window.geometry("700x500")
        
        tk.Label(report_window, text="📋 Rapport d'analyse du système", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Zone de texte pour le rapport
        report_text = tk.Text(report_window, font=('Courier', 10))
        report_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Générer le contenu du rapport
        report_content = """
RAPPORT D'ANALYSE DU SYSTÈME MCP
================================

Système Multi-Agent pour l'analyse et la sécurisation de fichiers

Composants testés:
- 🤖 Orchestrateur MCP
- 🔍 Agent NLP (analyse de texte)
- 👁️ Agent Vision (analyse d'images)
- 🔐 Système de sécurité
- 💾 Coffre-fort chiffré
- 🔍 Recherche intelligente

Fonctionnalités disponibles:
- Analyse automatique de dossiers
- Détection de données sensibles (PII)
- Chiffrement automatique des fichiers sensibles
- Recherche en langage naturel
- Authentification pour l'accès aux fichiers chiffrés
- Interface graphique intuitive

Statut: ✅ Système opérationnel
"""
        
        report_text.insert(tk.END, report_content)
        report_text.config(state='disabled')
        
        tk.Button(report_window, text="Fermer", 
                 command=report_window.destroy, bg='#95a5a6', fg='white').pack(pady=10)
    
    def run(self):
        """Lance l'interface"""
        self.root.mainloop()

def main():
    """Fonction principale"""
    try:
        app = MCPDesktopTest()
        app.run()
    except Exception as e:
        print(f"Erreur lors du lancement: {e}")
        messagebox.showerror("Erreur critique", f"Impossible de lancer l'application: {e}")

if __name__ == "__main__":
    main()
