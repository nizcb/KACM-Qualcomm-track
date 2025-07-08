# 🤖 Système Multi-Agents MCP Réel - KACM Qualcomm Track

## 🎯 Vue d'ensemble

Ce projet implémente un **système multi-agents réel** utilisant le **Model Context Protocol (MCP)** pour l'analyse automatique et la sécurisation de fichiers. Le système est conçu pour détecter les informations personnelles identifiables (PII) et sécuriser automatiquement les fichiers sensibles.

### ✨ Fonctionnalités Principales

- 🤖 **6 Agents Spécialisés** : Orchestrateur, NLP, Vision, Audio, File Manager, Security
- 🧠 **Intégration Ollama/Llama 3.2:1b** : Analyse IA réelle des contenus
- 🔐 **Sécurisation Automatique** : Chiffrement des fichiers sensibles détectés
- 📋 **Protocol MCP Natif** : Communication inter-agents standardisée
- 🎯 **Interface Interactive** : Test et validation en temps réel
- 📊 **Rapports Détaillés** : Consolidation et recommandations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    🎯 ORCHESTRATEUR                         │
│                      (Port 8001)                           │
│   • Scan et classification des fichiers                    │
│   • Distribution vers agents spécialisés                   │
│   • Consolidation des résultats                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
     ┌────────────┼────────────┬───────────────┐
     │            │            │               │
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐
│ 🤖 NLP  │  │ 👁️ VISION│  │ 🔊 AUDIO│  │ 📊 MANAGER  │
│Port 8002│  │Port 8003│  │Port 8004│  │  Port 8005  │
│         │  │         │  │         │  │             │
│•Texte   │  │•Images  │  │•Audio   │  │•Consolidation│
│•PDF     │  │•OCR     │  │•Speech  │  │•Statistiques│
│•JSON    │  │•Objets  │  │•Analyse │  │•Recommandations│
│•PII     │  │•Documents│ │•PII     │  │•Rapports    │
└─────────┘  └─────────┘  └─────────┘  └─────────────┘
                  │
            ┌─────────────┐
            │ 🔐 SECURITY │
            │  Port 8006  │
            │             │
            │ • Chiffrement│
            │ • Vault     │
            │ • Audit     │
            └─────────────┘
```

## 🚀 Installation et Configuration

### Prérequis

- Python 3.9+
- Ollama avec Llama 3.2:1b
- Git

### Installation Rapide

```bash
# 1. Cloner le projet
git clone <repository-url>
cd real_mcp_system

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer Ollama (si pas déjà fait)
# Installer Ollama : https://ollama.ai/download
ollama pull llama3.2:1b

# 5. Vérifier l'installation
ollama list
```

### Structure du Projet

```
real_mcp_system/
├── 📁 agents/                  # Scripts des agents MCP
│   ├── agent_orchestrator_mcp.py
│   ├── agent_nlp_mcp.py
│   ├── agent_vision_mcp.py
│   ├── agent_audio_mcp.py
│   ├── agent_file_manager_mcp.py
│   └── agent_security_mcp.py
├── 📁 data/test_files/         # Fichiers de test
│   ├── document_pii.txt        # Fichier avec PII
│   ├── document_normal.txt     # Fichier normal
│   ├── clients_data.json       # Données JSON sensibles
│   └── ...                     # Autres fichiers d'exemple
├── 📁 logs/                    # Journaux du système
├── 📁 vault/                   # Fichiers chiffrés
├── config.py                   # Configuration centralisée
├── system_manager.py          # Gestionnaire du système
├── test_interface.py          # Interface de test de base
├── interactive_interface.py   # Interface interactive complète
└── requirements.txt           # Dépendances Python
```

## 🎮 Utilisation

### 1. Démarrage du Système

```bash
# Démarrer tous les agents
python system_manager.py start

# Vérifier la santé (optionnel, pour debug)
python system_manager.py health

# Arrêter le système
python system_manager.py stop
```

### 2. Tests et Validation

#### Test Automatique du Workflow
```bash
# Test complet avec tous les fichiers d'exemple
python test_interface.py --workflow
```

#### Interface Interactive Complète
```bash
# Lancer l'interface interactive avec Ollama
python interactive_interface.py
```

L'interface interactive propose :
- 🧪 Test d'un fichier spécifique avec Llama
- 📁 Analyse complète du répertoire
- 🎭 Simulation du workflow complet
- 📋 Statut des agents et système

### 3. Test Manuel d'un Agent

```bash
# Test direct de l'agent NLP
cd agents/
python agent_nlp_mcp.py

# Dans un autre terminal :
# Utiliser un client MCP pour se connecter
```

## 📊 Workflow de Traitement

### Étape 1 : Scan et Classification
```
📁 Répertoire source → 🎯 Orchestrateur
├── Fichiers texte (.txt, .json, .csv, .md) → 🤖 Agent NLP
├── Fichiers image (.jpg, .png, .gif) → 👁️ Agent Vision  
└── Fichiers audio (.mp3, .wav, .m4a) → 🔊 Agent Audio
```

### Étape 2 : Analyse Spécialisée
```
🤖 Agent NLP + 🧠 Ollama/Llama 3.2:1b
├── Détection PII (emails, téléphones, SSN, etc.)
├── Analyse sémantique du contenu
├── Classification de sensibilité
└── Résumé automatique

