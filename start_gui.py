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
        print("✅ Graphical interface available")
        
        # Add agents path
        agents_path = Path(__file__).parent / "agents"
        if agents_path.exists():
            sys.path.insert(0, str(agents_path))
            print("✅ Agents loaded")
        
        # Import and launch interface
        from gui_file_organizer import FileOrganizerGUI
        
        print("🎨 Creating interface...")
        app = FileOrganizerGUI()
        
        print("✅ Interface ready!")
        print("\n📋 Available features:")
        print("- 🔍 Intelligent file analysis")
        print("- 🗂️ Automatic organization by business categories")
        print("- 🔒 Encryption of sensitive folders")
        print("- 📊 Detailed reports and statistics")
        print("- ⚡ Complete automated workflow")
        print("\n🎯 ZERO 'general' category guaranteed!")
        
        # Launch interface
        print("\n🎨 Launching graphical interface...")
        app.run()
        
    except ImportError as e:
        print(f"❌ Graphical interface not available: {e}")
        print("💡 Check that Tkinter is installed")
        return 1
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
