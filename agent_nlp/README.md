# # Agent NLP - Version finale

## 🎯 Objectif
Agent NLP Python migré de Coral/Pydantic vers LangChain, utilisant le modèle Llama 3.2 via Ollama.

**Retourne un JSON avec :**
- `file_path` : chemin du fichier (string)
- `resume` : résumé du contenu (string) 
- `warning` : présence d'informations PII (boolean)

## 🚀 Installation

### 1. Installer Ollama
```bash
# Télécharger depuis https://ollama.ai/
# Ou utiliser le script fourni
install_ollama.bat
```

### 2. Installer le modèle Llama 3.2
```bash
ollama pull llama3.2:latest
```

### 3. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

## 📋 Fichiers du projet

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
