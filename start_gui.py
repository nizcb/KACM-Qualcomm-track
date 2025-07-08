#!/usr/bin/env python3
"""
Startup script for graphical interface
======================================

Launches the complete graphical interface of the intelligent file organizer.
"""

import sys
import os
from pathlib import Path

def main():
    print("🚀 Starting graphical interface...")
    print("📁 Intelligent File Organizer")
    print("=" * 50)
    
    try:
        # Vérifier Tkinter
        import tkinter as tk
        print("✅ Interface graphique disponible")
        
        # Ajouter le chemin des agents
        agents_path = Path(__file__).parent / "agents"
        if agents_path.exists():
            sys.path.insert(0, str(agents_path))
            print("✅ Agents chargés")
        
        # Importer et lancer l'interface
        from gui_file_organizer import FileOrganizerGUI
        
        print("🎨 Création de l'interface...")
        app = FileOrganizerGUI()
        
        print("✅ Interface prête!")
        print("\n📋 Fonctionnalités disponibles:")
        print("- 🔍 Analyse intelligente des files")
        print("- 🗂️ Organisation automatique par catégories métier")
        print("- 🔒 Chiffrement des dossiers sensibles")
        print("- 📊 Rapports détaillés et statistiques")
        print("- ⚡ Workflow complet automatisé")
        print("\n🎯 ZÉRO catégorie 'general' garantie!")
        
        # Lancer l'interface
        print("\n🎨 Lancement de l'interface graphique...")
        app.run()
        
    except ImportError as e:
        print(f"❌ Interface graphique non disponible: {e}")
        print("💡 Vérifiez que Tkinter est installé")
        return 1
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
