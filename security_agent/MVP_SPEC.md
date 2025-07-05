# Security Agent - MVP Spécification

**Agent de sécurité spécialisé dans le chiffrement et la gestion de vault**

## 🎯 Architecture mise à jour

```
Vision Agent ──┐
                ├── détection sensible ──> File Manager ──> Security Agent
NLP Agent ────┘                                              (chiffrement + vault)
```

### Responsabilités
- **Vision/NLP** : Détection du contenu sensible
- **File Manager** : Orchestration, liste des fichiers à sécuriser  
- **Security Agent** : Chiffrement AES-256, gestion vault, métadonnées

## 🔐 Fonctionnalités Security Agent

### 1. **Interface MCP principale**
```json
// Entrée du File Manager
{
  "thread_id": "batch-42",
  "sender": "file_manager", 
  "type": "task.security",
  "payload": {
    "files": ["/path/to/sensitive.pdf", "/path/to/doc.jpg"],
    "owner": "nizar",
    "policy": "AES256"
  }
}

// Sortie vers orchestrateur
{
  "thread_id": "batch-42",
  "sender": "security_agent",
  "type": "result.security", 
  "payload": {
    "vault": [
      {
        "orig": "/path/to/sensitive.pdf",
        "vault_path": "/Users/nizar/NeurosortVault/3d8bbf.enc",
        "hash": "SHA256:ab12...",
        "uuid": "3d8bbf", 
        "timestamp": "2025-07-05T14:33:02Z"
      }
    ]
  }
}
```

### 2. **API HTTP locale (FastAPI)**
- `POST /encrypt` : Chiffrement ad-hoc
- `POST /decrypt` : Déchiffrement avec UUID + password  
- `GET /vault_status` : Inventaire vault.db

### 3. **Gestion des clés**
- **Clé maître** stockée dans macOS Keychain (keyring)
- **Salt unique** par fichier
- **AES-256-GCM** avec pyAesCrypt
- **Base SQLite** pour métadonnées

## 🏗️ Structure du projet

```
security_agent/
├─ main.py          # FastAPI + consumer MCP
├─ crypto.py        # encrypt_file / decrypt_file  
├─ vault.py         # init_vault_dir, register_db, get_entry
├─ config.py        # variables d'env, chemins
├─ models.py        # Pydantic schemas
├─ requirements.txt # dépendances
└─ tests/           # tests unitaires
```

## 🚀 Implémentation

Prêt à implémenter cette nouvelle architecture ?
