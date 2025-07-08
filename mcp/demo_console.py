#!/usr/bin/env python3
"""
Démonstration Console - Système Multi-Agent
==========================================

Démonstration en mode console qui fonctionne sans interface graphique.
Parfait pour WSL et les environnements sans GUI.
"""

import asyncio
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent))

from simple_mcp_system import orchestrator

def print_banner():
    """Afficher la bannière"""
    print("=" * 70)
    print("🤖 SYSTÈME MULTI-AGENT - DÉMONSTRATION CONSOLE")
    print("   KACM Qualcomm Hackathon")
    print("   Intelligence Artificielle Agentique")
    print("=" * 70)
    print()

def print_separator(title=""):
    """Afficher un séparateur"""
    if title:
        print("\n" + "=" * 60)
        print(f"🎯 {title}")
        print("=" * 60)
    else:
        print("-" * 60)

def create_demo_environment():
    """Créer l'environnement de démonstration"""
    print("🏗️ Création de l'environnement de démonstration...")
    
    # Créer les dossiers
    folders = ["demo_files", "encrypted", "decrypted", "vault", "logs"]
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
    
    # Créer des fichiers de test réalistes
    demo_files = {
        "demo_files/document_public.txt": """
Rapport Mensuel - Novembre 2024
===============================

Ce document présente les résultats du mois de novembre.
Aucune information confidentielle n'est présente dans ce rapport.

Résultats:
- Objectifs atteints: 95%
- Satisfaction client: 4.2/5
- Croissance: +12%

Conclusion: Mois très positif pour l'équipe.
        """.strip(),
        
        "demo_files/document_confidentiel.txt": """
DOCUMENT CONFIDENTIEL - ACCÈS RESTREINT
======================================

Informations personnelles des employés:

Employé 1:
- Nom: Jean Dupont
- Email: jean.dupont@entreprise.com
- Téléphone: 06 12 34 56 78
- N° Sécurité Sociale: 1 23 45 67 890 123 45

Employé 2:
- Nom: Marie Martin
- Email: marie.martin@entreprise.com
- Téléphone: 06 98 76 54 32
- IBAN: FR14 2004 1010 0505 0001 3M02 606

Ces informations sont strictement confidentielles.
        """.strip(),
        
        "demo_files/carte_vitale_scan.jpg": "FAKE_IMAGE_DATA_CARTE_VITALE_SENSIBLE",
        "demo_files/photo_identite.png": "FAKE_IMAGE_DATA_PHOTO_IDENTITE_SENSIBLE",
        "demo_files/passeport_scan.pdf": "FAKE_PDF_DATA_PASSEPORT_SENSIBLE",
        "demo_files/facture_electricite.pdf": "FAKE_PDF_DATA_FACTURE_NORMALE",
        "demo_files/cours_histoire.pdf": "FAKE_PDF_DATA_COURS_HISTOIRE_NORMALE",
        "demo_files/musique_detente.mp3": "FAKE_AUDIO_DATA_MUSIQUE",
        
        "demo_files/data_clients.json": json.dumps({
            "clients": [
                {
                    "id": 1,
                    "nom": "Jean Dupont",
                    "email": "jean.dupont@email.com",
                    "telephone": "06 12 34 56 78",
                    "adresse": "123 Rue de la Paix, 75001 Paris"
                },
                {
                    "id": 2,
                    "nom": "Marie Martin",
                    "email": "marie.martin@email.com", 
                    "telephone": "06 98 76 54 32",
                    "carte_bancaire": "4532 1234 5678 9012"
                }
            ]
        }, indent=2),
        
        "demo_files/readme.md": """# Documentation Projet

## Description
Ceci est la documentation du projet de démonstration.

## Fonctionnalités
- Analyse automatique de fichiers
- Détection d'informations sensibles
- Chiffrement sécurisé

## Utilisation
Suivez les instructions dans le README principal.
        """.strip(),
    }
    
    # Écrire les fichiers
    for file_path, content in demo_files.items():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Environnement créé avec succès")
    return Path("demo_files")

