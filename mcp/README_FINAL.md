# 🤖 Système Multi-Agent - KACM Qualcomm Hackathon

## 🎯 Vue d'ensemble

Système multi-agents intelligent utilisant l'IA pour analyser automatiquement différents types de fichiers (texte, image, audio) et sécuriser les données sensibles. Le système intègre une interface desktop moderne avec une recherche intelligente pilotée par l'IA.

## ✨ Fonctionnalités Principales

### 🔍 **Analyse Intelligente Multi-Format**

- **Fichiers texte** : Détection PII, analyse sémantique (PDF, TXT, MD, JSON, etc.)
- **Images** : Reconnaissance de documents sensibles (carte vitale, passeport, etc.)
- **Audio** : Analyse de contenu vocal et transcription
- **Sécurité** : Chiffrement automatique des fichiers sensibles

### 🎨 **Interface Desktop Moderne**

- Interface graphique intuitive avec drag & drop
- Recherche intelligente en langage naturel
- Authentification sécurisée pour les fichiers chiffrés
- Visualisation des résultats en temps réel

### 🔐 **Vault Sécurisé**

- Chiffrement automatique des fichiers sensibles
- Base de données SQLite pour la gestion des clés
- Authentification par phrase de passe
- Audit trail complet

### 🌐 **API RESTful**

- API FastAPI complète avec documentation Swagger
- Endpoints pour tous les services
- Communication asynchrone entre agents
- Monitoring et métriques

## 🚀 Installation et Démarrage

### Prérequis

```bash
# Python 3.8+
python --version

# Dépendances système (Ubuntu/Debian)
sudo apt-get install python3-tk python3-pip

# Dépendances Python (installées automatiquement)
pip install -r requirements_fixed.txt
```

### Démarrage Rapide - Démonstration Complète

```bash
# Démarrer le système complet (recommandé)
python launch_system.py --mode demo

# Ou avec WSL sur Windows
wsl -e bash -c "cd /mnt/c/Users/chaki/Desktop/hackathon/KACM-Qualcomm-track/mcp && python3 launch_system.py --mode demo"
```

### Démarrage par Composant

```bash
# API seulement
python launch_system.py --mode api

# Interface desktop seulement
python launch_system.py --mode desktop

# Tests seulement
python launch_system.py --mode test
```

## 🎬 Guide de Démonstration

### 1. **Préparation**

```bash
# Lancer la démonstration complète
python launch_system.py --mode demo
```

### 2. **Analyse de Fichiers**

1. **Sélectionner le dossier** : Cliquez sur "Parcourir" et sélectionnez `demo_files`
2. **Analyser** : Cliquez sur "🚀 Analyser le Dossier"
3. **Observer** : Regardez l'analyse en temps réel dans l'onglet "Fichiers Analysés"

### 3. **Recherche Intelligente**

1. **Tapez votre requête** : Ex: "trouve moi le scan de ma carte vitale"
2. **Rechercher** : Cliquez sur "🤖 Rechercher avec IA"
3. **Authentification** : Saisissez le mot de passe : `mon_secret_ultra_securise_2024`

### 4. **Exemples de Recherche**

- `"trouve moi le scan de ma carte vitale"` → Fichier chiffré dans le vault
- `"donne moi le pdf de cours d'histoire"` → Fichier normal accessible
- `"où est ma photo d'identité"` → Document sensible chiffré
- `"liste les factures de ce mois"` → Recherche dans les documents

## 🏗️ Architecture Technique

### 🤖 **Agents Spécialisés**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Agent NLP      │    │  Agent Vision   │    │  Agent Audio    │
│  Port: 8002     │    │  Port: 8003     │    │  Port: 8004     │
│  - Texte        │    │  - Images       │    │  - Audio        │
│  - PII          │    │  - OCR          │    │  - Speech       │
│  - Sémantique   │    │  - Objets       │    │  - Analyse      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Orchestrateur  │
                    │  Port: 8001     │
                    │  - Coordination │
                    │  - Dispatch     │
                    │  - Consolidation│
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  File Manager   │    │  Agent Security │    │  FastAPI Server │
│  Port: 8005     │    │  Port: 8006     │    │  Port: 8000     │
│  - Consolidation│    │  - Chiffrement  │    │  - REST API     │
│  - Rapports     │    │  - Vault        │    │  - Interface    │
│  - Historique   │    │  - Audit        │    │  - Documentation│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔄 **Workflow de Traitement**

1. **Scan** → L'orchestrateur scanne le répertoire
2. **Classification** → Tri automatique par type de fichier
3. **Dispatch** → Envoi vers l'agent approprié
4. **Analyse** → Traitement spécialisé + détection PII
5. **Sécurisation** → Chiffrement automatique si sensible
6. **Consolidation** → Agrégation des résultats
7. **Rapport** → Génération du rapport final

## 🔧 Structure des Fichiers

```
mcp/
├── 🚀 launch_system.py              # Lanceur principal
├── 🌐 api_server.py                 # Serveur API FastAPI
├── 🖥️ desktop_app_integrated.py    # Interface desktop
├── 🤖 simple_mcp_system.py         # Système MCP simplifié
├── 🧪 test_system.py               # Suite de tests
├── 📦 requirements_fixed.txt       # Dépendances
├── 📚 README_FINAL.md              # Cette documentation
│
├── demo_files/                      # Fichiers de démonstration
│   ├── document_public.txt         # Document normal
│   ├── document_confidentiel.txt   # Document avec PII
│   ├── carte_vitale_scan.jpg       # Image sensible
│   ├── cours_histoire.pdf          # Document normal
│   └── ...
│
├── vault/                          # Coffre-fort sécurisé
├── encrypted/                      # Fichiers chiffrés
├── decrypted/                      # Fichiers déchiffrés (temp)
├── logs/                           # Logs du système
└── temp/                           # Fichiers temporaires
```

