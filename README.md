# Multi-Agent MCP System

## Vue d'ensemble

Système multi-agents modulaire utilisant le Model Context Protocol (MCP) pour la communication inter-agents. Le système analyse automatiquement différents types de fichiers (texte, image, audio) en utilisant des agents spécialisés et coordonne les actions de sécurité.

## Architecture

### Agents du Système

1. **Agent Orchestrateur** (`agent_orchestrator_mcp.py`)
   - Coordinateur principal du système
   - Scanne les répertoires et classifie les fichiers
   - Dispatche les tâches aux agents spécialisés
   - Collecte et coordonne les résultats

2. **Agent NLP** (`agent_nlp_mcp.py`)
   - Traite les fichiers texte (.txt, .pdf, .md, .json, etc.)
   - Détection intelligente des PII avec IA (Ollama/Llama)
   - Analyse sémantique et résumé automatique
   - Support multilingue

3. **Agent Vision** (`agent_vision_mcp.py`)
   - Traite les fichiers image (.jpg, .png, .gif, etc.)
   - Analyse de contenu visuel
   - Détection d'objets et reconnaissance
   - Génération de descriptions

4. **Agent Audio** (`agent_audio_mcp.py`)
   - Traite les fichiers audio (.mp3, .wav, .flac, etc.)
   - Analyse de contenu audio
   - Transcription et analyse vocale
   - Détection de caractéristiques sonores

5. **Agent File Manager** (`agent_file_manager_mcp.py`)
   - Consolide les résultats de tous les agents
   - Génère des rapports détaillés
   - Gère les statistiques et l'historique
   - Organise les fichiers de sortie

6. **Agent Security** (`agent_security_mcp.py`)
   - Sécurise les fichiers avec warnings
   - Actions de chiffrement et quarantaine
   - Audit et notifications de sécurité
   - Gestion des politiques de sécurité

## Format de Sortie Unifié

Tous les agents retournent un format JSON standardisé :

```json
{
  "file_path": "chemin/vers/fichier",
  "summary": "Résumé du contenu",
  "warning": true/false
}
```

## Communication MCP

Le système utilise le protocole MCP (Model Context Protocol) pour :
- Communication agent-to-agent (A2A)
- Exposition des outils via FastMCP
- Standardisation des interfaces
- Découverte automatique des services

### Ports par Défaut

- **Orchestrateur** : 8001
- **NLP** : 8002
- **Vision** : 8003
- **Audio** : 8004
- **File Manager** : 8005
- **Security** : 8006

## Installation

### Prérequis

```bash
# Python 3.8+
pip install -r requirements.txt
```

### Dépendances Principales

```
mcp-server-fastmcp
pydantic
langchain-community
ollama
PyPDF2
pymupdf
pillow
librosa
psutil
```

### Configuration Ollama (Optionnel)

Pour l'analyse IA avancée :

```bash
# Installer Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Télécharger un modèle
ollama pull llama3.2:latest
```

## Utilisation

### Démarrage Rapide

```bash
# Démarrer tous les agents
python startup_multi_agent_system.py start

# Vérifier le statut
python startup_multi_agent_system.py status

# Lancer les tests
python startup_multi_agent_system.py test

# Arrêter tous les agents
python startup_multi_agent_system.py stop
```

### Utilisation Programmatique

```python
from agent_orchestrator_mcp import AgentOrchestrator
import asyncio

async def main():
    orchestrator = AgentOrchestrator()
    
    # Traiter un répertoire
    result = await orchestrator.process_directory("./mon_repertoire")
    
    print(f"Fichiers traités: {len(result.processed_files)}")
    print(f"Avertissements: {result.total_warnings}")

asyncio.run(main())
```

### Traitement par Lot

```python
# Scan d'un répertoire
scan_result = orchestrator.scan_directory("./documents", recursive=True)

# Traitement complet
processing_result = await orchestrator.process_batch("./documents")
```

## Workflow Complet

