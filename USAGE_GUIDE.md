# Guide d'Utilisation - Système Multi-Agents MCP

## 🚀 Démarrage Rapide

### 1. Vérification du Système
```bash
python quick_start.py check
```

### 2. Démonstration
```bash
python quick_start.py demo
```

### 3. Système Complet
```bash
python quick_start.py main
```

## 📁 Structure du Projet

```
KACM-Qualcomm-track/
├── agent_nlp/                          # 🤖 Agents du système
│   ├── agent_orchestrator_mcp.py       # 🎯 Orchestrateur principal
│   ├── agent_nlp_mcp.py                # 📝 Agent NLP (texte)
│   ├── agent_vision_mcp.py             # 👁️ Agent Vision (images)
│   ├── agent_audio_mcp.py              # 🎵 Agent Audio (sons)
│   ├── agent_file_manager_mcp.py       # 📁 Gestionnaire de fichiers
│   ├── agent_security_mcp.py           # 🔒 Agent de sécurité
│   ├── main.py                         # 🎮 Interface principal
│   ├── config.py                       # ⚙️ Configuration
│   ├── startup_multi_agent_system.py   # 🚀 Gestionnaire système
│   └── test_multi_agent_workflow.py    # 🧪 Tests
├── quick_start.py                      # ⚡ Démarrage rapide
├── requirements.txt                    # 📦 Dépendances
└── README.md                           # 📖 Documentation
```

## 🔄 Workflow Complet

### Étape 1: Scanner un Répertoire
```python
# L'orchestrateur scanne le répertoire
python agent_nlp/main.py scan ./mon_repertoire
```

### Étape 2: Classification Automatique
- **Fichiers texte** (.txt, .pdf, .md, .json) → Agent NLP
- **Fichiers image** (.jpg, .png, .gif) → Agent Vision  
- **Fichiers audio** (.mp3, .wav, .flac) → Agent Audio

### Étape 3: Traitement Spécialisé
Chaque agent retourne le format unifié:
```json
{
  "file_path": "chemin/vers/fichier",
  "summary": "Résumé du contenu",
  "warning": true/false
}
```

### Étape 4: Consolidation
Le File Manager consolide tous les résultats.

### Étape 5: Sécurité
Les fichiers avec `warning: true` sont envoyés à l'Agent Security.

## 🎯 Commandes Principales

### Orchestrateur
```bash
cd agent_nlp
python main.py start                    # Démarrer le système
python main.py process ./documents     # Traiter un répertoire
python main.py scan ./documents        # Scanner seulement
python main.py demo                     # Démonstration
python main.py status                   # Statut des agents
```

### Tests
```bash
python main.py test                     # Tests complets
python main.py test-quick               # Tests rapides
```

## 🤖 Communication MCP

### Ports des Agents
- **Orchestrateur**: 8001
- **NLP**: 8002  
- **Vision**: 8003
- **Audio**: 8004
- **File Manager**: 8005
- **Security**: 8006

### Communication A2A (Agent-to-Agent)
```python
# Exemple d'appel MCP
import httpx

async def call_nlp_agent(file_path):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8002/analyze_file",
            json={"file_path": file_path}
        )
        return response.json()
```

## 🔧 Configuration

### Variables d'Environnement
```bash
# Ollama (optionnel pour IA avancée)
export OLLAMA_BASE_URL=http://localhost:11434
export LLAMA_MODEL=llama3.2:latest

# Logs
export LOG_LEVEL=INFO
```

### Configuration des Agents
Modifiez `agent_nlp/config.py` pour personnaliser:
- Limites de traitement
- Modèles d'IA
- Répertoires de sortie
- Paramètres de sécurité

## 📊 Exemples d'Utilisation

### Traitement d'un Projet
```bash
# Traiter tous les fichiers d'un projet
python agent_nlp/main.py process ./mon_projet

# Résultats dans:
# - results/: Rapports JSON
# - output/: Fichiers traités
# - logs/: Logs détaillés
```

### Analyse de Sécurité
```bash
# Scanner pour des informations sensibles
python agent_nlp/main.py scan ./documents_confidentiels

# Les fichiers avec PII sont automatiquement:
# - Détectés par l'Agent NLP
# - Signalés avec warning: true
# - Sécurisés par l'Agent Security
```

### Traitement d'Images
```bash
# L'Agent Vision analyse automatiquement:
# - Contenu des images
# - Détection d'informations sensibles
# - Extraction de texte (OCR)
# - Détection de contenu NSFW
```

## 🔒 Sécurité et PII

### Détection Automatique
- **Emails**: john@example.com
- **Téléphones**: +33 1 23 45 67 89
- **Cartes bancaires**: 4532 1234 5678 9012
- **IBAN**: FR76 1234 5678 9012 3456 789
- **Documents d'identité**: Détection visuelle

### Actions de Sécurité
- **Chiffrement**: AES-256
- **Quarantaine**: Isolation des fichiers
- **Audit**: Traçabilité complète
- **Notifications**: Alertes automatiques

## 🧪 Tests et Validation

### Tests Automatisés
```bash
python test_multi_agent_workflow.py
```

### Tests Manuels
```bash
# Créer des fichiers de test
mkdir test_files
echo "Document normal" > test_files/normal.txt
echo "Email: test@example.com" > test_files/sensitive.txt

# Traiter
python agent_nlp/main.py process test_files
```

## 📈 Monitoring

### Logs
```bash
# Voir les logs
python agent_nlp/main.py logs

# Ou directement
tail -f logs/orchestrator.log
```

### Statut des Agents
```bash
python agent_nlp/main.py status
```

## 🛠️ Dépannage

### Problèmes Fréquents

1. **Port occupé**
   ```bash
   # Arrêter tous les agents
   python agent_nlp/main.py stop
   ```

2. **Ollama non disponible**
   ```bash
   # Le système fonctionne sans Ollama
   # Mais l'analyse IA sera limitée
   ```

3. **Dépendances manquantes**
   ```bash
   pip install -r requirements.txt
   ```

### Mode Debug
```bash
export LOG_LEVEL=DEBUG
python agent_nlp/main.py test
```

## 🎯 Cas d'Usage

### 1. Audit de Conformité
```bash
# Scanner tous les documents pour les PII
python agent_nlp/main.py process ./documents_entreprise
# → Rapport de conformité automatique
```

### 2. Veille Sécuritaire
```bash
# Surveiller un dossier partagé
python agent_nlp/main.py process ./dossier_partage
# → Détection automatique des fuites de données
```

### 3. Classification Documentaire
```bash
# Organiser une bibliothèque de documents
python agent_nlp/main.py process ./bibliotheque
# → Classification et résumés automatiques
```

## 📞 Support

### Debug
1. Vérifiez les logs: `logs/`
2. Testez les agents individuellement
3. Vérifiez la configuration: `agent_nlp/config.py`

### Performance
- Utilisez Ollama pour l'IA avancée
- Ajustez `max_concurrent_files` dans la config
- Surveillez l'utilisation mémoire

---

**🎉 Félicitations! Votre système multi-agents MCP est prêt!**

Commencez par: `python quick_start.py demo`
