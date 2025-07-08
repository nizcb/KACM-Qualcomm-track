#!/usr/bin/env python3
"""
Lanceur de démonstration pour Windows
Interface desktop intégrée avec le système multi-agent
"""
import os
import sys
import json
import threading
import time
from pathlib import Path

def check_dependencies():
    """Vérifier les dépendances"""
    missing = []
    
    try:
        import tkinter as tk
        import customtkinter as ctk
    except ImportError as e:
        missing.append("tkinter/customtkinter")
    
    try:
        import fastapi
        import uvicorn
    except ImportError:
        missing.append("fastapi/uvicorn")
    
    try:
        from simple_mcp_system import MCPSystem
    except ImportError:
        missing.append("simple_mcp_system")
    
    return missing

def start_mcp_system():
    """Démarrer le système MCP"""
    print("🚀 Démarrage du système MCP...")
    try:
        from simple_mcp_system import MCPSystem
        
        # Configuration
        config = {
            "vault_password": "mon_secret_ultra_securise_2024",
            "encryption_key": "ma_cle_de_chiffrement_ultra_securisee_2024"
        }
        
        # Démarrer le système
        system = MCPSystem(config)
        system.start()
        
        print("✅ Système MCP démarré")
        return system
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage MCP: {e}")
        return None

def start_desktop_app(mcp_system):
    """Démarrer l'application desktop"""
    print("🖥️ Démarrage de l'interface desktop...")
    
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
        import customtkinter as ctk
        
        # Configuration CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        class MultiAgentDesktopApp:
            def __init__(self, mcp_system):
                self.mcp_system = mcp_system
                self.root = ctk.CTk()
                self.root.title("🤖 Système Multi-Agent - KACM Qualcomm")
                self.root.geometry("1200x800")
                
                # Variables
                self.current_directory = tk.StringVar()
                self.search_query = tk.StringVar()
                self.search_results = []
                self.analysis_results = []
                
                self.create_widgets()
                
            def create_widgets(self):
                """Créer l'interface"""
                # Titre principal
                title_label = ctk.CTkLabel(
                    self.root, 
                    text="🤖 Système Multi-Agent - KACM Qualcomm",
                    font=ctk.CTkFont(size=24, weight="bold")
                )
                title_label.pack(pady=20)
                
                # Frame principale
                main_frame = ctk.CTkFrame(self.root)
                main_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Sélection du dossier
                folder_frame = ctk.CTkFrame(main_frame)
                folder_frame.pack(fill="x", padx=10, pady=10)
                
                ctk.CTkLabel(folder_frame, text="📁 Dossier à analyser:", font=ctk.CTkFont(size=16)).pack(anchor="w", padx=10, pady=5)
                
                folder_selection_frame = ctk.CTkFrame(folder_frame)
                folder_selection_frame.pack(fill="x", padx=10, pady=5)
                
                self.folder_entry = ctk.CTkEntry(folder_selection_frame, textvariable=self.current_directory, width=400)
                self.folder_entry.pack(side="left", fill="x", expand=True, padx=5)
                
                browse_button = ctk.CTkButton(folder_selection_frame, text="Parcourir", command=self.browse_folder)
                browse_button.pack(side="right", padx=5)
                
                analyze_button = ctk.CTkButton(folder_frame, text="🚀 Analyser le Dossier", command=self.analyze_folder)
                analyze_button.pack(pady=10)
                
                # Recherche intelligente
                search_frame = ctk.CTkFrame(main_frame)
                search_frame.pack(fill="x", padx=10, pady=10)
                
                ctk.CTkLabel(search_frame, text="🔍 Recherche intelligente:", font=ctk.CTkFont(size=16)).pack(anchor="w", padx=10, pady=5)
                
                search_input_frame = ctk.CTkFrame(search_frame)
                search_input_frame.pack(fill="x", padx=10, pady=5)
                
                self.search_entry = ctk.CTkEntry(search_input_frame, textvariable=self.search_query, width=400, placeholder_text="Ex: 'trouve moi le scan de ma carte vitale'")
                self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
                
                search_button = ctk.CTkButton(search_input_frame, text="🤖 Rechercher avec IA", command=self.smart_search)
                search_button.pack(side="right", padx=5)
                
                # Résultats
                results_frame = ctk.CTkFrame(main_frame)
                results_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Onglets
                self.tabview = ctk.CTkTabview(results_frame)
                self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Onglet analyse
                self.tabview.add("Fichiers Analysés")
                self.analysis_text = ctk.CTkTextbox(self.tabview.tab("Fichiers Analysés"), width=400, height=200)
                self.analysis_text.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Onglet recherche
                self.tabview.add("Résultats de Recherche")
                self.results_text = ctk.CTkTextbox(self.tabview.tab("Résultats de Recherche"), width=400, height=200)
                self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Onglet logs
                self.tabview.add("Logs Système")
                self.logs_text = ctk.CTkTextbox(self.tabview.tab("Logs Système"), width=400, height=200)
                self.logs_text.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Statut
                self.status_label = ctk.CTkLabel(main_frame, text="🟢 Système prêt", font=ctk.CTkFont(size=14))
                self.status_label.pack(pady=10)
                
                # Initialiser avec le dossier demo
                self.current_directory.set("demo_files")
                
            def browse_folder(self):
                """Sélectionner un dossier"""
                folder = filedialog.askdirectory(title="Sélectionner le dossier à analyser")
                if folder:
                    self.current_directory.set(folder)
                    
            def analyze_folder(self):
                """Analyser le dossier sélectionné"""
                directory = self.current_directory.get()
                if not directory:
                    messagebox.showerror("Erreur", "Veuillez sélectionner un dossier")
                    return
                
                if not os.path.exists(directory):
                    messagebox.showerror("Erreur", f"Le dossier {directory} n'existe pas")
                    return
                
                try:
                    self.status_label.configure(text="⏳ Analyse en cours...")
                    self.analysis_text.delete("1.0", "end")
                    self.analysis_text.insert("1.0", f"🔍 Analyse du dossier: {directory}\n\n")
                    
                    # Utiliser le système MCP pour l'analyse
                    if self.mcp_system:
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

