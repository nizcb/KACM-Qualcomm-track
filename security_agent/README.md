# Agent de Sécurité IA

Agent de sécurité intelligent avec chiffrement AES-256 et analyse IA via Ollama/Llama.

## 🚀 Démarrage rapide

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'interface
./run.sh
```

Interface disponible sur : http://localhost:8501

## 📁 Structure

```
security_agent/
├── security_agent_core.py    # Agent principal
├── security_interface.py     # Interface Streamlit
├── run.sh                    # Script de démarrage
├── requirements.txt          # Dépendances
├── test_file.txt            # Fichier de test
├── vault/                   # Base de données sécurisée
├── encrypted/               # Fichiers chiffrés
└── decrypted/               # Fichiers déchiffrés (temporaires)
```

## 🔐 Fonctionnalités

- **Chiffrement AES-256** : Sécurisation des fichiers sensibles
- **Analyse IA** : Explication du contenu via Llama 3.2
- **Vault sécurisé** : Base de données SQLite chiffrée
- **Authentification** : Protection par phrase secrète
- **Interface moderne** : Streamlit responsive

## 🧪 Test

**Fichier de test** : `test_file.txt`
**Phrase secrète** : `mon_secret_ultra_securise_2024`

## 🛠️ Utilisation

### Interface graphique
1. Lancer : `./run.sh`
2. Ouvrir : http://localhost:8501
3. Chiffrer un fichier
4. Déchiffrer avec authentification

### Ligne de commande
```bash
# Test de l'agent
python security_agent_core.py test
```

## 🔒 Sécurité

- Chiffrement AES-256 avec clés aléatoires
- Authentification par phrase secrète
- Vault protégé par clé maître
- Nettoyage automatique des fichiers temporaires
