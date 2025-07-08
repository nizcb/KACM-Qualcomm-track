#!/usr/bin/env python
"""
Démonstration du Workflow MCP - Version Finale
==============================================

Ce script démontre le workflow complet de traitement d'un dossier
avec l'agent NLP MCP, incluant toutes les fonctionnalités IA.
"""

import os
import sys
import json
from datetime import datetime

def main():
    print("=" * 60)
    print("🚀 DÉMONSTRATION WORKFLOW MCP - AGENT IA NLP")
    print("=" * 60)
    
    try:
        # Import du module principal
        from agent_nlp_mcp import get_agent, process_multiple_files, analyze_file
        
        print("✅ Module agent_nlp_mcp importé avec succès")
        
        # Créer l'agent
        agent = get_agent()
        
        ai_status = "IA COMPLÈTE" if agent.llm else "MODE FALLBACK"
        print(f"✅ Agent NLP initialisé - {ai_status}")
        
        # Définir le dossier de test
        test_directory = "test_workflow"
        
        if not os.path.exists(test_directory):
            print(f"❌ Dossier {test_directory} non trouvé")
            return False
        
        print(f"📁 Analyse du dossier: {test_directory}")
        
        # Collecter tous les fichiers
        file_paths = []
        for root, dirs, files in os.walk(test_directory):
            for file in files:
                if file.endswith(('.txt', '.md', '.json', '.py', '.csv')):
                    file_paths.append(os.path.join(root, file))
        
        print(f"📊 {len(file_paths)} fichiers trouvés:")
        for i, filepath in enumerate(file_paths, 1):
            filename = os.path.basename(filepath)
            print(f"  {i}. {filename}")
        
        if not file_paths:
            print("⚠️ Aucun fichier à traiter")
            return False
        
        # TRAITEMENT EN LOT COMPLET
        print(f"\n🔄 LANCEMENT DU WORKFLOW COMPLET...")
        print("=" * 50)
        
        # Utiliser la méthode de traitement en lot de l'agent
        batch_result = agent.process_multiple_files_with_reasoning(file_paths)
        
        # AFFICHAGE DES RÉSULTATS
        print(f"\n📈 RÉSULTATS DU TRAITEMENT:")
        print(f"  ✅ Total fichiers: {batch_result['batch_info']['total_files']}")
        print(f"  📄 Fichiers traités: {batch_result['batch_info']['processed_files']}")
        print(f"  🚨 Fichiers avec PII: {batch_result['batch_info']['files_with_pii']}")
        print(f"  📅 Date de traitement: {batch_result['batch_info']['processing_date']}")
        
        print(f"\n📋 ANALYSE DÉTAILLÉE PAR FICHIER:")
        print("-" * 50)
        
        for i, file_info in enumerate(batch_result['files'], 1):
            # Statut de sécurité
            if file_info['has_pii']:
                security_status = "🚨 ATTENTION - PII DÉTECTÉES"
            else:
                security_status = "✅ SÉCURISÉ"
            
            print(f"\n{i}. 📄 {file_info['file']}")
            print(f"   {security_status}")
            print(f"   📝 Résumé: {file_info['summary_preview']}")
            print(f"   📂 Chemin: {file_info['path']}")
        
        # RÉSULTATS DÉTAILLÉS
        print(f"\n🔍 RÉSULTATS DÉTAILLÉS:")
        print("-" * 30)
        
        for filename, details in batch_result['detailed_results'].items():
            print(f"\n📄 {filename}:")
            print(f"   📝 Résumé complet: {details['resume'][:150]}...")
            print(f"   ⚠️ PII détectées: {'OUI' if details['warning'] else 'NON'}")
        
        # SAUVEGARDE DU RAPPORT
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"workflow_demo_report_{timestamp}.json"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(batch_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 RAPPORT COMPLET SAUVEGARDÉ: {report_filename}")
        
        # STATISTIQUES FINALES
        print(f"\n📊 STATISTIQUES FINALES:")
        print("=" * 30)
        
        total_files = batch_result['batch_info']['total_files']
        pii_files = batch_result['batch_info']['files_with_pii']
        safe_files = total_files - pii_files
        
        pii_percentage = (pii_files / total_files * 100) if total_files > 0 else 0
        
        print(f"📈 Fichiers analysés: {total_files}")
        print(f"✅ Fichiers sécurisés: {safe_files}")
        print(f"🚨 Fichiers avec PII: {pii_files}")
        print(f"📊 Pourcentage PII: {pii_percentage:.1f}%")
        
        if pii_files > 0:
            print(f"\n⚠️ RECOMMANDATION:")
            print(f"   {pii_files} fichier(s) contiennent des informations sensibles.")
            print(f"   Vérifiez les permissions d'accès et la conformité RGPD.")
        else:
            print(f"\n✅ EXCELLENT!")
            print(f"   Aucune information personnelle détectée.")
            print(f"   Tous les fichiers sont conformes.")
        
        print(f"\n🎉 WORKFLOW TERMINÉ AVEC SUCCÈS!")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Vérifiez que tous les modules sont installés")
        return False
        
    except Exception as e:
        print(f"❌ Erreur durant l'exécution: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 Démarrage de la démonstration...")
    
    success = main()
    
    if success:
        print(f"\n{'='*60}")
        print("🎊 DÉMONSTRATION RÉUSSIE!")
        print("🚀 Le système MCP est pleinement opérationnel")
        print("💡 Utilisez les outils MCP pour intégrer avec d'autres systèmes")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ DÉMONSTRATION ÉCHOUÉE")
        print("🔧 Vérifiez la configuration et les dépendances")
        print(f"{'='*60}")
    
    input("\n👆 Appuyez sur Entrée pour terminer...")
    sys.exit(0 if success else 1)
