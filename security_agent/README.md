# Agent de Sécurité - Security Agent

## Description
Agent de sécurité intelligent pour le chiffrement, déchiffrement et gestion sécurisée des fichiers avec interface web Streamlit.

## Architecture
- **Agent Principal** : `security_agent_consolidated.py` (FastAPI)
- **Interface Web** : `streamlit_interface.py` (Streamlit)
- **Stockage Sécurisé** : Base de données SQLite + Vault
- **Chiffrement** : AES-256 avec gestion des clés

## Installation

### 1. Installer les dépendances
```bash
pip install -r requirements_consolidated.txt
```

### 2. Vérifier l'installation
```bash
python3 -c "import fastapi, streamlit, pyAesCrypt; print('✅ Toutes les dépendances sont installées')"
```

## Utilisation

### Méthode 1 : Démarrage automatique
```bash
python3 start_application.py
```

### Méthode 2 : Démarrage manuel
**Terminal 1 - Agent de sécurité :**
```bash
python3 security_agent_consolidated.py
```

**Terminal 2 - Interface web :**
```bash
python3 -m streamlit run streamlit_interface.py --server.port 8501
```

## Accès aux applications

- **Agent API** : http://localhost:8000
- **Interface Web** : http://localhost:8501
- **Documentation API** : http://localhost:8000/docs

## Fonctionnalités

### Agent de Sécurité (API)
- ✅ Chiffrement de fichiers (AES-256)
- ✅ Déchiffrement sécurisé
- ✅ Gestion des clés avec keyring
- ✅ Base de données SQLite pour métadonnées
- ✅ API RESTful avec FastAPI
- ✅ Logs et monitoring

### Interface Web (Streamlit)
- ✅ Upload de fichiers
- ✅ Chiffrement en temps réel
- ✅ Gestion des fichiers chiffrés
- ✅ Déchiffrement et téléchargement
- ✅ Statistiques et monitoring
- ✅ Interface intuitive

## Structure des dossiers

```
security_agent/
├── security_agent_consolidated.py  # Agent principal
├── streamlit_interface.py          # Interface web
├── requirements_consolidated.txt   # Dépendances
├── README.md                       # Documentation
├── .gitignore                      # Fichiers ignorés
├── vault/                          # Base de données
│   └── vault.db                    # Métadonnées SQLite
├── encrypted/                      # Fichiers chiffrés
│   └── *.aes                       # Fichiers AES
└── decrypted/                      # Fichiers déchiffrés temporaires
    └── *.txt                       # Fichiers temporaires
```

## Dépannage

### Problèmes courants

**1. Port déjà utilisé**
```bash
# Vérifier les ports
lsof -i :8000  # Agent
lsof -i :8501  # Streamlit

# Arrêter les processus
kill -9 <PID>
```

**2. Dépendances manquantes**
```bash
# Réinstaller les dépendances
pip install --upgrade -r requirements_consolidated.txt
```

**3. Erreur de permissions**
```bash
# Vérifier les permissions des dossiers
chmod 755 vault/ encrypted/ decrypted/
```

## Version
Version consolidée - Toutes les fonctionnalités dans des fichiers unifiés pour faciliter le déploiement et la maintenance.
- **Vault SQLite** pour métadonnées et traçabilité
- **API HTTP complète** avec FastAPI
- **Interface MCP** pour l'orchestrateur
- **Interface web Streamlit** pour tests et monitoring
- **Gestion sécurisée des clés** via macOS Keychain

## 📡 API Endpoints

- `POST /encrypt` - Chiffrer un fichier
- `POST /decrypt` - Déchiffrer un fichier  
- `GET /vault_status` - Statut du vault
- `GET /health` - Santé de l'agent
- `POST /mcp/task` - Interface MCP pour orchestrateur

## 🔄 Workflow

1. File Manager détecte fichiers sensibles
2. Envoi MCP vers Security Agent
3. Chiffrement AES-256 avec salt unique
4. Stockage vault avec métadonnées
5. Réponse MCP avec UUID et hash

---

**Architecture**: Vision/NLP → File Manager → Security Agent (chiffrement + vault)
- **Vault SQLite** : Base de données pour métadonnées et traçabilité
- **API HTTP** : Endpoints pour chiffrement/déchiffrement ad-hoc
- **Intégration MCP** : Traitement par lots depuis le File Manager