🔒 Fichiers sécurisés:
Les fichiers contenant des données sensibles ont été automatiquement chiffrés dans le vault.

📁 Fichiers analysés:
"""
                            
                            # Ajouter les détails des fichiers
                            for file_info in result.get("files", []):
                                analysis_text += f"• {file_info['name']} - {file_info['type']} - {'🔒 Chiffré' if file_info['sensitive'] else '📄 Public'}\n"
                            
                            self.analysis_text.insert("end", analysis_text)
                            self.status_label.configure(text="✅ Analyse terminée")
                            
                        else:
                            error_msg = result.get("error", "Erreur inconnue")
                            self.analysis_text.insert("end", f"❌ Erreur lors de l'analyse: {error_msg}")
                            self.status_label.configure(text="❌ Erreur lors de l'analyse")
                    
                except Exception as e:
                    error_msg = f"❌ Erreur lors de l'analyse: {str(e)}"
                    self.analysis_text.insert("end", error_msg)
                    self.status_label.configure(text="❌ Erreur")
                    messagebox.showerror("Erreur", error_msg)
                    
            def smart_search(self):
                """Recherche intelligente"""
                query = self.search_query.get().strip()
                if not query:
                    messagebox.showerror("Erreur", "Veuillez saisir une requête")
                    return
                
                try:
                    self.status_label.configure(text="🔍 Recherche en cours...")
                    self.results_text.delete("1.0", "end")
                    self.results_text.insert("1.0", f"🔍 Recherche: {query}\n\n")
                    
                    # Utiliser le système MCP pour la recherche
                    if self.mcp_system:
                        result = self.mcp_system.call_tool("Orchestrator", "smart_search", {"query": query})
                        
                        if result.get("success"):
                            results = result.get("results", [])
                            
                            if results:
                                search_text = f"🎯 {len(results)} résultat(s) trouvé(s):\n\n"
                                
                                for i, file_result in enumerate(results, 1):
                                    is_encrypted = file_result.get("encrypted", False)
                                    confidence = file_result.get("confidence", 0)
                                    
                                    search_text += f"{i}. {file_result['name']}\n"
                                    search_text += f"   📊 Pertinence: {confidence:.1f}%\n"
                                    search_text += f"   🔒 Statut: {'Chiffré' if is_encrypted else 'Public'}\n"
                                    search_text += f"   📄 Résumé: {file_result.get('summary', 'N/A')}\n\n"
                                    
                                    # Si le fichier est chiffré, demander le mot de passe
                                    if is_encrypted:
                                        search_text += f"   🔐 Authentification requise pour accéder au fichier\n\n"
                                        
                                        # Demander le mot de passe
                                        password = self.prompt_for_password(file_result['name'])
                                        if password:
                                            decrypt_result = self.mcp_system.call_tool("Security", "decrypt_file", {
                                                "file_id": file_result['id'],
                                                "password": password
                                            })
                                            
                                            if decrypt_result.get("success"):
                                                search_text += f"   ✅ Fichier déchiffré avec succès!\n"
                                                search_text += f"   📁 Emplacement: {decrypt_result.get('decrypted_path', 'N/A')}\n\n"
                                            else:
                                                search_text += f"   ❌ Mot de passe incorrect\n\n"
                                
                                self.results_text.insert("end", search_text)
                                self.status_label.configure(text="✅ Recherche terminée")
                                
                            else:
                                self.results_text.insert("end", "❌ Aucun résultat trouvé")
                                self.status_label.configure(text="❌ Aucun résultat")
                        
                        else:
                            error_msg = result.get("error", "Erreur inconnue")
                            self.results_text.insert("end", f"❌ Erreur lors de la recherche: {error_msg}")
                            self.status_label.configure(text="❌ Erreur lors de la recherche")
                    
                except Exception as e:
                    error_msg = f"❌ Erreur lors de la recherche: {str(e)}"
                    self.results_text.insert("end", error_msg)
                    self.status_label.configure(text="❌ Erreur")
                    messagebox.showerror("Erreur", error_msg)
                    
            def prompt_for_password(self, filename):
                """Demander le mot de passe pour un fichier chiffré"""
                dialog = ctk.CTkInputDialog(
                    text=f"🔐 Authentification requise\n\nFichier: {filename}\nVeuillez saisir le mot de passe:",
                    title="Authentification"
                )
                return dialog.get_input()
                
            def run(self):
                """Lancer l'application"""
                self.root.mainloop()
        
        # Créer et lancer l'application
        app = MultiAgentDesktopApp(mcp_system)
        app.run()
        
    except ImportError as e:
        print(f"❌ Dépendances manquantes pour l'interface desktop: {e}")
        print("Utilisez 'python demo_console.py' pour la démonstration console")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du démarrage desktop: {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🚀 DÉMONSTRATION SYSTÈME MULTI-AGENT - WINDOWS")
    print("=" * 60)
    
    # Vérifier les dépendances
    missing = check_dependencies()
    if missing:
        print(f"❌ Dépendances manquantes: {', '.join(missing)}")
        print("Exécutez 'python setup_windows.py' pour installer les dépendances")
        return False
    
    # Démarrer le système MCP
    mcp_system = start_mcp_system()
    if not mcp_system:
        print("❌ Impossible de démarrer le système MCP")
        return False
    
    try:
        # Démarrer l'interface desktop
        if start_desktop_app(mcp_system):
            print("✅ Démonstration terminée avec succès")
        else:
            print("❌ Problème avec l'interface desktop")
            print("Utilisation de la démonstration console...")
            
            # Fallback vers la console
            os.system("python demo_console.py")
            
    except KeyboardInterrupt:
        print("\n🔴 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
    finally:
        # Arrêter le système MCP
        if mcp_system:
            mcp_system.stop()
            print("🔴 Système MCP arrêté")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
