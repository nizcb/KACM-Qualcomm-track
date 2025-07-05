#!/usr/bin/env python3
"""
Security Agent Streamlit Interface
Interface web pour l'agent de sécurité

Usage:
    streamlit run security_interface.py
"""

import os
import sys
import subprocess
from pathlib import Path

# ================================
# INSTALLATION DES DÉPENDANCES
# ================================

def install_dependencies():
    """Installe les dépendances nécessaires"""
    print("🔍 Vérification des dépendances Streamlit...")
    
    packages = ["streamlit", "pandas"]
    
    for package in packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   📦 Installation de {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ Dépendances Streamlit OK")

# Installation des dépendances
install_dependencies()

# Imports après installation
import streamlit as st
import pandas as pd

# Import de l'agent de sécurité
from security_agent_core import SecurityAgent

# ================================
# INTERFACE STREAMLIT
# ================================

def main():
    """Interface principale Streamlit"""
    st.set_page_config(
        page_title="🔐 Security Agent",
        page_icon="🔐",
        layout="wide"
    )
    
    st.title("🔐 Security Agent - Chiffrement de Fichiers")
    st.markdown("---")
    
    # Initialiser l'agent
    if 'security_agent' not in st.session_state:
        with st.spinner("🚀 Initialisation de l'agent de sécurité..."):
            st.session_state.security_agent = SecurityAgent()
            st.session_state.security_agent.start_ollama()
    
    agent = st.session_state.security_agent
    
    # Sidebar pour les stats
    with st.sidebar:
        st.header("📊 Statistiques")
        stats = agent.get_stats()
        st.metric("Fichiers chiffrés", stats["total_files"])
        st.metric("Taille totale", f"{stats['total_size']:,} bytes")
        
        st.markdown("---")
        st.header("🔑 Authentification")
        st.info("Une phrase secrète est requise pour déchiffrer les fichiers")
        st.caption("Saisissez la phrase secrète dans l'onglet de déchiffrement")
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["🔒 Chiffrement", "🔓 Déchiffrement", "📁 Fichiers"])
    
    with tab1:
        st.header("🔒 Chiffrer un fichier")
        
        # Input pour le chemin du fichier
        file_path = st.text_input("📂 Chemin du fichier à chiffrer:", placeholder="/path/to/your/file.txt")
        
        if st.button("🔒 Chiffrer le fichier", type="primary"):
            if not file_path:
                st.error("❌ Veuillez saisir un chemin de fichier")
            elif not os.path.exists(file_path):
                st.error(f"❌ Fichier non trouvé: {file_path}")
            else:
                try:
                    with st.spinner("🔄 Chiffrement en cours..."):
                        # Chiffrer le fichier
                        result = agent.encrypt_file(file_path)
                        
                        # Afficher les résultats
                        st.success("✅ Fichier chiffré avec succès!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.info("📋 Informations du fichier")
                            st.write(f"**Nom:** {result['filename']}")
                            st.write(f"**UUID:** {result['uuid']}")
                            st.write(f"**Chemin chiffré:** {result['encrypted_path']}")
                        
                        with col2:
                            st.info("🤖 Explication IA")
                            st.write(result['explanation'])
                        
                        st.warning("⚠️ Gardez précieusement l'UUID pour pouvoir déchiffrer le fichier plus tard!")
                        
                except Exception as e:
                    st.error(f"❌ Erreur lors du chiffrement: {e}")
    
    with tab2:
        st.header("🔓 Déchiffrer un fichier")
        
        # Authentification
        secret_input = st.text_input("🔑 Phrase secrète:", type="password", placeholder="Saisissez la phrase secrète")
        
        if secret_input and agent.authenticate(secret_input):
            st.success("✅ Authentification réussie!")
            
            # Liste des fichiers disponibles
            files = agent.list_files()
            
            if files:
                file_options = {f"{file['filename']} ({file['uuid'][:8]}...)": file['uuid'] for file in files}
                selected_file = st.selectbox("📁 Sélectionnez un fichier à déchiffrer:", options=list(file_options.keys()))
                
                if st.button("🔓 Déchiffrer le fichier", type="primary"):
                    try:
                        with st.spinner("🔄 Déchiffrement en cours..."):
                            selected_uuid = file_options[selected_file]
                            result = agent.decrypt_file(selected_uuid)
                            
                            # Afficher les résultats
                            st.success("✅ Fichier déchiffré avec succès!")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.info("📋 Informations du fichier")
                                st.write(f"**Nom:** {result['filename']}")
                                st.write(f"**UUID:** {result['uuid']}")
                                st.write(f"**Chemin déchiffré:** {result['decrypted_path']}")
                            
                            with col2:
                                st.info("🤖 Explication IA")
                                st.write(result['explanation'])
                            
                    except Exception as e:
                        st.error(f"❌ Erreur lors du déchiffrement: {e}")
            else:
                st.info("📭 Aucun fichier chiffré dans le vault")
        
        elif secret_input:
            st.error("❌ Phrase secrète incorrecte!")
    
    with tab3:
        st.header("📁 Fichiers dans le vault")
        
        files = agent.list_files()
        
        if files:
            # Convertir en DataFrame pour affichage
            df = pd.DataFrame(files)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            df['file_size'] = df['file_size'].apply(lambda x: f"{x:,} bytes")
            
            st.dataframe(
                df[['filename', 'uuid', 'created_at', 'file_size']],
                use_container_width=True
            )
        else:
            st.info("📭 Aucun fichier dans le vault")

# ================================
# DÉMARRAGE
# ================================

if __name__ == "__main__":
    main()
