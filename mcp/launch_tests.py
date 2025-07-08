#!/usr/bin/env python3
"""
Lanceur de Test Complet - Système MCP
=====================================

Script simple pour tester tous les composants du système.
"""

import os
import sys
import subprocess
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
PYTHON_EXE = sys.executable

def run_test(script_name, description):
    """Exécute un script de test"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    script_path = BASE_DIR / script_name
    
    if not script_path.exists():
        print(f"❌ Script non trouvé: {script_name}")
        return False
    
    try:
        # Exécuter le script
        result = subprocess.run([PYTHON_EXE, str(script_path)], 
                              capture_output=True, text=True, timeout=60)
        
        print("📤 SORTIE:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ ERREURS:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Test terminé avec succès")
            return True
        else:
            print(f"❌ Test échoué (code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ Test interrompu (timeout)")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False

def main():
    """Fonction principale"""
    print("🎯 LANCEUR DE TEST COMPLET - SYSTÈME MCP")
    print("="*60)
    
    # Tests à exécuter
    tests = [
        ("test_complete_system.py", "Test complet du système"),
        ("demo_llama_integration.py", "Démonstration avec Llama3"),
        ("demo_console.py", "Démonstration console"),
    ]
    
    print("\nTests disponibles:")
    for i, (script, desc) in enumerate(tests, 1):
        print(f"{i}. {desc}")
    
    print("\nOptions:")
    print("a. Exécuter tous les tests")
    print("g. Lancer l'interface graphique")
    print("q. Quitter")
    
    try:
        choice = input("\nVotre choix: ").strip().lower()
        
        if choice == 'q':
            print("👋 Au revoir!")
            return
        
        elif choice == 'a':
            print("\n🚀 Exécution de tous les tests...")
            results = []
            
            for script, desc in tests:
                success = run_test(script, desc)
                results.append((desc, success))
            
            # Résumé final
            print(f"\n{'='*60}")
            print("📊 RÉSUMÉ DES TESTS")
            print(f"{'='*60}")
            
            passed = sum(1 for _, success in results if success)
            total = len(results)
            
            for desc, success in results:
                status = "✅" if success else "❌"
                print(f"{status} {desc}")
            
            print(f"\nRésultat: {passed}/{total} tests réussis")
            
            if passed == total:
                print("🎉 Tous les tests sont passés!")
            else:
                print("⚠️ Certains tests ont échoué")
        
        elif choice == 'g':
            print("\n🖥️ Lancement de l'interface graphique...")
            run_test("desktop_test_interface.py", "Interface graphique de test")
        
        elif choice.isdigit() and 1 <= int(choice) <= len(tests):
            index = int(choice) - 1
            script, desc = tests[index]
            run_test(script, desc)
        
        else:
            print("❌ Choix invalide")
    
    except KeyboardInterrupt:
        print("\n👋 Interruption par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
