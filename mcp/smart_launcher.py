#!/usr/bin/env python3
"""
Lanceur intelligent pour le système multi-agent
Détecte automatiquement l'environnement et choisit la meilleure interface
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def detect_environment():
    """Détecter l'environnement d'exécution"""
    env_info = {
        "os": platform.system(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "has_tkinter": False,
        "has_customtkinter": False,
        "has_fastapi": False,
        "has_mcp": False,
        "is_wsl": False
    }
    
    # Vérifier WSL
    if "microsoft" in platform.uname().release.lower():
        env_info["is_wsl"] = True
    
    # Vérifier tkinter
    try:
        import tkinter as tk
        env_info["has_tkinter"] = True
    except ImportError:
        pass
    
    # Vérifier customtkinter
    try:
        import customtkinter as ctk
        env_info["has_customtkinter"] = True
    except ImportError:
        pass
    
    # Vérifier FastAPI
    try:
        import fastapi
        import uvicorn
        env_info["has_fastapi"] = True
    except ImportError:
        pass
    
    # Vérifier le système MCP
    try:
        from simple_mcp_system import MCPSystem
        env_info["has_mcp"] = True
    except ImportError:
        pass
    
    return env_info

def print_environment_info(env_info):
    """Afficher les informations d'environnement"""
    print("=" * 60)
    print("🔍 DÉTECTION DE L'ENVIRONNEMENT")
    print("=" * 60)
    print(f"💻 OS: {env_info['os']}")
    print(f"🐍 Python: {env_info['python_version']}")
    print(f"🌐 WSL: {'Oui' if env_info['is_wsl'] else 'Non'}")
    print(f"🖥️ tkinter: {'✅' if env_info['has_tkinter'] else '❌'}")
    print(f"🎨 customtkinter: {'✅' if env_info['has_customtkinter'] else '❌'}")
    print(f"🌐 FastAPI: {'✅' if env_info['has_fastapi'] else '❌'}")
    print(f"🤖 MCP System: {'✅' if env_info['has_mcp'] else '❌'}")
    print()

def choose_interface(env_info):
    """Choisir la meilleure interface disponible"""
    if not env_info["has_mcp"]:
        print("❌ Système MCP non disponible")
        print("Exécutez 'python setup_windows.py' pour installer les dépendances")
        return None
    
    # Priorité 1: Interface desktop moderne (customtkinter)
    if env_info["has_customtkinter"] and env_info["has_tkinter"]:
        print("🎯 Interface recommandée: Desktop moderne (CustomTkinter)")
        return "desktop_modern"
    
    # Priorité 2: Interface desktop simple (tkinter standard)
    elif env_info["has_tkinter"]:
        print("🎯 Interface recommandée: Desktop simple (tkinter)")
        return "desktop_simple"
    
    # Priorité 3: Interface console
    else:
        print("🎯 Interface recommandée: Console")
        return "console"

def run_setup():
    """Exécuter le setup si nécessaire"""
    print("🔧 Exécution du setup...")
    try:
        result = subprocess.run([sys.executable, "setup_windows.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Setup terminé avec succès")
            return True
        else:
            print("❌ Problème lors du setup")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erreur lors du setup: {e}")
        return False

def launch_interface(interface_type):
    """Lancer l'interface sélectionnée"""
    print(f"🚀 Lancement de l'interface: {interface_type}")
    print("=" * 60)
    
    try:
        if interface_type == "desktop_modern":
            # Interface desktop moderne
            from launch_demo_windows import main
            return main()
            
        elif interface_type == "desktop_simple":
            # Interface desktop simple
            from desktop_app_simple import main
            return main()
            
        elif interface_type == "console":
            # Interface console
            subprocess.run([sys.executable, "demo_console.py"])
            return True
            
        else:
            print("❌ Type d'interface non reconnu")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return False

def show_menu(env_info):
    """Afficher le menu de sélection"""
    print("=" * 60)
    print("🎮 MENU DE SÉLECTION")
    print("=" * 60)
    
    options = []
    
    # Options disponibles selon l'environnement
    if env_info["has_customtkinter"] and env_info["has_tkinter"]:
        options.append(("1", "Desktop moderne (CustomTkinter)", "desktop_modern"))
    
    if env_info["has_tkinter"]:
        options.append(("2", "Desktop simple (tkinter)", "desktop_simple"))
    
    options.append(("3", "Console", "console"))
    options.append(("4", "Test système", "test"))
    options.append(("5", "Setup/Installation", "setup"))
    options.append(("q", "Quitter", "quit"))
    
    # Afficher les options
    for key, label, _ in options:
        print(f"{key}. {label}")
    
    print()
    choice = input("Votre choix: ").strip().lower()
    
    # Trouver l'option correspondante
    for key, label, interface_type in options:
        if choice == key:
            if interface_type == "quit":
                return None
            elif interface_type == "setup":
                if run_setup():
                    # Relancer après setup
                    return main()
                else:
                    return False
            elif interface_type == "test":
                subprocess.run([sys.executable, "test_system.py"])
                return True
            else:
                return launch_interface(interface_type)
    
    print("❌ Choix invalide")
    return show_menu(env_info)

def main():
    """Fonction principale"""
    print("🤖 SYSTÈME MULTI-AGENT - KACM QUALCOMM")
    print("Lanceur intelligent v1.0")
    print()
    
    # Détecter l'environnement
    env_info = detect_environment()
    print_environment_info(env_info)
    
    # Vérifier si on peut lancer automatiquement
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "auto":
            # Mode automatique
            interface_type = choose_interface(env_info)
            if interface_type:
                return launch_interface(interface_type)
            else:
                return False
                
        elif mode == "console":
            return launch_interface("console")
            
        elif mode == "desktop":
            if env_info["has_tkinter"]:
                return launch_interface("desktop_simple")
            else:
                print("❌ tkinter non disponible")
                return launch_interface("console")
                
        elif mode == "test":
            subprocess.run([sys.executable, "test_system.py"])
            return True
            
        elif mode == "setup":
            return run_setup()
            
        else:
            print(f"❌ Mode inconnu: {mode}")
            print("Modes disponibles: auto, console, desktop, test, setup")
            return False
    
    else:
        # Mode interactif
        return show_menu(env_info)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🔴 Arrêt demandé par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)