1. **Scan** : L'orchestrateur scanne le répertoire cible
2. **Classification** : Les fichiers sont classifiés par type
3. **Dispatch** : Chaque fichier est envoyé à l'agent approprié
4. **Traitement** : Les agents spécialisés analysent les fichiers
5. **Consolidation** : Le File Manager consolide les résultats
6. **Sécurité** : Les fichiers avec warnings sont sécurisés
7. **Rapport** : Un rapport final est généré

## Configuration

### Variables d'Environnement

```bash
# Ollama (optionnel)
export OLLAMA_BASE_URL=http://localhost:11434
export LLAMA_MODEL=llama3.2:latest

# Logging
export LOG_LEVEL=INFO
```

### Fichiers de Configuration

Chaque agent a sa propre configuration dans `config.py` :

```python
# Configuration NLP
NLP_CONFIG = {
    'max_text_length': 10000,
    'use_ai_analysis': True,
    'offline_mode': False
}

# Configuration Vision
VISION_CONFIG = {
    'max_image_size': 10 * 1024 * 1024,  # 10MB
    'supported_formats': ['.jpg', '.png', '.gif']
}
```

## Tests

### Suite de Tests Complète

```bash
# Lancer tous les tests
python test_multi_agent_workflow.py
```

### Tests Individuels

```python
# Test d'un agent spécifique
from agent_nlp_mcp import NLPAgent, NLPConfig

agent = NLPAgent(NLPConfig())
result = await agent.analyze_file("document.txt")
```

## Développement

### Ajouter un Nouvel Agent

1. Créer `agent_mon_agent_mcp.py`
2. Hériter de la classe de base
3. Implémenter les méthodes requises
4. Exposer les outils via MCP
5. Ajouter au startup script

### Structure d'un Agent

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

class MonAgent:
    def __init__(self, config):
        self.config = config
        
    async def process_file(self, file_path: str):
        # Logique de traitement
        return {
            "file_path": file_path,
            "summary": "Résumé",
            "warning": False
        }

# Serveur MCP
mcp_server = FastMCP("Mon Agent MCP")

@mcp_server.tool()
async def analyze_file(file_path: str):
    agent = MonAgent(config)
    return await agent.process_file(file_path)
```

## Monitoring

### Logs

Les logs sont disponibles dans `logs/` :

- `orchestrator.log` : Logs de l'orchestrateur
- `nlp_agent.log` : Logs de l'agent NLP
- `vision_agent.log` : Logs de l'agent Vision
- `audio_agent.log` : Logs de l'agent Audio

### Métriques

```python
# Statut du système
python startup_multi_agent_system.py status

# Ou programmatiquement
from startup_multi_agent_system import status
status()
```

## Sécurité

### Détection PII

L'agent NLP détecte automatiquement :
- Adresses email
- Numéros de téléphone
- Numéros de carte bancaire
- Codes IBAN
- Numéros de sécurité sociale

### Actions de Sécurité

L'agent Security peut :
- Chiffrer les fichiers sensibles
- Mettre en quarantaine
- Envoyer des notifications
- Créer des audits

## Dépannage

### Problèmes Courants

1. **Port occupé** : Vérifiez les processus en cours
2. **Ollama non disponible** : Le système fonctionne en mode offline
3. **Fichiers non supportés** : Vérifiez les extensions supportées
4. **Permissions** : Assurez-vous des droits d'accès aux fichiers

### Debug

```bash
# Logs détaillés
export LOG_LEVEL=DEBUG

# Mode test
python startup_multi_agent_system.py test
```

## Roadmap

- [ ] Interface web pour monitoring
- [ ] Support de nouveaux formats de fichiers
- [ ] Intégration avec des services cloud
- [ ] API REST pour intégration externe
- [ ] Dashboard de métriques en temps réel

## Contribution

1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Pousser vers la branche
5. Créer une Pull Request

## Licence

MIT License - voir le fichier LICENSE pour plus de détails.

## Support

Pour des questions ou des problèmes :
- Ouvrir une issue sur GitHub
- Consulter la documentation
- Vérifier les logs dans `logs/`