## 🚀 Démarrage rapide

### Installation

```bash
# Clone le repository
cd security_agent

# Installation des dépendances
python3 -m pip install -r requirements.txt

# Configuration de l'environnement
python3 start_agent.py --setup-only
```

### Lancement

```bash
# Mode production
python3 start_agent.py

# Mode développement avec auto-reload
python3 start_agent.py --reload

# Installation + tests + démarrage
python3 start_agent.py --install --test
```

### Démonstration

```bash
# Lancer la démo complète
python3 start_agent.py --demo

# Ou directement
python3 demo_mvp.py
```

## 🔐 Fonctionnalités

### 1. API HTTP (FastAPI)

#### Chiffrement de fichier
```bash
curl -X POST "http://127.0.0.1:8001/encrypt" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/sensitive.pdf",
    "owner": "user123",
    "policy": "AES256"
  }'
```

#### Déchiffrement de fichier
```bash
curl -X POST "http://127.0.0.1:8001/decrypt" \
  -H "Content-Type: application/json" \
  -d '{
    "vault_uuid": "abc123",
    "output_path": "/path/to/decrypted.pdf"
  }'
```

#### Statut du vault
```bash
curl "http://127.0.0.1:8001/vault_status"
```

### 2. Intégration MCP

#### Message d'entrée (File Manager)
```json
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
```

#### Message de sortie (Security Agent)
```json
{
  "thread_id": "batch-42",
  "sender": "security_agent",
  "type": "result.security",
  "payload": {
    "vault": [
      {
        "orig": "/path/to/sensitive.pdf",
        "vault_path": "/vault/3d8bbf.aes",
        "hash": "SHA256:ab12...",
        "uuid": "3d8bbf",
        "timestamp": "2025-01-07T14:33:02Z"
      }
    ],
    "processed": 1,
    "total_requested": 2
  }
}
```

### 3. Sécurité

- **Chiffrement AES-256** avec pyAesCrypt
- **Clé maître** stockée dans macOS Keychain
- **Salt unique** par fichier
- **Hachage SHA-256** pour intégrité
- **Métadonnées** en base SQLite chiffrée

## 🏗️ Architecture technique

### Structure des modules

```
security_agent/
├── main.py          # FastAPI app + MCP consumer
├── config.py        # Configuration et variables d'environnement
├── models.py        # Schémas Pydantic (MCP, API, DB)
├── crypto.py        # Chiffrement/déchiffrement AES-256
├── vault.py         # Gestion base SQLite et keyring
├── test_mvp.py      # Tests unitaires
├── demo_mvp.py      # Démonstration complète
├── start_agent.py   # Script de démarrage
└── requirements.txt # Dépendances
```

### Workflow de chiffrement

1. **Réception** : Fichier sensible identifié par Vision/NLP
2. **UUID** : Génération d'un identifiant unique
3. **Chiffrement** : AES-256 avec pyAesCrypt
4. **Stockage** : Fichier chiffré dans vault/
5. **Métadonnées** : Enregistrement en base SQLite
6. **Traçabilité** : Hash SHA-256 pour intégrité

### Base de données

```sql
CREATE TABLE vault_entries (
    id INTEGER PRIMARY KEY,
    vault_uuid TEXT UNIQUE,
    original_path TEXT,
    vault_path TEXT,
    file_hash TEXT,
    owner TEXT,
    policy TEXT,
    created_at TIMESTAMP,
    accessed_at TIMESTAMP
);
```

## 🧪 Tests

### Exécution des tests

```bash
# Tests unitaires
python3 -m pytest test_mvp.py -v

# Tests avec couverture
python3 -m pytest test_mvp.py --cov=. --cov-report=html

# Tests via script de démarrage
python3 start_agent.py --test
```

### Scénarios testés

- Chiffrement/déchiffrement de fichiers
- Intégrité du contenu
- Gestion des erreurs
- Validation des modèles Pydantic
- Workflow MCP complet
- Opérations vault (SQLite)

## 📊 Monitoring

### Santé de l'agent

```bash
curl "http://127.0.0.1:8001/health"
```

### Métriques vault

```bash
curl "http://127.0.0.1:8001/vault_status"
```

### Logs

Les logs sont configurés au niveau INFO avec format structuré :
- Succès de chiffrement/déchiffrement
- Erreurs et exceptions
- Opérations MCP
- Statut des requêtes HTTP

