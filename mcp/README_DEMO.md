# 🚀 DÉMO SYSTÈME MULTI-AGENT - GUIDE RAPIDE

## 🎯 Démarrage Ultra-Rapide

### Option 1: Lanceur Intelligent (Recommandé)

```bash
python smart_launcher.py auto
```

### Option 2: Choix Manuel

```bash
python smart_launcher.py
```

### Option 3: Modes Spécifiques

```bash
# Interface desktop (si tkinter disponible)
python smart_launcher.py desktop

# Interface console (toujours disponible)
python smart_launcher.py console

# Tests système
python smart_launcher.py test

# Installation/Setup
python smart_launcher.py setup
```

## 🎮 Démo Complète

### 1. 🔧 Installation

```bash
# Installer les dépendances
python setup_windows.py
```

### 2. 🚀 Lancement

```bash
# Lancer l'interface optimale
python smart_launcher.py auto
```

### 3. 🎯 Test de Fonctionnalités

#### Analyse de Fichiers

1. Sélectionnez le dossier `demo_files`
2. Cliquez sur "🚀 Analyser le Dossier"
3. Observez l'analyse automatique dans l'onglet "Fichiers Analysés"

#### Recherche Intelligente

1. Tapez: `"trouve moi le scan de ma carte vitale"`
2. Cliquez sur "🤖 Rechercher"
3. Saisissez le mot de passe: `mon_secret_ultra_securise_2024`
4. Accédez au fichier déchiffré

#### Autres Exemples

- `"donne moi le pdf de cours d'histoire"` → Fichier public
- `"où est ma photo d'identité"` → Fichier chiffré
- `"liste les factures"` → Recherche dans les documents

## 🔐 Informations Importantes

### Mot de Passe du Vault

```
mon_secret_ultra_securise_2024
```

### Fichiers de Démonstration

- `demo_files/carte_vitale_scan.jpg` → 🔒 **Sensible** (chiffré)
- `demo_files/photo_identite.png` → 🔒 **Sensible** (chiffré)
- `demo_files/cours_histoire.pdf` → 📄 **Public**
- `demo_files/document_confidentiel.txt` → 🔒 **Sensible** (chiffré)

## 🛠️ Dépannage

### Problème: Python non trouvé

```bash
# Sur Windows, installer Python depuis python.org
# Cocher "Add Python to PATH"
```

### Problème: tkinter manquant

```bash
# Réinstaller Python avec l'option "tcl/tk and IDLE"
# Ou utiliser le mode console
python smart_launcher.py console
```

### Problème: Dépendances manquantes

```bash
# Exécuter le setup
python setup_windows.py
```

## 🎪 Scénarios de Démonstration

### Scénario 1: Analyse de Sécurité

1. **Objectif**: Montrer la détection automatique de PII
2. **Action**: Analyser le dossier `demo_files`
3. **Résultat**: Fichiers sensibles automatiquement chiffrés

### Scénario 2: Recherche Sécurisée

1. **Objectif**: Démontrer la recherche avec authentification
2. **Action**: Rechercher "carte vitale"
3. **Résultat**: Authentification requise pour accéder

### Scénario 3: Accès Contrôlé

1. **Objectif**: Montrer le déchiffrement sécurisé
2. **Action**: Saisir le bon mot de passe
3. **Résultat**: Accès au fichier déchiffré

### Scénario 4: Recherche Publique

1. **Objectif**: Démontrer l'accès direct aux fichiers publics
2. **Action**: Rechercher "cours histoire"
3. **Résultat**: Accès immédiat sans authentification

## 📊 Architecture du Système

```
🤖 Orchestrateur (Port 8001)
├── 📝 Agent NLP (Port 8002)      → Analyse texte, détection PII
├── 👁️ Agent Vision (Port 8003)    → Analyse images, reconnaissance
├── 🎵 Agent Audio (Port 8004)     → Analyse audio, transcription
├── 🔒 Agent Security (Port 8006)  → Chiffrement, authentification
└── 📁 File Manager (Port 8005)   → Consolidation, rapports
```

## 🎯 Fonctionnalités Démontrées

- ✅ **Analyse Multi-Format**: Texte, image, audio
- ✅ **Détection PII**: Automatique et intelligente
- ✅ **Chiffrement**: Sécurisation automatique
- ✅ **Recherche IA**: Langage naturel
- ✅ **Authentification**: Contrôle d'accès
- ✅ **Interface Desktop**: Moderne et intuitive
- ✅ **Vault Sécurisé**: Stockage chiffré
- ✅ **Audit Trail**: Traçabilité complète

## 🆘 Support

### Commandes Utiles

```bash
# Vérifier le statut
python test_system.py

# Démo console uniquement
python demo_console.py

# Système MCP seul
python simple_mcp_system.py
```

### Logs et Diagnostic

- Logs système dans l'onglet "Logs Système"
- Fichiers de log dans le dossier `logs/`
- Aide intégrée via le bouton "❓ Aide"

---

🎉 **Prêt pour la démonstration !** 🎉

Le système est maintenant configuré et prêt à être utilisé. Utilisez `python smart_launcher.py auto` pour démarrer automatiquement avec la meilleure interface disponible.