## 🎯 Scénarios d'Usage

### 👔 **Entreprise - Conformité RGPD**

```bash
# Analyser un répertoire d'entreprise
python launch_system.py --mode demo
# Sélectionner le dossier contenant les documents
# Le système détecte automatiquement les PII et les chiffre
```

### 🏠 **Personnel - Organisation de Documents**

```bash
# Organiser ses documents personnels
python launch_system.py --mode demo
# Recherche: "trouve mes documents d'identité"
# Le système localise et sécurise automatiquement
```

### 🔍 **Recherche Intelligente**

```bash
# Recherche en langage naturel
"trouve moi le scan de ma carte vitale"
"où sont mes factures d'électricité"
"liste tous les documents contenant des emails"
```

## 🧪 Tests et Validation

### Tests Automatisés

```bash
# Suite de tests complète
python test_system.py

# Tests spécifiques
python test_system.py mcp      # Système MCP
python test_system.py api      # API server
python test_system.py desktop  # Interface desktop
```

### Validation Manuel

```bash
# Démarrer en mode test
python launch_system.py --mode test

# Vérifier les logs
tail -f logs/*.log
```

## 📊 Métriques et Monitoring

### API Endpoints

- `GET /health` - Santé du système
- `GET /system/status` - Statut des agents
- `POST /process/directory` - Analyser un dossier
- `POST /search/smart` - Recherche intelligente
- `POST /file/decrypt` - Déchiffrer un fichier

### Documentation API

```bash
# Accéder à la documentation Swagger
http://localhost:8000/docs
```

## 🔒 Sécurité

### Chiffrement

- **Algorithme** : AES-256
- **Clés** : Dérivées de phrases de passe
- **Stockage** : Base SQLite chiffrée
- **Audit** : Logs complets des accès

### Authentification

- **Mot de passe par défaut** : `mon_secret_ultra_securise_2024`
- **Hachage** : SHA-256
- **Sessions** : Gestion automatique
- **Timeout** : Configuration par utilisateur

## 🎨 Personnalisation

### Configuration

```python
# Modifier les paramètres dans simple_mcp_system.py
class ConfigurationPersonnalisee:
    VAULT_PASSWORD = "votre_mot_de_passe_securise"
    API_PORT = 8000
    LOG_LEVEL = "INFO"
```

### Ajout d'Agents

```python
# Créer un nouvel agent
class MonNouvelAgent(SimpleMCPAgent):
    def __init__(self):
        super().__init__("MonAgent", 8007)
        self.register_tool("mon_outil", self.mon_outil)
```

## 🐛 Dépannage

### Problèmes Courants

**❌ "API non disponible"**

```bash
# Vérifier que l'API est démarrée
curl http://localhost:8000/health
```

**❌ "Modules manquants"**

```bash
# Installer les dépendances
pip install -r requirements_fixed.txt
```

**❌ "Erreur tkinter"**

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter
```

### Logs de Debug

```bash
# Activer le debug
export LOG_LEVEL=DEBUG
python launch_system.py --mode demo
```

## 🚀 Évolutions Futures

### Roadmap

- [ ] **Intégration Ollama/Llama** - IA locale avancée
- [ ] **Interface Web** - Dashboard moderne
- [ ] **API REST étendue** - Intégration externe
- [ ] **Agents supplémentaires** - Vidéo, code source
- [ ] **Cloud Storage** - Intégration AWS/Azure
- [ ] **Mobile App** - Application mobile

### Contributions

```bash
# Fork le projet
git clone https://github.com/votre-username/KACM-Qualcomm-track.git
cd KACM-Qualcomm-track/mcp

# Créer une branche
git checkout -b feature/nouvelle-fonctionnalite

# Développer et tester
python test_system.py

# Soumettre une PR
```

## 📞 Support

### Contact

- **Email** : support@kacm-qualcomm.com
- **Issues** : [GitHub Issues](https://github.com/nizcb/KACM-Qualcomm-track/issues)
- **Documentation** : [Wiki](https://github.com/nizcb/KACM-Qualcomm-track/wiki)

### Communauté

- **Discord** : [Serveur KACM](https://discord.gg/kacm)
- **Forum** : [Discussions](https://github.com/nizcb/KACM-Qualcomm-track/discussions)

---

## 🎉 Conclusion

Ce système multi-agents représente une solution complète d'analyse et de sécurisation automatique de documents utilisant l'IA. Il combine :

- **Intelligence Artificielle** pour l'analyse contextuelle
- **Sécurité Enterprise** pour la protection des données
- **Interface Moderne** pour une expérience utilisateur optimale
- **Architecture Modulaire** pour la scalabilité

**Prêt pour votre démonstration !** 🚀

```bash
# Commande magique pour démarrer la démo
python launch_system.py --mode demo
```

---

_Développé avec ❤️ pour le Hackathon KACM Qualcomm 2024_
