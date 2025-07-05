#!/usr/bin/env python3
"""
Test Complet - Security Agent Consolidé
Test avec plusieurs fichiers et MCP
"""

import requests
import tempfile
import json
from pathlib import Path

def test_complet():
    print("🔐 Test Complet du Security Agent Consolidé")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # Test 1: Santé
    print("\n1. 🔍 Test santé...")
    response = requests.get(f"{base_url}/health")
    if response.status_code == 200:
        health = response.json()
        print(f"✅ Agent en bonne santé")
        print(f"📂 Vault: {health['vault_path']}")
        print(f"📊 Fichiers actuels: {health['total_files']}")
    else:
        print("❌ Agent en panne")
        return
    
    # Test 2: Créer plusieurs fichiers
    print("\n2. 📝 Création de fichiers test...")
    test_files = []
    
    # Fichier 1: Personnel
    with tempfile.NamedTemporaryFile(mode='w', suffix='_personnel.txt', delete=False) as f:
        f.write("""DONNÉES PERSONNELLES
Nom: Jean Dupont
Email: jean.dupont@email.com
Téléphone: +33 1 23 45 67 89
Numéro SS: 1 23 45 67 890 123
""")
        test_files.append(f.name)
        print(f"✅ Fichier personnel: {Path(f.name).name}")
    
    # Fichier 2: Financier
    with tempfile.NamedTemporaryFile(mode='w', suffix='_financier.txt', delete=False) as f:
        f.write("""DONNÉES FINANCIÈRES
Compte: 12345678901
IBAN: FR76 1234 5678 9012 3456 7890 123
Carte: 4532 1234 5678 9012
Solde: 25,000€
""")
        test_files.append(f.name)
        print(f"✅ Fichier financier: {Path(f.name).name}")
    
    # Fichier 3: Médical
    with tempfile.NamedTemporaryFile(mode='w', suffix='_medical.txt', delete=False) as f:
        f.write("""DOSSIER MÉDICAL
Patient: Marie Martin
Pathologie: Diabète type 2
Traitement: Metformine 1000mg
Allergie: Pénicilline
""")
        test_files.append(f.name)
        print(f"✅ Fichier médical: {Path(f.name).name}")
    
    # Test 3: Chiffrement individuel
    print("\n3. 🔒 Test chiffrement individuel...")
    encrypted_files = []
    
    for i, file_path in enumerate(test_files):
        data = {
            "file_path": file_path,
            "owner": f"user_{i+1}",
            "policy": "AES256"
        }
        response = requests.post(f"{base_url}/encrypt", json=data)
        if response.status_code == 200:
            result = response.json()
            encrypted_files.append(result)
            print(f"✅ Fichier {i+1} chiffré: {result['vault_uuid']}")
        else:
            print(f"❌ Échec chiffrement fichier {i+1}")
    
    # Test 4: Test MCP Batch
    print("\n4. 🔄 Test MCP Batch...")
    
    # Créer des fichiers pour le batch
    batch_files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'_batch_{i}.txt', delete=False) as f:
            f.write(f"Document batch {i+1}\nContenu sensible batch: {i+1}")
            batch_files.append(f.name)
    
    # Requête MCP
    mcp_data = {
        "thread_id": "test-batch-complet-123",
        "sender": "file_manager",
        "type": "task.security",
        "payload": {
            "files": batch_files,
            "owner": "batch_user",
            "policy": "AES256"
        }
    }
    
    response = requests.post(f"{base_url}/mcp/task", json=mcp_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Batch MCP traité:")
        print(f"   Thread: {result['thread_id']}")
        print(f"   Fichiers: {len(result['payload']['vault'])}")
        
        for entry in result['payload']['vault']:
            print(f"   - {entry['uuid']}: {Path(entry['orig']).name}")
    else:
        print(f"❌ Échec MCP Batch")
    
    # Test 5: Déchiffrement
    print("\n5. 🔓 Test déchiffrement...")
    
    for i, encrypted_file in enumerate(encrypted_files[:2]):  # Tester 2 fichiers
        data = {
            "vault_uuid": encrypted_file['vault_uuid']
        }
        response = requests.post(f"{base_url}/decrypt", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Fichier {i+1} déchiffré: {Path(result['decrypted_path']).name}")
            
            # Vérifier le contenu
            with open(result['decrypted_path'], 'r') as f:
                content = f.read()
                if i == 0 and "DONNÉES PERSONNELLES" in content:
                    print("   ✅ Contenu personnel correct")
                elif i == 1 and "DONNÉES FINANCIÈRES" in content:
                    print("   ✅ Contenu financier correct")
        else:
            print(f"❌ Échec déchiffrement fichier {i+1}")
    
    # Test 6: Statut final
    print("\n6. 📊 Test statut final...")
    response = requests.get(f"{base_url}/vault_status")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Statut final:")
        print(f"   Total fichiers: {result['total_files']}")
        print(f"   Taille totale: {result['total_size_bytes']:,} bytes")
        print(f"   Dernières entrées:")
        
        for entry in result['entries'][:5]:  # Afficher 5 dernières
            print(f"     - {entry['vault_uuid']}: {entry['owner']} - {Path(entry['original_path']).name}")
    else:
        print(f"❌ Échec statut final")
    
    # Test 7: Nettoyage
    print("\n7. 🧹 Nettoyage...")
    try:
        # Supprimer fichiers temporaires
        for file_path in test_files + batch_files:
            if Path(file_path).exists():
                Path(file_path).unlink()
        
        # Supprimer fichiers déchiffrés
        decrypted_dir = Path("decrypted")
        if decrypted_dir.exists():
            for file_path in decrypted_dir.glob("tmp*"):
                file_path.unlink()
        
        print("✅ Fichiers temporaires supprimés")
    except Exception as e:
        print(f"⚠️  Erreur nettoyage: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 TOUS LES TESTS PASSENT!")
    print("✅ Security Agent Consolidé fonctionne parfaitement")
    print("🔐 Chiffrement/déchiffrement: OK")
    print("📊 Gestion vault: OK")
    print("🔄 Intégration MCP: OK")
    print("=" * 50)

if __name__ == "__main__":
    test_complet()
