# Guide d'Installation - Système KACM

## Prérequis

- Python 3.9 ou supérieur
- Node.js 16+ (pour certains outils)
- Git pour le versioning

## Installation

```bash
# Cloner le repository
git clone https://github.com/votre-org/kacm-system.git
cd kacm-system

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:1b
```

## Configuration

Créer un fichier `.env`:

```
OLLAMA_BASE_URL=http://localhost:11434
LLAMA_MODEL=llama3.2:1b
LOG_LEVEL=INFO
```

## Lancement

```bash
# Démarrer tous les agents
python system_manager.py start

# Vérifier le statut
python system_manager.py health

# Lancer les tests
python system_manager.py test
```

## Utilisation

Voir le fichier `USAGE.md` pour les exemples d'utilisation.
