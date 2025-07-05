# Cross-Platform Setup Instructions

## Configuration Cross-Platform

### Windows
```bash
# PowerShell
$env:NEUROSORT_MASTER_PWD = "your-secure-master-password"
$env:SECURITY_AGENT_VAULT_PATH = "C:\Security\vault"
$env:SECURITY_AGENT_ENCRYPTED_PATH = "C:\Security\encrypted"
$env:SECURITY_AGENT_DECRYPTED_PATH = "C:\Security\decrypted"

# Installer les dépendances
pip install -r requirements_consolidated.txt

# Démarrer l'agent
python security_agent_consolidated.py
```

### macOS
```bash
# Terminal
export NEUROSORT_MASTER_PWD="your-secure-master-password"
export SECURITY_AGENT_VAULT_PATH="/Users/$USER/Security/vault"
export SECURITY_AGENT_ENCRYPTED_PATH="/Users/$USER/Security/encrypted"
export SECURITY_AGENT_DECRYPTED_PATH="/Users/$USER/Security/decrypted"

# Installer les dépendances
pip3 install -r requirements_consolidated.txt

# Démarrer l'agent
python3 security_agent_consolidated.py
```

### Linux
```bash
# Terminal
export NEUROSORT_MASTER_PWD="your-secure-master-password"
export SECURITY_AGENT_VAULT_PATH="/home/$USER/Security/vault"
export SECURITY_AGENT_ENCRYPTED_PATH="/home/$USER/Security/encrypted"
export SECURITY_AGENT_DECRYPTED_PATH="/home/$USER/Security/decrypted"

# Installer les dépendances système pour keyring (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-keyring gnome-keyring

# Ou pour CentOS/RHEL
sudo yum install python3-keyring

# Installer les dépendances Python
pip3 install -r requirements_consolidated.txt

# Démarrer l'agent
python3 security_agent_consolidated.py
```

## Compatibilité Keyring

### Windows
- Utilise Windows Credential Store automatiquement
- Pas de configuration supplémentaire nécessaire

### macOS
- Utilise le Keychain macOS automatiquement
- Pas de configuration supplémentaire nécessaire

### Linux
- Peut nécessiter l'installation de `python3-keyring`
- Dépend du gestionnaire de mots de passe installé :
  - GNOME Keyring (Ubuntu/Debian)
  - KDE Wallet (KDE)
  - Ou fallback vers variable d'environnement

## Fallback Mode

Si keyring n'est pas disponible, l'agent utilise :
1. Variable d'environnement `NEUROSORT_MASTER_PWD`
2. Génération automatique avec affichage du mot de passe

## Scripts de Démarrage Cross-Platform

### Windows (start_windows.bat)
```batch
@echo off
echo Starting Security Agent on Windows...
set NEUROSORT_MASTER_PWD=your-secure-password
python security_agent_consolidated.py
```

### macOS/Linux (start_unix.sh)
```bash
#!/bin/bash
echo "Starting Security Agent on Unix..."
export NEUROSORT_MASTER_PWD="your-secure-password"
python3 security_agent_consolidated.py
```

## Tests Cross-Platform

### Test de compatibilité
```python
import platform
import keyring
import sqlite3
from pathlib import Path

def test_cross_platform():
    print(f"OS: {platform.system()}")
    print(f"Python: {platform.python_version()}")
    
    # Test keyring
    try:
        keyring.set_password("test", "test", "test")
        keyring.get_password("test", "test")
        print("✅ Keyring: OK")
    except Exception as e:
        print(f"⚠️ Keyring: {e}")
    
    # Test SQLite
    try:
        conn = sqlite3.connect(":memory:")
        conn.close()
        print("✅ SQLite: OK")
    except Exception as e:
        print(f"❌ SQLite: {e}")
    
    # Test Path
    try:
        test_path = Path("test_dir")
        test_path.mkdir(exist_ok=True)
        test_path.rmdir()
        print("✅ Path operations: OK")
    except Exception as e:
        print(f"❌ Path operations: {e}")

if __name__ == "__main__":
    test_cross_platform()
```
