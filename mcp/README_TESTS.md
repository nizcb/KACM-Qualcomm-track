# 🧪 Tests du Système MCP - Guide d'utilisation

## 📋 Vue d'ensemble

Ce dossier contient tous les fichiers nécessaires pour tester le système multi-agents MCP complet, incluant l'interface desktop, le backend avec orchestrateur, et l'intégration Llama3.

## 🗂️ Fichiers de test créés

### 📁 Données de test (`test_files/`)

- `document_sensible.txt` - Document avec données PII (carte vitale)
- `cours_histoire.txt` - Cours d'histoire (non sensible)
- `bulletin_paie.txt` - Bulletin de paie (sensible)
- `recette_cuisine.txt` - Recette de cuisine (non sensible)
- `ordonnance_medicale.json` - Ordonnance médicale (sensible)

### 🧪 Scripts de test

- `test_complete_system.py` - Test complet de tous les composants
- `desktop_test_interface.py` - Interface graphique de test
- `demo_llama_integration.py` - Démonstration avec simulation Llama3
- `launch_tests.py` - Lanceur pour tous les tests

## 🚀 Comment tester le système

### Option 1: Lancement rapide

```bash
# Lancer le menu de tests
python launch_tests.py
```

### Option 2: Tests individuels

#### 1. Test complet du système

```bash
python test_complete_system.py
```

**Teste:**

- ✅ Dépendances Python
- ✅ Système MCP simple
- ✅ Coffre-fort sécurisé
- ✅ Recherche intelligente
- ✅ Interface desktop
- ✅ API FastAPI
- ✅ Workflow complet

#### 2. Interface graphique

```bash
python desktop_test_interface.py
```

**Fonctionnalités:**

- 📁 Sélection et analyse de dossiers
- 🔍 Recherche intelligente
- 📊 Affichage des résultats
- 🔐 Gestion du coffre-fort
- 📝 Logs en temps réel

#### 3. Démonstration avec Llama3

```bash
python demo_llama_integration.py
```

**Scénarios:**

- 🗣️ Requêtes en langage naturel
- 🧠 Compréhension des intentions
- 🔐 Authentification automatique
- 📋 Génération de réponses

## 🎯 Scénarios de démonstration

### Scénario 1: Analyse de dossier

1. Lancer `desktop_test_interface.py`
2. Cliquer sur "Parcourir" et sélectionner le dossier `test_files`
3. Cliquer sur "Analyser"
4. Observer les résultats avec statut sensible/normal

### Scénario 2: Recherche intelligente

1. Dans l'interface, taper: "trouve moi ma carte vitale"
2. Cliquer sur "Rechercher"
3. Double-cliquer sur le résultat
4. Saisir le mot de passe pour l'authentification

### Scénario 3: Workflow complet

1. Lancer `demo_llama_integration.py`
2. Choisir le mode interactif
3. Tester différentes requêtes:
   - "Trouve-moi le scan de ma carte vitale"
   - "Je cherche le PDF du cours d'histoire"
   - "Peux-tu me donner mon bulletin de paie?"

## 🔧 Dépendances requises

### Minimales (pour les tests de base)

- Python 3.8+
- tkinter (inclus avec Python)
- sqlite3 (inclus avec Python)
- json, pathlib, threading (inclus)

### Complètes (pour toutes les fonctionnalités)

```bash
pip install -r requirements_fixed.txt
```

## 📊 Résultats attendus

### ✅ Tests qui doivent passer

- Dépendances Python de base
- Système MCP simple
- Coffre-fort sécurisé
- Recherche intelligente
- Interface desktop (si tkinter disponible)
- Workflow complet

### ⚠️ Tests qui peuvent échouer

- API FastAPI (si uvicorn/fastapi non installés)
- Fonctionnalités avancées (si dépendances manquantes)

## 🐛 Dépannage

### Problème: Interface ne s'affiche pas

- **Cause**: tkinter non installé
- **Solution**:

  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-tk

  # Windows: tkinter inclus avec Python
  ```

### Problème: API FastAPI échoue

- **Cause**: uvicorn/fastapi non installés
- **Solution**:
  ```bash
  pip install fastapi uvicorn
  ```

### Problème: Modules manquants

- **Solution**:
  ```bash
  pip install -r requirements_fixed.txt
  ```

## 🎪 Démonstration en live

### Préparation

1. Installer les dépendances
2. Lancer `launch_tests.py`
3. Exécuter "a" pour tous les tests
4. Lancer l'interface graphique avec "g"

### Présentation

1. **Montrer l'analyse automatique** (dossier → analyse → classification)
2. **Démontrer la recherche intelligente** (requête naturelle → résultats)
3. **Illustrer la sécurité** (fichier sensible → authentification)
4. **Workflow complet** (dépôt dossier → prompt → récupération fichier)

## 📝 Logs et rapports

- Logs en temps réel dans l'interface
- Rapports de tests dans `logs/`
- Fichiers chiffrés dans `vault/`
- Fichiers temporaires dans `temp/`

---

**🎯 Objectif**: Démontrer un système multi-agents complet et fonctionnel prêt pour la production!
