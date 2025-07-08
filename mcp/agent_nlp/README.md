# Système Multi-Agents MCP

## Vue d'ensemble

Ce projet implémente un système multi-agents utilisant le **Model Context Protocol (MCP)** pour la communication inter-agents et l'orchestration de workflows. Le système est conçu pour traiter différents types de documents (texte, PDF, audio, etc.) en utilisant des agents spécialisés.

## Architecture

### 🧠 Agent NLP (`agent_nlp_mcp.py`)
- **Capacités**: Analyse de texte, détection PII, résumé, traduction
- **Formats supportés**: TXT, PDF, Markdown
- **Outils MCP**: `analyze_text`, `detect_pii_in_text`, `summarize_text`, `translate_text`
- **Ressources MCP**: `nlp://config`, `nlp://status`

### 🎵 Agent Audio (`agent_audio_mcp.py`)
- **Capacités**: Analyse audio, transcription, extraction de features
- **Formats supportés**: MP3, WAV, M4A, FLAC
- **Outils MCP**: `analyze_audio`, `transcribe_audio`, `extract_features`
- **Ressources MCP**: `audio://config`, `audio://status`

### 🎯 Agent Manager (`agent_manager_mcp.py`)
- **Capacités**: Classification de fichiers, orchestration de workflows
- **Rôle**: Coordonnateur central qui route les tâches vers les agents appropriés
- **Outils MCP**: `classify_file`, `scan_directory`, `execute_workflow`
- **Ressources MCP**: `manager://agents`, `manager://status`

### 🌐 Hub MCP (`mcp_hub.py`)
- **Rôle**: Service unifié exposant tous les agents via MCP
- **Capacités**: Découverte d'agents, recommandations, orchestration
- **Outils MCP**: `discover_agents`, `recommend_agents`, `create_workflow`
- **Ressources MCP**: `hub://agents`, `hub://capabilities`, `hub://status`

## Fonctionnalités Clés

### ✅ Protocole MCP Natif
- Utilisation de la librairie officielle `mcp` (python-sdk)
- Décorateurs `@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`
- Communication via `FastMCP` et `ClientSession`

### ✅ Communication Inter-Agents
- Protocole standardisé via MCP
- Découverte automatique des agents
- Routage intelligent des tâches

### ✅ Workflow Multi-Agents
- Orchestration centralisée par le manager
- Traitement parallèle des fichiers
- Gestion des dépendances entre tâches

### ✅ Sortie Structurée
- Modèles Pydantic pour toutes les réponses
- Validation automatique des données
- Typage fort avec `BaseModel`

## Installation

```bash
# Installer les dépendances
pip install mcp transformers torch PyPDF2 pydantic

# Cloner le projet
git clone <repository-url>
cd KACM-Qualcomm-track/agent_nlp
```

## Utilisation

### 1. Lancement des Agents Individuels

```bash
# Agent NLP
python agent_nlp_mcp.py

# Agent Audio
python agent_audio_mcp.py

# Agent Manager
python agent_manager_mcp.py

# Hub MCP
python mcp_hub.py
```

### 2. Test du Système

```bash
# Exécuter tous les tests
python test_mcp_system.py
```

### 3. Configuration Claude Desktop

Ajouter à `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nlp-agent": {
      "command": "python",
      "args": ["agent_nlp_mcp.py"],
      "env": {}
    },
    "audio-agent": {
      "command": "python",
      "args": ["agent_audio_mcp.py"],
      "env": {}
    },
    "agent-manager": {
      "command": "python",
      "args": ["agent_manager_mcp.py"],
      "env": {}
    },
    "mcp-hub": {
      "command": "python",
      "args": ["mcp_hub.py"],
      "env": {}
    }
  }
}
```

## Exemples d'Usage

### Analyse de Texte via Agent NLP

```python
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

# Connexion à l'agent NLP
server_params = StdioServerParameters(
    command="python",
    args=["agent_nlp_mcp.py"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # Analyse de texte
        result = await session.call_tool(
            "analyze_text",
            arguments={"text": "Votre texte ici"}
        )
        print(result)
```

### Workflow Multi-Agents via Manager

```python
# Connexion au manager
server_params = StdioServerParameters(
    command="python",
    args=["agent_manager_mcp.py"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # Traitement d'un répertoire
        result = await session.call_tool(
            "process_directory",
            arguments={
                "directory": "./documents",
                "operations_by_agent": {
                    "nlp": ["analyze", "summarize"],
                    "audio": ["transcribe"]
                }
            }
        )
        print(result)
```

## Structure des Fichiers