async def demo_file_analysis(demo_dir):
    """Démonstration de l'analyse de fichiers"""
    print_separator("ANALYSE AUTOMATIQUE DE FICHIERS")
    
    print("📁 Répertoire à analyser:", demo_dir.absolute())
    print("⏳ Démarrage de l'analyse...")
    
    # Démarrer les agents
    await orchestrator.start_all_agents()
    print("✅ Tous les agents sont démarrés")
    
    # Analyser le répertoire
    result = await orchestrator.process_directory(str(demo_dir))
    
    print_separator()
    print("📊 RÉSULTATS DE L'ANALYSE")
    print(f"   📄 Fichiers traités: {result['processed_files']}")
    print(f"   ⚠️  Fichiers sensibles: {result['files_with_warnings']}")
    print(f"   ⏱️  Temps de traitement: {result['processing_time']:.2f}s")
    
    print_separator()
    print("📋 DÉTAIL DES FICHIERS")
    
    for i, file_result in enumerate(result['results'], 1):
        print(f"\n{i}. 📄 {file_result['filename']}")
        print(f"   🏷️  Type: {file_result['extension']}")
        print(f"   🤖 Agent: {file_result['agent_type']}")
        print(f"   📝 Résumé: {file_result['summary'][:80]}...")
        
        if file_result['is_sensitive']:
            print(f"   🔒 SENSIBLE: Fichier chiffré automatiquement")
        else:
            print(f"   ✅ NORMAL: Aucune information sensible détectée")
    
    return result

async def demo_smart_search():
    """Démonstration de la recherche intelligente"""
    print_separator("RECHERCHE INTELLIGENTE AVEC IA")
    
    search_queries = [
        "trouve moi le scan de ma carte vitale",
        "donne moi le pdf de cours d'histoire", 
        "où est ma photo d'identité",
        "liste les documents contenant des emails",
        "fichiers avec informations bancaires"
    ]
    
    print("🔍 Test de différentes requêtes de recherche:")
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n{i}. 🔍 Requête: \"{query}\"")
        print("   ⏳ Recherche en cours...")
        
        search_result = await orchestrator.smart_search(query)
        
        print(f"   📊 Résultats trouvés: {search_result['total_results']}")
        print(f"   ⏱️  Temps de recherche: {search_result['search_time']:.2f}s")
        
        if search_result['results']:
            for j, result in enumerate(search_result['results'], 1):
                print(f"      {j}. 📄 {result['filename']}")
                print(f"         📍 Emplacement: {result['location']}")
                
                if result.get('requires_auth'):
                    print(f"         🔒 Authentification requise")
                else:
                    print(f"         ✅ Accès libre")
        else:
            print("      ❌ Aucun fichier correspondant")

async def demo_security_vault():
    """Démonstration du système de sécurité"""
    print_separator("SYSTÈME DE SÉCURITÉ ET VAULT")
    
    print("🔐 Test du système de chiffrement/déchiffrement...")
    
    # Créer un fichier de test
    test_file = Path("demo_files/test_securite.txt")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Fichier de test pour le système de sécurité\n")
        f.write("Email de test: test@example.com\n")
        f.write("Numéro de téléphone: 06 12 34 56 78\n")
    
    security_agent = orchestrator.security_agent
    
    # Test de chiffrement
    print("\n1. 🔒 Test de chiffrement")
    encrypt_result = await security_agent.call_tool(
        "encrypt_file",
        file_path=str(test_file),
        password="mon_secret_ultra_securise_2024"
    )
    print(f"   ✅ {encrypt_result['message']}")
    print(f"   🆔 ID du fichier: {encrypt_result['file_id']}")
    
    # Test de déchiffrement avec bon mot de passe
    print("\n2. 🔓 Test de déchiffrement (bon mot de passe)")
    decrypt_result = await security_agent.call_tool(
        "decrypt_file",
        file_id=encrypt_result['file_id'],
        password="mon_secret_ultra_securise_2024"
    )
    print(f"   ✅ {decrypt_result['message']}")
    
    # Test de déchiffrement avec mauvais mot de passe
    print("\n3. ❌ Test de déchiffrement (mauvais mot de passe)")
    bad_decrypt_result = await security_agent.call_tool(
        "decrypt_file",
        file_id=encrypt_result['file_id'],
        password="mauvais_mot_de_passe"
    )
    print(f"   ❌ {bad_decrypt_result['message']}")
    
    # Afficher les statistiques du vault
    print("\n4. 📊 Statistiques du vault")
    import sqlite3
    conn = sqlite3.connect(security_agent.vault_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vault_files")
    vault_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"   📁 Fichiers dans le vault: {vault_count}")

