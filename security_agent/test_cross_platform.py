#!/usr/bin/env python3
"""
Script de test de compatibilité cross-platform
Vérifie que tous les composants fonctionnent sur le système actuel
"""

import platform
import sys
import os
from pathlib import Path

def test_cross_platform_compatibility():
    """Test de compatibilité cross-platform pour Security Agent"""
    
    print("🔍 Test de compatibilité cross-platform")
    print("=" * 50)
    
    # Informations système
    print(f"🖥️  OS: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {platform.python_version()}")
    print(f"📁 Répertoire: {Path.cwd()}")
    
    results = []
    
    # Test 1: Modules Python requis
    print("\n1️⃣ Test des modules Python...")
    required_modules = [
        'fastapi', 'uvicorn', 'pydantic', 'pyAesCrypt', 
        'keyring', 'sqlite3', 'pathlib', 'secrets', 'hashlib'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
            results.append(f"✅ Module {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
            results.append(f"❌ Module {module}: {e}")
    
    # Test 2: Keyring
    print("\n2️⃣ Test du keyring...")
    try:
        import keyring
        
        # Test d'écriture/lecture
        test_service = "security_agent_test"
        test_username = "test_user"
        test_password = "test_password_123"
        
        keyring.set_password(test_service, test_username, test_password)
        retrieved = keyring.get_password(test_service, test_username)
        
        if retrieved == test_password:
            print("   ✅ Keyring: lecture/écriture OK")
            results.append("✅ Keyring fonctionnel")
        else:
            print("   ⚠️ Keyring: problème de lecture/écriture")
            results.append("⚠️ Keyring: problème de lecture/écriture")
            
        # Nettoyage
        keyring.delete_password(test_service, test_username)
        
    except Exception as e:
        print(f"   ❌ Keyring: {e}")
        results.append(f"❌ Keyring: {e}")
    
    # Test 3: SQLite
    print("\n3️⃣ Test de SQLite...")
    try:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO test VALUES (1, 'test')")
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchone()
        conn.close()
        
        if result == (1, 'test'):
            print("   ✅ SQLite: OK")
            results.append("✅ SQLite fonctionnel")
        else:
            print("   ❌ SQLite: problème de données")
            results.append("❌ SQLite: problème de données")
            
    except Exception as e:
        print(f"   ❌ SQLite: {e}")
        results.append(f"❌ SQLite: {e}")
    
    # Test 4: Opérations sur fichiers
    print("\n4️⃣ Test des opérations sur fichiers...")
    try:
        test_dir = Path("test_security_agent")
        test_file = test_dir / "test.txt"
        
        # Créer répertoire
        test_dir.mkdir(exist_ok=True)
        
        # Créer fichier
        test_file.write_text("test content")
        
        # Lire fichier
        content = test_file.read_text()
        
        # Nettoyer
        test_file.unlink()
        test_dir.rmdir()
        
        if content == "test content":
            print("   ✅ Opérations fichiers: OK")
            results.append("✅ Opérations fichiers OK")
        else:
            print("   ❌ Opérations fichiers: problème de contenu")
            results.append("❌ Opérations fichiers: problème de contenu")
            
    except Exception as e:
        print(f"   ❌ Opérations fichiers: {e}")
        results.append(f"❌ Opérations fichiers: {e}")
    
    # Test 5: Chiffrement AES
    print("\n5️⃣ Test du chiffrement AES...")
    try:
        import pyAesCrypt
        import tempfile
        import os
        
        # Créer fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content for encryption")
            temp_file_path = temp_file.name
        
        encrypted_path = temp_file_path + ".aes"
        decrypted_path = temp_file_path + ".decrypted"
        password = "test_password_123"
        
        # Chiffrer
        pyAesCrypt.encryptFile(temp_file_path, encrypted_path, password)
        
        # Déchiffrer
        pyAesCrypt.decryptFile(encrypted_path, decrypted_path, password)
        
        # Vérifier
        with open(decrypted_path, 'r') as f:
            decrypted_content = f.read()
        
        # Nettoyer
        os.unlink(temp_file_path)
        os.unlink(encrypted_path)
        os.unlink(decrypted_path)
        
        if decrypted_content == "test content for encryption":
            print("   ✅ Chiffrement AES: OK")
            results.append("✅ Chiffrement AES fonctionnel")
        else:
            print("   ❌ Chiffrement AES: problème de contenu")
            results.append("❌ Chiffrement AES: problème de contenu")
            
    except Exception as e:
        print(f"   ❌ Chiffrement AES: {e}")
        results.append(f"❌ Chiffrement AES: {e}")
    
    # Test 6: Variables d'environnement
    print("\n6️⃣ Test des variables d'environnement...")
    try:
        # Test de lecture
        test_var = os.getenv("PATH")
        if test_var:
            print("   ✅ Variables d'environnement: OK")
            results.append("✅ Variables d'environnement OK")
        else:
            print("   ⚠️ Variables d'environnement: PATH non trouvé")
            results.append("⚠️ Variables d'environnement: PATH non trouvé")
            
    except Exception as e:
        print(f"   ❌ Variables d'environnement: {e}")
        results.append(f"❌ Variables d'environnement: {e}")
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    success_count = sum(1 for r in results if r.startswith("✅"))
    warning_count = sum(1 for r in results if r.startswith("⚠️"))
    error_count = sum(1 for r in results if r.startswith("❌"))
    
    print(f"✅ Succès: {success_count}")
    print(f"⚠️ Avertissements: {warning_count}")
    print(f"❌ Erreurs: {error_count}")
    
    print(f"\n📋 Détails:")
    for result in results:
        print(f"   {result}")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS:")
    if error_count > 0:
        print("   - Installez les modules manquants avec: pip install -r requirements_consolidated.txt")
    if platform.system() == "Linux" and any("keyring" in r for r in results if r.startswith("❌")):
        print("   - Sur Linux, installez: sudo apt-get install python3-keyring gnome-keyring")
    if warning_count > 0:
        print("   - Vérifiez la configuration du système pour les avertissements")
    
    # Conclusion
    compatibility_score = (success_count / len(results)) * 100
    print(f"\n🎯 Score de compatibilité: {compatibility_score:.1f}%")
    
    if compatibility_score >= 90:
        print("🎉 Excellent! Le système est pleinement compatible.")
        return True
    elif compatibility_score >= 75:
        print("👍 Bon! Le système est compatible avec quelques ajustements.")
        return True
    else:
        print("⚠️ Attention! Des problèmes de compatibilité détectés.")
        return False

if __name__ == "__main__":
    success = test_cross_platform_compatibility()
    sys.exit(0 if success else 1)