👁️ Agent Vision
├── Analyse d'images et documents
├── OCR et reconnaissance de texte
├── Détection de documents officiels
└── Classification visuelle

🔊 Agent Audio  
├── Analyse des caractéristiques audio
├── Transcription (simulée)
├── Détection de contenu sensible
└── Classification audio
```

### Étape 3 : Consolidation et Sécurisation
```
📊 File Manager
├── Collecte tous les résultats
├── Génération de statistiques
├── Création de recommandations
└── Rapport consolidé

🔐 Security Agent (si PII détectée)
├── Chiffrement AES des fichiers sensibles
├── Stockage sécurisé dans vault/
├── Génération de clés
└── Audit et logging
```

## 🧪 Exemples de Fichiers de Test

Le système inclut des fichiers d'exemple pour tester toutes les fonctionnalités :

### Fichiers avec PII (détectés comme sensibles)
- `document_pii.txt` - Rapport médical avec SSN, téléphone, email
- `confidential_memo.txt` - Mémo interne avec salaires et données RH
- `clients_data.json` - Base clients avec informations personnelles
- `carte_identite.jpg.txt` - Simulation de document d'identité

### Fichiers normaux (sûrs)
- `document_normal.txt` - Rapport technique sans PII
- `programming_tips.txt` - Conseils de programmation
- `installation_guide.md` - Guide d'installation
- `paysage.jpg.txt` - Simulation d'image de paysage

## 🔧 Configuration Avancée

### Variables d'Environnement

```bash
# Ollama
export OLLAMA_BASE_URL=http://localhost:11434
export LLAMA_MODEL=llama3.2:1b

# Ports des agents
export ORCHESTRATOR_PORT=8001
export NLP_PORT=8002
export VISION_PORT=8003
export AUDIO_PORT=8004
export FILE_MANAGER_PORT=8005
export SECURITY_PORT=8006

# Sécurité
export VAULT_PASSWORD=your_secure_password
export LOG_LEVEL=INFO
```

### Configuration des Agents

Modifier `config.py` pour personnaliser :
- Ports et endpoints
- Extensions de fichiers supportées  
- Paramètres de sécurité
- Configuration Ollama

## 🐛 Dépannage

### Problèmes Courants

**Agents ne démarrent pas**
```bash
# Vérifier les ports
python system_manager.py health

# Redémarrer le système
python system_manager.py stop
python system_manager.py start
```

**Ollama non disponible**
```bash
# Vérifier Ollama
ollama list
curl http://localhost:11434/api/tags

# Redémarrer Ollama si nécessaire
ollama serve
```

**Erreurs de dépendances**
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

## 🚀 Développement et Extension

### Ajouter un Nouvel Agent

1. Créer `agents/agent_nouveau_mcp.py`
2. Implémenter l'interface MCP avec `@mcp.tool()`
3. Ajouter la configuration dans `config.py`
4. Mettre à jour `system_manager.py`

### Intégrer un Nouveau Type de Fichier

1. Modifier la classification dans l'orchestrateur
2. Étendre l'agent approprié
3. Ajouter les extensions dans `config.py`
4. Créer des fichiers de test

## 📋 Résultats d'Exemple

```
======================================================================
📋 RAPPORT FINAL DU WORKFLOW
======================================================================

📊 Statistiques:
  • Total fichiers traités: 10
  • Fichiers avec warnings: 4
  • Fichiers sécurisés: 4

🤖 Traitement par agent:
  • Agent NLP: 8 fichiers
  • Agent Vision: 1 fichier
  • Agent Audio: 1 fichier

🔐 Actions de sécurité:
  ✅ document_pii.txt → Chiffré
  ✅ confidential_memo.txt → Chiffré
  ✅ clients_data.json → Chiffré
  ✅ carte_identite.jpg → Chiffré

💡 Recommandations:
  • Chiffrer les fichiers sensibles détectés
  • Revoir les permissions d'accès
  • Effectuer un audit de sécurité

🎉 Workflow de test terminé avec succès!
======================================================================
```

## 🤝 Contribution

Ce projet fait partie du **KACM Qualcomm Track** et démontre l'utilisation pratique du protocole MCP avec de l'IA réelle pour la sécurisation de données.

### Technologies Utilisées

- **Protocol MCP** : Communication inter-agents standardisée
- **Ollama/Llama 3.2:1b** : Intelligence artificielle locale
- **FastAPI** : APIs REST pour les agents
- **SQLite** : Persistance des données
- **Cryptography** : Chiffrement AES des fichiers sensibles
- **Pydantic** : Validation et sérialisation des données

---

🎯 **Prêt à tester le système ?** Lancez `python interactive_interface.py` et explorez toutes les fonctionnalités !

✨ **Questions ?** Consultez les logs dans `logs/` ou utilisez l'interface de debug.