## 🔄 Intégration

### Avec File Manager

Le Security Agent écoute les messages MCP de type `task.security` et répond avec `result.security`.

### Avec autres agents

- **Vision Agent** : Détection de contenu sensible dans images
- **NLP Agent** : Détection de PII dans texte
- **File Manager** : Orchestration et batch processing

### Configuration MCP

```json
{
  "agent_id": "security_agent",
  "capabilities": ["encryption", "vault_management"],
  "message_types": ["task.security"],
  "response_types": ["result.security"]
}
```

## 🚀 Déploiement

### Environnement de production

```bash
# Variables d'environnement
export SECURITY_AGENT_VAULT_PATH="/secure/vault"
export SECURITY_AGENT_HOST="0.0.0.0"
export SECURITY_AGENT_PORT="8001"

# Démarrage
python3 start_agent.py --host 0.0.0.0 --port 8001
```

### Docker (optionnel)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python3", "start_agent.py"]
```

## 📝 Limitations actuelles

- Pas de rotation automatique des clés
- Pas de sauvegarde distribuée du vault
- Interface MCP simplifiée (pas de Redis/RabbitMQ)
- Pas de chiffrement des métadonnées en base

## 🔮 Évolutions futures

- Intégration Redis pour MCP
- Rotation automatique des clés
- Sauvegarde chiffrée du vault
- Support multi-tenant
- Audit trail complet
- Interface web d'administration

## 🤝 Contribution

1. Fork le repository
2. Créer une branche feature
3. Ajouter des tests pour les nouvelles fonctionnalités
4. Lancer `python3 start_agent.py --test`
5. Créer une pull request

## 📄 Licence

MIT License - voir LICENSE pour détails.
```

### **2. Structure générée automatiquement**
```
security_agent/
├─ agent.py              # Point d'entrée principal
├─ encryption.py         # Chiffrement AES-256-CBC
├─ pii.py               # Détection PII (spaCy + regex)
├─ register_tools.py    # Enregistrement manuel
├─ launcher.py          # Script de lancement avec vérifications
├─ demo.py              # Démonstration complète
├─ test_agent_tools.py  # Tests unitaires
├─ requirements.txt     # Dépendances Python
├─ vault/
│  └─ master.key        # Clé maître (générée auto)
├─ encrypted/           # Fichiers chiffrés (.aes)
└─ decrypted/          # Fichiers déchiffrés
```

---

## 🚀 **Démarrage rapide**

### **Option 1: Launcher (recommandé)**
```bash
# Vérifications + démonstration
python launcher.py --demo

# Vérifications uniquement
python launcher.py --check

# Lancement de l'agent en mode production
python launcher.py --start

# Tests complets
python launcher.py --test

# Enregistrement manuel des tools
python launcher.py --register
```

### **Option 2: Commandes directes**
```bash
# Mode démo
python demo.py

# Mode production
python agent.py

# Tests
python test_agent_tools.py

# Enregistrement manuel
python register_tools.py
```

---

## 📋 **Utilisation**

### **Démarrage automatique (recommandé)**
```bash
python agent.py
```

**Workflow automatique :**
1. ✅ Génération de la clé maître si absente
2. ✅ Auto-registration sur `http://localhost:5555/register`
3. ✅ Écoute SSE sur `/stream?agent=security_agent`
4. ✅ Traitement des threads et réponses automatiques

### **Enregistrement manuel (fallback)**
```bash
# Si l'auto-registration échoue
python register_tools.py
python register_tools.py http://localhost:5555 --test
```

---

## 🔧 **Configuration**

### **Variables d'environnement**
```bash
export CORAL_URL="http://localhost:5555"  # Serveur Coral MCP
export SECURITY_VAULT_DIR="./vault"       # Dossier vault
export SECURITY_LOG_LEVEL="INFO"          # Niveau de log
```

### **Clé maître**
- **Générée automatiquement** au premier démarrage
- **Stockée dans** `./vault/master.key` (permissions 0600)
- **Format:** AES-256-CBC, clé de 256 bits
- **Sauvegarde recommandée** pour récupération

---

## 📊 **Exemples d'utilisation**

### **Via Coral MCP (production)**
```json
{
  "thread_id": "thread_123",
  "tool_call": {
    "name": "encrypt_file",
    "arguments": {
      "filepath": "./documents/secret.pdf"
    }
  }
}
```

