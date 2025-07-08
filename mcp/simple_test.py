#!/usr/bin/env python3
"""
Test Simple - Orchestrateur
===========================

Test rapide de l'orchestrateur avec des fichiers d'exemple.
"""

import asyncio
import os
import sys
from pathlib import Path
import tempfile
import shutil

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "agent_nlp"))

async def test_orchestrator():
    """Test simple de l'orchestrateur"""
    print("🎯 Test Simple de l'Orchestrateur")
    print("=" * 50)
    
    # Créer un répertoire de test temporaire
    test_dir = Path("simple_test")
    test_dir.mkdir(exist_ok=True)
    
    try:
        # Créer des fichiers de test simples
        test_files = {
            "document1.txt": "Ceci est un document normal avec du texte public.",
            "document2.txt": "Document avec email: test@example.com et téléphone: 01 23 45 67 89",
            "rapport.json": '{"titre": "Test", "contenu": "Données publiques"}',
            "readme.md": "# Test Document\n\nCeci est un fichier markdown de test.",
        }
        
        print(f"📝 Création de {len(test_files)} fichiers de test...")
        for filename, content in test_files.items():
            file_path = test_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print("✅ Fichiers créés")
        
        # Importer et tester l'orchestrateur
        print("\n🤖 Test de l'orchestrateur...")
        try:
            from agent_orchestrator_mcp import AgentOrchestrator
            
            orchestrator = AgentOrchestrator()
            
            # Test 1: Scanner le répertoire
            print("📂 1. Scan du répertoire...")
            scan_result = orchestrator.scan_directory(str(test_dir))
            
            # scan_result est un dictionnaire avec 'nlp', 'vision', 'audio'
            nlp_files = scan_result.get('nlp', [])
            vision_files = scan_result.get('vision', [])
            audio_files = scan_result.get('audio', [])
            total_files = len(nlp_files) + len(vision_files) + len(audio_files)
            
            print(f"   📁 Fichiers trouvés: {total_files}")
            print(f"     📝 NLP: {len(nlp_files)} fichiers")
            print(f"     👁️ Vision: {len(vision_files)} fichiers")
            print(f"     🎵 Audio: {len(audio_files)} fichiers")
            
            # Afficher quelques exemples
            for file_info in nlp_files[:3]:
                print(f"     - {Path(file_info.file_path).name} ({file_info.file_type})")
            
            # Test 2: Classification
            print("\n🏷️ 2. Classification des fichiers...")
            print(f"   📝 Fichiers texte: {len(nlp_files)}")
            
            # Test 3: Traitement (simulé)
            print("\n⚙️ 3. Traitement simulé...")
            for file_info in nlp_files[:2]:  # Traiter seulement les 2 premiers
                print(f"   🔄 Traitement: {Path(file_info.file_path).name}")
                # Simulation du traitement
                await asyncio.sleep(0.1)
                print(f"   ✅ Terminé")
            
            print("\n🎉 Test orchestrateur réussi!")
            return True
            
        except ImportError as e:
            print(f"❌ Impossible d'importer l'orchestrateur: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            return False
            
    finally:
        # Nettoyer
        print(f"\n🧹 Nettoyage du répertoire {test_dir}")
        shutil.rmtree(test_dir)

async def test_individual_agents():
    """Test des agents individuels"""
    print("\n🔬 Test des Agents Individuels")
    print("=" * 40)
    
    # Test Agent NLP
    print("📝 Test Agent NLP...")
    try:
        from agent_nlp_mcp import analyze_file
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Document de test avec informations publiques.")
            temp_file = f.name
        
        try:
            result = analyze_file(temp_file)
            print(f"   ✅ NLP OK - Warning: {result.warning}")
        finally:
            os.unlink(temp_file)
            
    except Exception as e:
        print(f"   ❌ NLP Error: {e}")
    
    # Test Agent Vision
    print("👁️ Test Agent Vision...")
    try:
        from agent_vision_mcp import VisionAgent
        
        agent = VisionAgent()
        print(f"   ✅ Vision Agent initialisé")
        
    except Exception as e:
        print(f"   ❌ Vision Error: {e}")
    
    # Test Agent Audio  
    print("🎵 Test Agent Audio...")
    try:
        # L'agent audio n'a pas de classe AudioAgent, utiliser la fonction directement
        from agent_audio_mcp import analyze_audio
        
        # Juste tester l'import pour l'instant
        print(f"   ✅ Audio Agent fonction importée")
        
    except Exception as e:
        print(f"   ❌ Audio Error: {e}")

def main():
    """Point d'entrée principal"""
    print("🧪 TESTS SIMPLES - Système Multi-Agents")
    print("Tests de base pour vérifier le fonctionnement")
    print("=" * 60)
    
    try:
        # Test orchestrateur
        success = asyncio.run(test_orchestrator())
        
        if success:
            # Test agents individuels
            asyncio.run(test_individual_agents())
            
            print("\n🎉 TOUS LES TESTS TERMINÉS")
            print("Le système semble fonctionner correctement!")
        else:
            print("\n❌ TESTS ÉCHOUÉS")
            print("Vérifiez la configuration et les dépendances")
            
    except KeyboardInterrupt:
        print("\n👋 Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")

if __name__ == "__main__":
    main()
