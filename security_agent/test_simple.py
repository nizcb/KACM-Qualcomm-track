#!/usr/bin/env python3
"""
Test Simple - Security Agent Consolidé
"""

import requests
import tempfile
import json
from pathlib import Path

def test_simple():
    print("🔐 Test Simple du Security Agent")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:8001"
    
    # Test 1: Santé
    print("\n1. Test santé...")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Agent en bonne santé")
    else:
        print("❌ Agent en panne")
        return
    
    # Test 2: Créer un fichier
    print("\n2. Création fichier test...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Document test sensible\nNuméro: 123-456-789")
        test_file = f.name
    print(f"Fichier créé: {test_file}")
    
    # Test 3: Chiffrement
    print("\n3. Test chiffrement...")
    data = {
        "file_path": test_file,
        "owner": "test_user"
    }
    response = requests.post(f"{base_url}/encrypt", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Chiffrement réussi")
        print(f"UUID: {result['vault_uuid']}")
        vault_uuid = result['vault_uuid']
    else:
        print("❌ Chiffrement échoué")
        print(response.text)
        return
    
    # Test 4: Déchiffrement
    print("\n4. Test déchiffrement...")
    data = {
        "vault_uuid": vault_uuid
    }
    response = requests.post(f"{base_url}/decrypt", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Déchiffrement réussi")
        print(f"Fichier: {result['decrypted_path']}")
        
        # Vérifier le contenu
        with open(result['decrypted_path'], 'r') as f:
            content = f.read()
            if "Document test sensible" in content:
                print("✅ Contenu correct")
            else:
                print("❌ Contenu incorrect")
    else:
        print("❌ Déchiffrement échoué")
        print(response.text)
        return
    
    # Test 5: Statut
    print("\n5. Test statut...")
    response = requests.get(f"{base_url}/vault_status")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Statut récupéré")
        print(f"Fichiers: {result['total_files']}")
    else:
        print("❌ Statut échoué")
    
    # Nettoyage
    print("\n6. Nettoyage...")
    Path(test_file).unlink()
    print("✅ Fichier temporaire supprimé")
    
    print("\n🎉 TOUS LES TESTS PASSENT!")

if __name__ == "__main__":
    test_simple()