### **Test direct (développement)**
```python
from encryption import EncryptionManager
from pii import PIIDetector

# Chiffrement
em = EncryptionManager()
result = em.encrypt_file("./test.txt")
print(result["encrypted_file"])

# Détection PII
detector = PIIDetector()
result = detector.scan_pii("Mon email est jean@example.com", "fr")
print(result["contains_pii"])  # True
```

---

## 🧪 **Tests**

### **Test des composants**
```bash
# Test chiffrement
python encryption.py

# Test détection PII
python pii.py

# Test complet agent
python agent.py
```

### **Test avec fichiers réels**
```bash
# Créer un fichier test
echo "Secret: jean.dupont@example.com" > test.txt

# Chiffrer
python -c "
from encryption import EncryptionManager
em = EncryptionManager()
result = em.encrypt_file('test.txt')
print('Chiffré:', result['encrypted_file'])
"

# Scanner PII
python -c "
from pii import PIIDetector
detector = PIIDetector()
with open('test.txt', 'r') as f:
    result = detector.scan_pii(f.read(), 'fr')
print('PII détectées:', result['found'])
"
```

---

## 🔒 **Sécurité**

### **Chiffrement**
- **Algorithme :** AES-256-CBC (pyAesCrypt)
- **Clé :** 256 bits générée par `secrets.token_urlsafe(32)`
- **Stockage :** Keyring système + fichier vault sécurisé
- **Performance :** Buffer 64KB optimisé ARM64

### **Détection PII**
- **Méthodes :** spaCy NLP + regex patterns
- **Fallback :** regex uniquement si spaCy indisponible
- **Types :** email, téléphone, SSN, CB, IBAN, noms, lieux
- **Langues :** français, anglais (extensible)

---

## 🌟 **Architecture Coral MCP**

### **Flux de données**
```
Tauri UI → FastAPI → Coral MCP → Security Agent
                ↑                      ↓
            Stream SSE ←─── Tool Response
```

### **Messages MCP**
```json
// Requête
{
  "thread_id": "unique_id",
  "tool_call": {
    "name": "encrypt_file",
    "arguments": {"filepath": "/path/file.txt"}
  }
}

// Réponse
{
  "agent": "security_agent",
  "result": {
    "encrypted_file": "/path/file.aes",
    "success": true
  },
  "timestamp": 1234567890
}
```

---

## 📈 **Performance Snapdragon X Elite**

### **Optimisations ARM64**
- ✅ Buffer 64KB pour I/O fichiers
- ✅ spaCy models optimisés ARM64
- ✅ regex compilées pour patterns PII
- ✅ JSON streaming pour gros volumes
- ✅ Async/await pour concurrence

### **Benchmarks estimés**
- **Chiffrement :** ~50MB/s (AES-256)
- **Détection PII :** ~1000 mots/s (spaCy)
- **Regex PII :** ~10000 mots/s (fallback)
- **Memory :** <100MB RAM total

---

## 🐛 **Troubleshooting**

### **Erreurs communes**

1. **"spaCy models not found"**
   ```bash
   python -m spacy download fr_core_news_sm
   python -m spacy download en_core_web_sm
   ```

2. **"Coral registration failed"**
   ```bash
   # Vérifier que Coral MCP server tourne
   curl http://localhost:5555/health
   
   # Enregistrement manuel
   python register_tools.py
   ```

3. **"Permission denied vault/master.key"**
   ```bash
   chmod 600 vault/master.key
   chown $USER vault/master.key
   ```

### **Logs de debug**
```bash
# Logs JSON détaillés
python agent.py 2>&1 | jq .

# Filtrer par événements
python agent.py 2>&1 | jq 'select(.event == "tool_executed")'
```

---

## 🏆 **Hackathon Ready!**

✅ **100% Offline** - Aucune dépendance cloud  
✅ **ARM64 Native** - Optimisé Snapdragon X Elite  
✅ **Coral MCP** - Intégration seamless  
✅ **Production Ready** - Gestion d'erreurs complète  
✅ **Extensible** - Nouveaux tools facilement ajoutables  

---

## 📝 **License**

MIT License - Hackathon RAISE Your Hack track Qualcomm 2025

**Équipe :** Neurosort Security Agent  
**Platform :** Snapdragon X Elite ARM64  
**Stack :** Python + Coral MCP + Tauri