def demo_interactive_search():
    """Mode recherche interactive"""
    print_separator("MODE RECHERCHE INTERACTIVE")
    
    print("🎯 Vous pouvez maintenant faire des recherches interactives!")
    print("💡 Exemples de requêtes:")
    print("   - 'trouve moi le scan de ma carte vitale'")
    print("   - 'donne moi le pdf de cours d'histoire'")
    print("   - 'où est ma photo d'identité'")
    print("   - 'quit' pour quitter")
    print()
    
    while True:
        try:
            query = input("🔍 Votre recherche: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            print("   ⏳ Recherche en cours...")
            
            # Exécuter la recherche de manière synchrone
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            search_result = loop.run_until_complete(orchestrator.smart_search(query))
            loop.close()
            
            print(f"   📊 Résultats: {search_result['total_results']}")
            
            if search_result['results']:
                for i, result in enumerate(search_result['results'], 1):
                    print(f"      {i}. 📄 {result['filename']}")
                    print(f"         📍 {result['location']}")
                    
                    if result.get('requires_auth'):
                        print(f"         🔒 Fichier chiffré - Authentification requise")
                        
                        # Demander si l'utilisateur veut déchiffrer
                        choice = input("         Voulez-vous déchiffrer ce fichier? (o/n): ").strip().lower()
                        if choice == 'o':
                            password = input("         🔑 Mot de passe: ")
                            
                            # Tenter le déchiffrement
                            try:
                                security_agent = orchestrator.security_agent
                                vault_id = result.get('vault_id', 'unknown')
                                
                                decrypt_loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(decrypt_loop)
                                decrypt_result = decrypt_loop.run_until_complete(
                                    security_agent.call_tool("decrypt_file", file_id=vault_id, password=password)
                                )
                                decrypt_loop.close()
                                
                                if decrypt_result['success']:
                                    print(f"         ✅ {decrypt_result['message']}")
                                    print(f"         📁 Fichier disponible: {decrypt_result['decrypted_path']}")
                                else:
                                    print(f"         ❌ {decrypt_result['message']}")
                            except Exception as e:
                                print(f"         ❌ Erreur lors du déchiffrement: {e}")
                    else:
                        print(f"         ✅ Accès libre")
            else:
                print("      ❌ Aucun fichier correspondant")
            
            print()
        
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")

async def run_complete_demo():
    """Exécuter la démonstration complète"""
    print_banner()
    
    # Créer l'environnement
    demo_dir = create_demo_environment()
    
    try:
        # 1. Analyse des fichiers
        analysis_result = await demo_file_analysis(demo_dir)
        
        input("\n⏸️  Appuyez sur Entrée pour continuer vers la recherche intelligente...")
        
        # 2. Recherche intelligente
        await demo_smart_search()
        
        input("\n⏸️  Appuyez sur Entrée pour continuer vers les tests de sécurité...")
        
        # 3. Tests de sécurité
        await demo_security_vault()
        
        input("\n⏸️  Appuyez sur Entrée pour continuer vers le mode interactif...")
        
        # 4. Mode interactif
        demo_interactive_search()
        
    finally:
        # Arrêter les agents
        await orchestrator.stop_all_agents()
        print("✅ Tous les agents ont été arrêtés")
    
    print_separator("DÉMONSTRATION TERMINÉE")
    print("🎉 Merci d'avoir testé le système multi-agents!")
    print("📁 Les fichiers de démonstration sont dans:", demo_dir.absolute())
    print("🔒 Les fichiers chiffrés sont dans: encrypted/")
    print("🔓 Les fichiers déchiffrés sont dans: decrypted/")

def main():
    """Fonction principale"""
    try:
        asyncio.run(run_complete_demo())
    except KeyboardInterrupt:
        print("\n🔴 Démonstration interrompue par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
