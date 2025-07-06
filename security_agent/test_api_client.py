#!/usr/bin/env python3
"""
Client de test pour Security Agent API
Démontre l'utilisation des API REST
"""

import requests
import json
import time

API_BASE = "http://localhost:8080"

def test_api():
    """Test complet de l'API Security Agent"""
    
    print("🧪 Test de l'API Security Agent")
    print("=" * 50)
    
    # 1. Vérifier l'état de santé
    print("1️⃣ Vérification de l'état de santé...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ API accessible - Ollama: {health['ollama_running']}")
        else:
            print(f"   ❌ API non accessible: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        return
    
    # 2. Analyser un fichier
    print("\n2️⃣ Analyse IA d'un fichier...")
    analyze_data = {
        "file_path": "test_file.txt",
        "mode": "security"
    }
    
    try:
        response = requests.post(f"{API_BASE}/analyze", json=analyze_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Analyse terminée")
            print(f"   🔍 Recommandation: {result['security_recommendation']}")
            print(f"   🤖 IA: {result['ai_reasoning'][:100]}...")
        else:
            print(f"   ❌ Erreur analyse: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur requête: {e}")
    
    # 3. Chiffrer le fichier si nécessaire
    print("\n3️⃣ Chiffrement du fichier...")
    encrypt_data = {
        "file_path": "test_file.txt",
        "user_id": "test_user"
    }
    
    vault_uuid = None
    try:
        response = requests.post(f"{API_BASE}/encrypt", json=encrypt_data)
        if response.status_code == 200:
            result = response.json()
            vault_uuid = result['uuid']
            print(f"   ✅ Fichier chiffré")
            print(f"   🔑 UUID: {vault_uuid}")
            print(f"   📁 Nom: {result['filename']}")
        else:
            print(f"   ❌ Erreur chiffrement: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur requête: {e}")
    
    # 4. Statistiques du vault
    print("\n4️⃣ Statistiques du vault...")
    try:
        response = requests.get(f"{API_BASE}/vault/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   📊 Fichiers: {stats['total_files']}")
            print(f"   💾 Taille: {stats['total_size']} bytes")
        else:
            print(f"   ❌ Erreur stats: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur requête: {e}")
    
    # 5. Déchiffrer le fichier
    if vault_uuid:
        print("\n5️⃣ Déchiffrement du fichier...")
        decrypt_data = {
            "vault_uuid": vault_uuid,
            "secret_phrase": "mon_secret_ultra_securise_2024",
            "user_id": "test_user"
        }
        
        try:
            response = requests.post(f"{API_BASE}/decrypt", json=decrypt_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Fichier déchiffré")
                print(f"   📁 Nom: {result['filename']}")
                print(f"   📂 Chemin: {result['decrypted_path']}")
            else:
                print(f"   ❌ Erreur déchiffrement: {response.text}")
        except Exception as e:
            print(f"   ❌ Erreur requête: {e}")
    
    print("\n✅ Test API terminé!")
    print(f"📚 Documentation: {API_BASE}/docs")

if __name__ == "__main__":
    test_api()