```
agent_nlp/
├── agent_nlp_mcp.py      # Agent NLP avec MCP
├── agent_audio_mcp.py    # Agent Audio avec MCP
├── agent_manager_mcp.py  # Agent Manager avec MCP
├── mcp_hub.py           # Hub MCP unifié
├── config.py            # Configuration système
├── test_mcp_system.py   # Tests du système
├── README.md            # Cette documentation
├── logs/                # Fichiers de log
└── temp/                # Fichiers temporaires
```

## Protocoles et Standards

### MCP (Model Context Protocol)
- **Spécification**: [spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io/)
- **SDK Python**: [github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- **Transport**: stdio, HTTP, WebSocket

### Types de Primitives MCP
- **Resources**: Données contextuelles (`@mcp.resource()`)
- **Tools**: Fonctions exécutables (`@mcp.tool()`)
- **Prompts**: Templates d'interaction (`@mcp.prompt()`)

## Avantages du Système

### 🔧 Modularité
- Agents spécialisés et indépendants
- Communication via protocole standardisé
- Ajout facile de nouveaux agents

### 🚀 Scalabilité
- Traitement parallèle des fichiers
- Orchestration intelligente des tâches
- Gestion des ressources optimisées

### 🛡️ Robustesse
- Validation des données avec Pydantic
- Gestion d'erreurs structurée
- Logging centralisé

### � Interopérabilité
- Protocole MCP standard
- Compatible avec Claude Desktop
- Extensible vers d'autres clients MCP

## Développement Futur

### Prochaines Étapes
1. **Agents Additionnels**: Image, Vidéo, Document
2. **Persistance**: Base de données pour les workflows
3. **Interface Web**: Dashboard pour l'orchestration
4. **Déploiement**: Containerisation Docker
5. **Monitoring**: Métriques et alertes

### Extensions Possibles
- Agent de reconnaissance d'images
- Agent de traitement vidéo
- Agent de génération de rapports
- Intégration avec APIs externes
- Interface graphique pour configuration

- `agent_nlp.py` : **Agent NLP principal** ✅
- `recit.txt` : Fichier de test sans PII
- `rapport_client.txt` : Fichier de test avec PII
- `requirements.txt` : Dépendances Python
- `install_ollama.bat` : Script d'installation Ollama
- `README.md` : Ce fichier

## 🛠️ Utilisation

### Commande basique
```bash
python agent_nlp.py rapport_client.txt
```

### Sauvegarde dans un fichier
```bash
python agent_nlp.py rapport_client.txt resultat.json
```

### Mode offline (sans IA)
```bash
python agent_nlp.py rapport_client.txt --offline
```

### Tests
```bash
python agent_nlp.py --test
```

## � Format de sortie

```json
{
  "file_path": "C:\\chemin\\vers\\fichier.txt",
  "resume": "Résumé du contenu en 3 phrases maximum...",
  "warning": true
}
```

## 🔍 Détection PII

L'agent détecte automatiquement :
- **Emails** : marie@email.com
- **Téléphones** : +33 6 12 34 56 78
- **Cartes bancaires** : 4242 4242 4242 4242
- **IBAN** : FR14 2004 1010 0505 0001 3M02 606
- **Numéros SSN** : 123-45-6789

## 🎨 Exemples concrets

### Fichier sans PII
```bash
python agent_nlp.py recit.txt --offline
```

**Sortie :**
```json
{
  "file_path": "C:\\...\\recit.txt",
  "resume": "L'Intelligence Artificielle au Service de l'Humanité...",
  "warning": false
}
```

### Fichier avec PII
```bash
python agent_nlp.py rapport_client.txt --offline
```

**Sortie :**
```json
{
  "file_path": "C:\\...\\rapport_client.txt",
  "resume": "Rapport de Service Client - Confidentiel...",
  "warning": true
}
```

## 🧪 Intégration Python

```python
from agent_nlp import process_file
import json

# Traitement d'un fichier
result = process_file("mon_fichier.txt", offline_mode=True)

# Accès aux données
file_path = result["file_path"]
resume = result["resume"]
warning = result["warning"]

if warning:
    print("⚠️  Informations personnelles détectées !")
```

## 🎯 Migration réussie

✅ **Workspace nettoyé** - Un seul fichier `agent_nlp.py`  
✅ **JSON simplifié** - file_path, resume, warning  
✅ **Détection PII** - Retour boolean simple  
✅ **Résumé IA** - Avec Llama 3.2 + mode offline  
✅ **Interface simple** - Ligne de commande intuitive  

L'agent est maintenant **prêt à l'emploi** ! 🚀
Group repo for "Raise your hack" hackathon within the Qualcomm track
