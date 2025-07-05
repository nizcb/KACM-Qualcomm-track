# Agent de Sécurité IA - Version Minimale

Agent de sécurité intelligent qui utilise l'IA (Llama via Ollama) pour analyser et expliquer les contenus des fichiers lors des opérations de chiffrement et déchiffrement.

## Architecture Simplifiée

Le projet est organisé en **deux scripts principaux** :

1. **`security_agent_core.py`** - Agent principal avec toutes les fonctionnalités :
   - Chiffrement/Déchiffrement AES-256
   - Analyse IA via Ollama/Llama
   - Gestion du vault sécurisé
   - Authentification par phrase secrète
   - Interface CLI complète

2. **`security_interface.py`** - Interface Streamlit séparée :
   - Interface graphique moderne
   - Connexion à l'agent via import Python
   - Fonctionnalités complètes en mode graphique

## Installation Rapide

```bash
# Installer les dépendances
pip install -r requirements.txt

# Démarrer l'interface Streamlit
./start.sh
```

## Utilisation

### Interface Graphique (Recommandée)
```bash
./start.sh
```
Puis ouvrir http://localhost:8501 dans votre navigateur.

### Ligne de Commande
```bash
# Test de l'agent
python security_agent_core.py test

# Chiffrement d'un fichier
python security_agent_core.py encrypt /path/to/file.txt

# Déchiffrement d'un fichier
python security_agent_core.py decrypt /path/to/encrypted/file.aes
```

## Fonctionnalités

- ✅ **Chiffrement/Déchiffrement** : AES-256 avec clés sécurisées
- ✅ **Analyse IA** : Explication intelligente du contenu via Llama 3.2
- ✅ **Vault sécurisé** : Stockage SQLite chiffré des métadonnées
- ✅ **Authentification** : Protection par phrase secrète
- ✅ **Auto-installation** : Ollama et modèle Llama installés automatiquement
- ✅ **Interface moderne** : Streamlit avec design responsive

## Structure du Projet

```
security_agent/
├── security_agent_core.py    # Agent principal (CLI + fonctionnalités)
├── security_interface.py     # Interface Streamlit
├── start.sh                  # Script de démarrage
├── requirements.txt          # Dépendances Python
├── README.md                # Documentation
├── .gitignore               # Fichiers ignorés par Git
├── vault/                   # Vault sécurisé (SQLite + clés)
├── encrypted/               # Fichiers chiffrés
├── decrypted/               # Fichiers déchiffrés (temporaires)
└── test_sensitive_file.txt  # Fichier de test
```

## Sécurité

- 🔒 **Chiffrement AES-256** avec clés générées aléatoirement
- 🔐 **Authentification** par phrase secrète
- 🗄️ **Vault protégé** par mot de passe maître
- 🧹 **Nettoyage automatique** des fichiers temporaires
- 🔍 **Analyse IA** sans stockage permanent du contenu

## Développement

Le projet est maintenant simplifié avec seulement deux scripts essentiels :
- Un agent principal autonome (`security_agent_core.py`)
- Une interface web séparée (`security_interface.py`)

Cette architecture permet une utilisation flexible, que ce soit via l'interface graphique ou en ligne de commande.
