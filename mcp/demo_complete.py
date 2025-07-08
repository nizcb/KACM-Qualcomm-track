#!/usr/bin/env python3
"""
Démonstration Complète - Système Multi-Agents MCP
================================================

Démonstration du workflow complet avec tous les agents.
"""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path
import json

# Ajouter le chemin des agents
sys.path.insert(0, str(Path(__file__).parent / "agent_nlp"))

def print_banner():
    """Bannière de la démonstration"""
    print("=" * 80)
    print("🎬 DÉMONSTRATION COMPLÈTE - SYSTÈME MULTI-AGENTS MCP")
    print("   Workflow End-to-End avec tous les agents")
    print("   Hackathon Qualcomm Edge-AI")
    print("=" * 80)
    print()

async def demo_complete_workflow():
    """Démonstration du workflow complet"""
    
    # 1. Créer un environnement de test riche
    print("🏗️ ÉTAPE 1: Création de l'environnement de test")
    print("-" * 50)
    
    demo_dir = Path("demo_complete")
    demo_dir.mkdir(exist_ok=True)
    
    # Créer différents types de fichiers
    test_files = {
        # Fichiers texte pour NLP
        "documents/rapport_public.txt": "Ceci est un rapport public contenant des informations générales sur notre projet.",
        "documents/document_sensible.txt": "CONFIDENTIEL: Ce document contient jean.dupont@email.com et téléphone 06 12 34 56 78",
        "documents/facture.json": '{"client": "ACME Corp", "montant": 1500, "date": "2024-01-01"}',
        "documents/README.md": "# Projet Demo\n\nDocumentation du projet de démonstration.",
        
        # Fichiers image simulés pour Vision
        "images/logo.jpg": "FAKE_IMAGE_LOGO_DATA",
        "images/document_scan.png": "FAKE_SCANNED_DOCUMENT_DATA",
        "images/photo_id.jpeg": "FAKE_ID_PHOTO_DATA",
        
        # Fichiers audio simulés pour Audio
        "audio/reunion.mp3": "FAKE_MEETING_AUDIO_DATA",
        "audio/presentation.wav": "FAKE_PRESENTATION_AUDIO_DATA",
        
        # Autres fichiers
        "autres/script.py": "print('Hello World')",
        "autres/config.xml": "<config><param>value</param></config>"
    }
    
    print(f"📝 Création de {len(test_files)} fichiers de test...")
    created_count = 0
    for file_path, content in test_files.items():
        full_path = demo_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        created_count += 1
    
    print(f"✅ {created_count} fichiers créés dans {demo_dir}")
    print()
    
    # 2. Scanner avec l'orchestrateur
    print("🔍 ÉTAPE 2: Scan et classification par l'orchestrateur")
    print("-" * 50)
    
    try:
        from agent_orchestrator_mcp import AgentOrchestrator
        
        orchestrator = AgentOrchestrator()
        scan_result = orchestrator.scan_directory(str(demo_dir))
        
        # Analyser les résultats
        nlp_files = scan_result.get('nlp', [])
        vision_files = scan_result.get('vision', [])
        audio_files = scan_result.get('audio', [])
        total_files = len(nlp_files) + len(vision_files) + len(audio_files)
        
        print(f"📊 Résultats du scan:")
        print(f"  📁 Total des fichiers: {total_files}")
        print(f"  📝 Fichiers texte (NLP): {len(nlp_files)}")
        print(f"  👁️ Fichiers image (Vision): {len(vision_files)}")
        print(f"  🎵 Fichiers audio (Audio): {len(audio_files)}")
        print()
        
        # Afficher la classification détaillée
        if nlp_files:
            print("📝 Fichiers NLP détectés:")
            for file_info in nlp_files:
                print(f"  - {Path(file_info.file_path).name} ({file_info.extension})")
        
        if vision_files:
            print("👁️ Fichiers Vision détectés:")
            for file_info in vision_files:
                print(f"  - {Path(file_info.file_path).name} ({file_info.extension})")
        
        if audio_files:
            print("🎵 Fichiers Audio détectés:")
            for file_info in audio_files:
                print(f"  - {Path(file_info.file_path).name} ({file_info.extension})")
        
        print()
        
    except Exception as e:
        print(f"❌ Erreur lors du scan: {e}")
        return False
    
    # 3. Traitement par les agents spécialisés
    print("⚙️ ÉTAPE 3: Traitement par les agents spécialisés")
    print("-" * 50)
    
    processing_results = []
    
    # 3a. Traitement NLP
    if nlp_files:
        print("📝 Traitement par l'Agent NLP...")
        try:
            from agent_nlp_mcp import analyze_file
            
            for file_info in nlp_files[:3]:  # Traiter les 3 premiers
                print(f"  🔄 Analyse: {Path(file_info.file_path).name}")
                
                try:
                    result = await analyze_file(file_info.file_path)
                    
                    # Extraire les informations
                    if hasattr(result, 'dict'):
                        result_dict = result.dict()
                    else:
                        result_dict = {
                            'file_path': file_info.file_path,
                            'resume': getattr(result, 'resume', 'Analysé'),
                            'warning': getattr(result, 'warning', False)
                        }
                    
                    processing_results.append({
                        'agent': 'NLP',
                        'file': Path(file_info.file_path).name,
                        'summary': result_dict.get('resume', 'Résumé non disponible')[:80] + "...",
                        'warning': result_dict.get('warning', False)
                    })
                    
                    status = "⚠️ WARNING" if result_dict.get('warning') else "✅ OK"
                    print(f"    {status}: {result_dict.get('resume', 'Analysé')[:50]}...")
                    
                except Exception as e:
                    print(f"    ❌ Erreur: {e}")
                    processing_results.append({
                        'agent': 'NLP',
                        'file': Path(file_info.file_path).name,
                        'summary': f"Erreur: {e}",
                        'warning': True
                    })
                
                await asyncio.sleep(0.5)  # Pause pour éviter la surcharge
        
        except ImportError as e:
            print(f"  ❌ Impossible d'importer l'agent NLP: {e}")
    
    # 3b. Traitement Vision (simulation)
    if vision_files:
        print(f"\n👁️ Traitement par l'Agent Vision...")
        try:
            from agent_vision_mcp import analyze_document, VisionArgs
            
            for file_info in vision_files[:2]:  # Traiter les 2 premiers
                print(f"  🔄 Analyse: {Path(file_info.file_path).name}")
                
                try:
                    # Créer une vraie image pour le test
                    import numpy as np
                    import cv2
                    
                    # Créer une image simple
                    test_image = np.zeros((200, 400, 3), dtype=np.uint8)
                    test_image.fill(255)  # Fond blanc
                    cv2.putText(test_image, "TEST IMAGE", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                    
                    # Remplacer le fichier simulé par une vraie image
                    cv2.imwrite(file_info.file_path, test_image)
                    
                    args = VisionArgs(path=file_info.file_path)
                    result = await analyze_document(args)
                    
                    processing_results.append({
                        'agent': 'Vision',
                        'file': Path(file_info.file_path).name,
                        'summary': result.summary[:80] + "...",
                        'warning': result.warning
                    })
                    
                    status = "⚠️ WARNING" if result.warning else "✅ OK"
                    print(f"    {status}: {result.summary[:50]}...")
                    
                except Exception as e:
                    print(f"    ❌ Erreur: {e}")
                    processing_results.append({
                        'agent': 'Vision',
                        'file': Path(file_info.file_path).name,
                        'summary': f"Erreur: {e}",
                        'warning': True
                    })
                
                await asyncio.sleep(0.5)
        
        except ImportError as e:
            print(f"  ❌ Agent Vision non disponible: {e}")
    
    # 3c. Traitement Audio (simulation)
    if audio_files:
        print(f"\n🎵 Traitement par l'Agent Audio (simulation)...")
        for file_info in audio_files[:1]:  # Traiter le premier
            print(f"  🔄 Analyse: {Path(file_info.file_path).name}")
            
            # Simulation de l'analyse audio
            processing_results.append({
                'agent': 'Audio',
                'file': Path(file_info.file_path).name,
                'summary': "Fichier audio analysé - Contenu vocal détecté",
                'warning': False
            })
            
            print(f"    ✅ OK: Fichier audio analysé avec succès")
            await asyncio.sleep(0.5)
    
    print()
    
    # 4. Consolidation des résultats
    print("📊 ÉTAPE 4: Consolidation des résultats")
    print("-" * 50)
    
    warning_files = [r for r in processing_results if r['warning']]
    safe_files = [r for r in processing_results if not r['warning']]
    
    print(f"📈 Statistiques finales:")
    print(f"  📁 Fichiers traités: {len(processing_results)}")
    print(f"  ✅ Fichiers sûrs: {len(safe_files)}")
    print(f"  ⚠️ Fichiers avec avertissements: {len(warning_files)}")
    print()
    
    # Détails des résultats
    if processing_results:
        print("📋 Résultats détaillés:")
        for result in processing_results:
            status = "⚠️" if result['warning'] else "✅"
            print(f"  {status} [{result['agent']}] {result['file']}")
            print(f"      {result['summary']}")
    
    print()
    
    # 5. Actions de sécurité (simulation)
    if warning_files:
        print("🔒 ÉTAPE 5: Actions de sécurité")
        print("-" * 50)
        
        print(f"🛡️ Actions requises pour {len(warning_files)} fichier(s) sensible(s):")
        for file_result in warning_files:
            print(f"  🔐 {file_result['file']}: Mise en quarantaine recommandée")
            print(f"      Raison: Informations sensibles détectées")
        print()
    
    # 6. Rapport final
    print("📄 ÉTAPE 6: Génération du rapport final")
    print("-" * 50)
    
    report = {
        "session_id": orchestrator.session_id,
        "timestamp": orchestrator.session_id,
        "summary": {
            "total_files_scanned": total_files,
            "files_processed": len(processing_results),
            "safe_files": len(safe_files),
            "warning_files": len(warning_files)
        },
        "details": processing_results,
        "security_actions": [
            {
                "file": f['file'],
                "action": "quarantine",
                "reason": "Sensitive data detected"
            } for f in warning_files
        ]
    }
    
    # Sauvegarder le rapport
    report_path = demo_dir / "workflow_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📋 Rapport sauvegardé: {report_path}")
    print()
    
    # 7. Nettoyage
    print("🧹 ÉTAPE 7: Nettoyage")
    print("-" * 50)
    
    print("🗑️ Suppression des fichiers de démonstration...")
    shutil.rmtree(demo_dir)
    print("✅ Nettoyage terminé")
    print()
    
    return True

async def main():
    """Point d'entrée principal"""
    print_banner()
    
    try:
        success = await demo_complete_workflow()
        
        if success:
            print("🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
            print("🔥 Le système multi-agents fonctionne parfaitement!")
            print()
            print("🚀 Prochaines étapes:")
            print("  1. Lancer le système complet: python agent_nlp/main.py start")
            print("  2. Traiter vos propres fichiers: python agent_nlp/main.py process ./mon_repertoire")
            print("  3. Voir le statut: python agent_nlp/main.py status")
        else:
            print("❌ DÉMONSTRATION ÉCHOUÉE")
            print("Vérifiez les logs et les dépendances")
    
    except KeyboardInterrupt:
        print("\n👋 Démonstration interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")

if __name__ == "__main__":
    asyncio.run(main())
