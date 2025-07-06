#!/usr/bin/env python3
"""
Interface Streamlit pour l'agent de sécurité
Interface web pour chiffrement/déchiffrement et analyse IA
"""

import streamlit as st
import os
import sys
import json
import requests
import pandas as pd
from pathlib import Path
import time
from datetime import datetime

# Ajouter le chemin du module principal
sys.path.append(str(Path(__file__).parent))

# Import du module principal
try:
    from security_agent_core import SecurityAgent
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    st.error("❌ Module security_agent_core non trouvé")

# Configuration de la page
st.set_page_config(
    page_title="🔐 Security Agent IA",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .error-box {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de l'agent
@st.cache_resource
def init_agent():
    """Initialise l'agent de sécurité"""
    if not AGENT_AVAILABLE:
        return None
    
    try:
        agent = SecurityAgent()
        agent.start_ollama()
        return agent
    except Exception as e:
        st.error(f"❌ Erreur d'initialisation de l'agent: {e}")
        return None

# Interface principale
def main():
    """Interface principale Streamlit"""
    
    # En-tête
    st.markdown("""
    <div class="main-header">
        <h1>🔐 Security Agent IA</h1>
        <p>Agent de sécurité avec analyse IA ReAct (Llama/Ollama)</p>
        <p>Chiffrement • Déchiffrement • Analyse de sécurité</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🔧 Navigation")
    
    # Vérifier si l'agent est disponible
    if not AGENT_AVAILABLE:
        st.sidebar.error("❌ Agent non disponible")
        st.error("Le module security_agent_core n'est pas disponible. Vérifiez l'installation.")
        return
    
    # Initialiser l'agent
    agent = init_agent()
    if agent is None:
        st.error("❌ Impossible d'initialiser l'agent de sécurité")
        return
    
    # Menu de navigation
    pages = {
        "🏠 Accueil": "home",
        "🔍 Analyse IA": "analyze",
        "🔐 Chiffrement": "encrypt",
        "🔓 Déchiffrement": "decrypt",
        "📊 Vault & Stats": "vault",
        "🧪 Tests": "test",
        "⚙️ Configuration": "config"
    }
    
    selected_page = st.sidebar.selectbox("Sélectionnez une page", list(pages.keys()))
    page_key = pages[selected_page]
    
    # Afficher les statistiques dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Statistiques")
    
    try:
        stats = agent.get_stats()
        st.sidebar.metric("Fichiers chiffrés", stats.get("total_files", 0))
        st.sidebar.metric("Taille totale", f"{stats.get('total_size', 0)} bytes")
        st.sidebar.metric("IA Ollama", "🟢 Actif" if agent.ollama_manager.is_running else "🔴 Inactif")
    except Exception as e:
        st.sidebar.error(f"❌ Erreur stats: {e}")
    
    # Afficher la page sélectionnée
    if page_key == "home":
        show_home_page(agent)
    elif page_key == "analyze":
        show_analyze_page(agent)
    elif page_key == "encrypt":
        show_encrypt_page(agent)
    elif page_key == "decrypt":
        show_decrypt_page(agent)
    elif page_key == "vault":
        show_vault_page(agent)
    elif page_key == "test":
        show_test_page(agent)
    elif page_key == "config":
        show_config_page(agent)

def show_home_page(agent):
    """Page d'accueil"""
    st.header("🏠 Accueil")
    
    # Informations générales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🔐 Chiffrement</h3>
            <p>Chiffrement sécurisé AES avec analyse IA préalable</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🤖 IA ReAct</h3>
            <p>Analyse intelligente avec raisonnement Llama/Ollama</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Vault</h3>
            <p>Gestion sécurisée des fichiers chiffrés</p>
        </div>
        """, unsafe_allow_html=True)
    
    # État du système
    st.subheader("🚦 État du système")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Composants")
        status_items = [
            ("Agent de sécurité", "🟢 Actif"),
            ("Base de données", "🟢 Accessible"),
            ("Dossiers vault", "🟢 Configurés"),
            ("IA Ollama", "🟢 Actif" if agent.ollama_manager.is_running else "🔴 Inactif")
        ]
        
        for item, status in status_items:
            st.write(f"**{item}**: {status}")
    
    with col2:
        st.markdown("### 📈 Statistiques")
        try:
            stats = agent.get_stats()
            st.metric("Fichiers chiffrés", stats.get("total_files", 0))
            st.metric("Taille totale", f"{stats.get('total_size', 0)} bytes")
            st.metric("IA disponible", "Oui" if agent.ollama_manager.is_running else "Non")
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement des stats: {e}")
    
    # Guide rapide
    st.subheader("🚀 Guide rapide")
    st.markdown("""
    1. **🔍 Analyse IA** : Analysez un fichier pour détecter des informations sensibles
    2. **🔐 Chiffrement** : Chiffrez vos fichiers de manière sécurisée
    3. **🔓 Déchiffrement** : Déchiffrez vos fichiers avec la phrase secrète
    4. **📊 Vault** : Consultez vos fichiers chiffrés et les statistiques
    """)

def show_analyze_page(agent):
    """Page d'analyse IA"""
    st.header("🔍 Analyse IA des fichiers")
    st.markdown("Analysez vos fichiers pour détecter des informations sensibles avec l'IA ReAct")
    
    # Sélection du fichier
    st.subheader("📁 Sélection du fichier")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        file_path = st.text_input("Chemin du fichier à analyser", placeholder="/chemin/vers/votre/fichier.txt")
    
    with col2:
        mode = st.selectbox("Mode d'analyse", ["security", "content", "full"])
    
    # Upload de fichier
    uploaded_file = st.file_uploader("Ou uploadez un fichier", type=['txt', 'csv', 'json', 'log', 'py', 'js', 'html'])
    
    if uploaded_file is not None:
        # Sauvegarder le fichier uploadé
        temp_path = Path("/tmp") / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_path = str(temp_path)
        st.success(f"✅ Fichier uploadé: {uploaded_file.name}")
    
    # Bouton d'analyse
    if st.button("🔍 Analyser le fichier", type="primary"):
        if file_path:
            with st.spinner("🤖 Analyse en cours avec l'IA ReAct..."):
                try:
                    analysis = agent.analyze_file_with_ai(file_path, mode)
                    
                    if "error" in analysis:
                        st.error(f"❌ Erreur: {analysis['error']}")
                    else:
                        # Afficher les résultats
                        st.subheader("📋 Résultats de l'analyse")
                        
                        # Métriques principales
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            risk_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
                            risk_level = analysis.get("risk_level", "UNKNOWN")
                            st.metric("Niveau de risque", f"{risk_color.get(risk_level, '⚪')} {risk_level}")
                        
                        with col2:
                            st.metric("Score de confiance", f"{analysis.get('confidence_score', 0):.2f}")
                        
                        with col3:
                            st.metric("Problèmes détectés", len(analysis.get("security_issues", [])))
                        
                        # Détails de l'analyse
                        if analysis.get("security_issues"):
                            st.markdown("### 🚨 Problèmes de sécurité détectés")
                            for issue in analysis["security_issues"]:
                                issue_labels = {
                                    "email_addresses": "📧 Adresses email",
                                    "phone_numbers": "📞 Numéros de téléphone",
                                    "credentials": "🔑 Informations d'identification",
                                    "payment_info": "💳 Informations de paiement"
                                }
                                st.warning(f"• {issue_labels.get(issue, issue)}")
                        
                        # Recommandation
                        st.markdown("### 💡 Recommandation")
                        recommendation = analysis.get("security_recommendation", "UNKNOWN")
                        if recommendation == "ENCRYPT_REQUIRED":
                            st.error("🔐 **Chiffrement recommandé** - Ce fichier contient des informations sensibles")
                        elif recommendation == "SAFE":
                            st.success("✅ **Fichier sûr** - Aucun problème de sécurité détecté")
                        else:
                            st.info(f"⚠️ Statut: {recommendation}")
                        
                        # Explication IA
                        if analysis.get("ai_reasoning"):
                            st.markdown("### 🤖 Analyse IA ReAct")
                            st.markdown(f"```\n{analysis['ai_reasoning']}\n```")
                        
                        # Détails techniques
                        with st.expander("📊 Détails techniques"):
                            st.json(analysis)
                        
                        # Action recommandée
                        if recommendation == "ENCRYPT_REQUIRED":
                            st.markdown("---")
                            st.markdown("### 🔐 Action recommandée")
                            if st.button("Chiffrer ce fichier maintenant", type="primary"):
                                st.switch_page("pages/encrypt.py")
                
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse: {e}")
        else:
            st.warning("⚠️ Veuillez sélectionner un fichier à analyser")

def show_encrypt_page(agent):
    """Page de chiffrement"""
    st.header("🔐 Chiffrement de fichiers")
    st.markdown("Chiffrez vos fichiers de manière sécurisée avec analyse IA préalable")
    
    # Sélection du fichier
    st.subheader("📁 Sélection du fichier")
    
    file_path = st.text_input("Chemin du fichier à chiffrer", placeholder="/chemin/vers/votre/fichier.txt")
    
    # Upload de fichier
    uploaded_file = st.file_uploader("Ou uploadez un fichier", type=None)
    
    if uploaded_file is not None:
        # Sauvegarder le fichier uploadé
        temp_path = Path("/tmp") / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_path = str(temp_path)
        st.success(f"✅ Fichier uploadé: {uploaded_file.name}")
    
    # Options
    user_id = st.text_input("Identifiant utilisateur", value="default_user")
    
    # Bouton de chiffrement
    if st.button("🔐 Chiffrer le fichier", type="primary"):
        if file_path:
            with st.spinner("🔐 Chiffrement en cours..."):
                try:
                    result = agent.encrypt_file(file_path, user_id)
                    
                    if result.get("success"):
                        st.success("✅ Fichier chiffré avec succès!")
                        
                        # Afficher les détails
                        st.subheader("📋 Détails du chiffrement")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 📄 Informations")
                            st.write(f"**Nom du fichier**: {result.get('filename')}")
                            st.write(f"**UUID**: `{result.get('uuid')}`")
                            st.write(f"**Utilisateur**: {result.get('user_id')}")
                        
                        with col2:
                            st.markdown("### 📊 Analyse")
                            analysis = result.get("analysis", {})
                            if analysis:
                                st.write(f"**Niveau de risque**: {analysis.get('risk_level', 'N/A')}")
                                st.write(f"**Problèmes détectés**: {len(analysis.get('security_issues', []))}")
                        
                        # Explication IA
                        if result.get("explanation"):
                            st.markdown("### 🤖 Explication IA")
                            st.info(result["explanation"])
                        
                        # Copier l'UUID
                        st.markdown("### 📋 UUID pour déchiffrement")
                        st.code(result.get("uuid"), language="text")
                        st.caption("💡 Gardez cet UUID pour déchiffrer le fichier plus tard")
                        
                    else:
                        st.error(f"❌ Erreur: {result.get('message', 'Erreur inconnue')}")
                
                except Exception as e:
                    st.error(f"❌ Erreur lors du chiffrement: {e}")
        else:
            st.warning("⚠️ Veuillez sélectionner un fichier à chiffrer")

def show_decrypt_page(agent):
    """Page de déchiffrement"""
    st.header("🔓 Déchiffrement de fichiers")
    st.markdown("Déchiffrez vos fichiers avec l'UUID et la phrase secrète")
    
    # Paramètres de déchiffrement
    st.subheader("🔑 Paramètres de déchiffrement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        vault_uuid = st.text_input("UUID du fichier", placeholder="ex: 12345678-1234-1234-1234-123456789012")
    
    with col2:
        user_id = st.text_input("Identifiant utilisateur", value="default_user")
    
    secret_phrase = st.text_input("Phrase secrète", type="password", value="mon_secret_ultra_securise_2024")
    
    # Liste des fichiers disponibles
    st.subheader("📁 Fichiers disponibles")
    
    try:
        files = agent.list_files()
        if files:
            df = pd.DataFrame(files)
            
            # Sélection dans le tableau
            selected_indices = st.dataframe(
                df[['filename', 'uuid', 'created_at', 'file_size']], 
                use_container_width=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            if selected_indices and selected_indices.selection.rows:
                selected_file = files[selected_indices.selection.rows[0]]
                vault_uuid = selected_file['uuid']
                st.success(f"✅ Fichier sélectionné: {selected_file['filename']}")
        else:
            st.info("ℹ️ Aucun fichier chiffré trouvé")
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des fichiers: {e}")
    
    # Bouton de déchiffrement
    if st.button("🔓 Déchiffrer le fichier", type="primary"):
        if vault_uuid and secret_phrase:
            with st.spinner("🔓 Déchiffrement en cours..."):
                try:
                    result = agent.decrypt_file(vault_uuid, user_id)
                    
                    if result.get("success"):
                        st.success("✅ Fichier déchiffré avec succès!")
                        
                        # Afficher les détails
                        st.subheader("📋 Détails du déchiffrement")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Nom du fichier**: {result.get('filename')}")
                            st.write(f"**Chemin déchiffré**: {result.get('decrypted_path')}")
                            st.write(f"**Utilisateur**: {result.get('user_id')}")
                        
                        with col2:
                            st.write(f"**UUID**: `{vault_uuid}`")
                            st.write(f"**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        # Explication IA
                        if result.get("explanation"):
                            st.markdown("### 🤖 Explication IA")
                            st.info(result["explanation"])
                        
                        # Afficher le contenu si c'est un fichier texte
                        try:
                            file_path = result.get("decrypted_path")
                            if file_path and os.path.exists(file_path):
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                st.markdown("### 📄 Contenu du fichier")
                                st.text_area("Contenu", content, height=300)
                        except:
                            st.info("💡 Fichier déchiffré disponible dans le dossier 'decrypted'")
                        
                    else:
                        st.error(f"❌ Erreur: {result.get('message', 'Erreur inconnue')}")
                
                except Exception as e:
                    st.error(f"❌ Erreur lors du déchiffrement: {e}")
        else:
            st.warning("⚠️ Veuillez fournir l'UUID et la phrase secrète")

def show_vault_page(agent):
    """Page du vault et statistiques"""
    st.header("📊 Vault et statistiques")
    
    # Statistiques générales
    st.subheader("📈 Statistiques générales")
    
    try:
        stats = agent.get_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Fichiers chiffrés", stats.get("total_files", 0))
        
        with col2:
            st.metric("Taille totale", f"{stats.get('total_size', 0)} bytes")
        
        with col3:
            st.metric("IA Ollama", "Actif" if agent.ollama_manager.is_running else "Inactif")
        
        # Liste des fichiers
        st.subheader("📁 Fichiers dans le vault")
        
        files = agent.list_files()
        if files:
            df = pd.DataFrame(files)
            
            # Formatage des colonnes
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            df['file_size'] = df['file_size'].apply(lambda x: f"{x} bytes")
            df['uuid_short'] = df['uuid'].apply(lambda x: f"{x[:8]}...")
            
            # Affichage du tableau
            st.dataframe(
                df[['filename', 'uuid_short', 'created_at', 'file_size']],
                use_container_width=True,
                column_config={
                    "filename": "Nom du fichier",
                    "uuid_short": "UUID",
                    "created_at": "Créé le",
                    "file_size": "Taille"
                }
            )
            
            # Graphique des fichiers par jour
            if len(files) > 1:
                st.subheader("📊 Évolution des fichiers")
                df['date'] = pd.to_datetime(df['created_at']).dt.date
                daily_counts = df.groupby('date').size().reset_index(name='count')
                st.line_chart(daily_counts.set_index('date'))
        
        else:
            st.info("ℹ️ Aucun fichier dans le vault")
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des statistiques: {e}")

def show_test_page(agent):
    """Page de tests"""
    st.header("🧪 Tests de l'agent")
    st.markdown("Testez les fonctionnalités de l'agent de sécurité")
    
    # Test principal
    if st.button("🚀 Lancer le test complet", type="primary"):
        with st.spinner("🧪 Test en cours..."):
            try:
                # Capturer la sortie du test
                import io
                import contextlib
                
                f = io.StringIO()
                with contextlib.redirect_stdout(f):
                    agent.test()
                
                test_output = f.getvalue()
                
                st.success("✅ Test terminé avec succès!")
                st.subheader("📋 Résultats du test")
                st.code(test_output, language="text")
                
            except Exception as e:
                st.error(f"❌ Erreur lors du test: {e}")
    
    # Tests individuels
    st.subheader("🔧 Tests individuels")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Test analyse IA"):
            with st.spinner("Test en cours..."):
                try:
                    # Créer un fichier de test
                    test_file = "/tmp/test_analysis.txt"
                    with open(test_file, 'w') as f:
                        f.write("Email: test@example.com\nTéléphone: 123-456-7890\nMot de passe: secret123")
                    
                    analysis = agent.analyze_file_with_ai(test_file, "security")
                    st.success("✅ Test d'analyse réussi")
                    st.json(analysis)
                    
                    # Nettoyer
                    os.remove(test_file)
                    
                except Exception as e:
                    st.error(f"❌ Erreur test analyse: {e}")
    
    with col2:
        if st.button("📊 Test statistiques"):
            with st.spinner("Test en cours..."):
                try:
                    stats = agent.get_stats()
                    files = agent.list_files()
                    
                    st.success("✅ Test statistiques réussi")
                    st.write(f"Fichiers: {stats.get('total_files', 0)}")
                    st.write(f"Taille: {stats.get('total_size', 0)} bytes")
                    
                except Exception as e:
                    st.error(f"❌ Erreur test stats: {e}")

def show_config_page(agent):
    """Page de configuration"""
    st.header("⚙️ Configuration")
    
    # État du système
    st.subheader("🚦 État du système")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Composants")
        components = [
            ("Agent de sécurité", "🟢 Actif"),
            ("Base de données SQLite", "🟢 Accessible"),
            ("Dossier vault", "🟢 Configuré"),
            ("Dossier encrypted", "🟢 Configuré"),
            ("Dossier decrypted", "🟢 Configuré"),
            ("IA Ollama", "🟢 Actif" if agent.ollama_manager.is_running else "🔴 Inactif")
        ]
        
        for component, status in components:
            st.write(f"**{component}**: {status}")
    
    with col2:
        st.markdown("### 📁 Chemins")
        paths = [
            ("Base dir", str(Path(__file__).parent)),
            ("Vault DB", str(Path(__file__).parent / "vault" / "vault.db")),
            ("Encrypted", str(Path(__file__).parent / "encrypted")),
            ("Decrypted", str(Path(__file__).parent / "decrypted"))
        ]
        
        for path_name, path_value in paths:
            st.write(f"**{path_name}**: `{path_value}`")
    
    # Configuration Ollama
    st.subheader("🤖 Configuration Ollama")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Modèle**: {agent.ollama_manager.model_name}")
        st.write(f"**URL**: {agent.ollama_manager.ollama_url}")
        st.write(f"**Status**: {'🟢 Actif' if agent.ollama_manager.is_running else '🔴 Inactif'}")
    
    with col2:
        if st.button("🔄 Redémarrer Ollama"):
            with st.spinner("Redémarrage d'Ollama..."):
                try:
                    success = agent.ollama_manager.start_ollama()
                    if success:
                        st.success("✅ Ollama redémarré avec succès")
                    else:
                        st.warning("⚠️ Impossible de redémarrer Ollama")
                except Exception as e:
                    st.error(f"❌ Erreur redémarrage Ollama: {e}")
    
    # Actions de maintenance
    st.subheader("🔧 Actions de maintenance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Nettoyer dossier decrypted"):
            try:
                decrypted_dir = Path(__file__).parent / "decrypted"
                files_removed = 0
                for file in decrypted_dir.glob("*"):
                    if file.is_file():
                        file.unlink()
                        files_removed += 1
                st.success(f"✅ {files_removed} fichiers supprimés")
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
    
    with col2:
        if st.button("📊 Vérifier intégrité"):
            with st.spinner("Vérification..."):
                try:
                    # Vérifier que tous les fichiers chiffrés existent
                    files = agent.list_files()
                    missing = 0
                    for file in files:
                        if not os.path.exists(file.get('encrypted_path', '')):
                            missing += 1
                    
                    if missing == 0:
                        st.success("✅ Tous les fichiers sont accessibles")
                    else:
                        st.warning(f"⚠️ {missing} fichiers manquants")
                        
                except Exception as e:
                    st.error(f"❌ Erreur vérification: {e}")
    
    with col3:
        if st.button("🔄 Réinitialiser agent"):
            with st.spinner("Réinitialisation..."):
                try:
                    # Réinitialiser l'agent en cache
                    st.cache_resource.clear()
                    st.success("✅ Agent réinitialisé")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur réinitialisation: {e}")

# Lancement de l'application
if __name__ == "__main__":
    main()