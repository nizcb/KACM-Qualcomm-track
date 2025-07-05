#!/usr/bin/env python3
"""
Interface Streamlit pour tester le Security Agent MVP
Interface web interactive pour visualiser et tester toutes les fonctionnalités.
"""

import streamlit as st
import requests
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration
SECURITY_AGENT_URL = "http://127.0.0.1:8001"

# Configuration de la page
st.set_page_config(
    page_title="Security Agent MVP - Interface Test",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e8b57;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_agent_health():
    """Vérifie si l'agent est en fonctionnement"""
    try:
        response = requests.get(f"{SECURITY_AGENT_URL}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def get_vault_status():
    """Récupère le statut du vault"""
    try:
        response = requests.get(f"{SECURITY_AGENT_URL}/vault_status", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def encrypt_file(file_path, owner="streamlit_user", policy="AES256"):
    """Chiffre un fichier"""
    try:
        payload = {
            "file_path": file_path,
            "owner": owner,
            "policy": policy
        }
        response = requests.post(f"{SECURITY_AGENT_URL}/encrypt", json=payload, timeout=30)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {"error": str(e)}

def decrypt_file(vault_uuid, output_path=None):
    """Déchiffre un fichier"""
    try:
        payload = {
            "vault_uuid": vault_uuid,
            "output_path": output_path
        }
        response = requests.post(f"{SECURITY_AGENT_URL}/decrypt", json=payload, timeout=30)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {"error": str(e)}

def process_mcp_task(files, owner="streamlit_user", policy="AES256"):
    """Traite une tâche MCP"""
    try:
        payload = {
            "thread_id": f"streamlit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "sender": "streamlit_interface",
            "type": "task.security",
            "payload": {
                "files": files,
                "owner": owner,
                "policy": policy
            }
        }
        response = requests.post(f"{SECURITY_AGENT_URL}/mcp/task", json=payload, timeout=30)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {"error": str(e)}

# En-tête principal
st.markdown('<h1 class="main-header">🔐 Security Agent MVP - Interface Test</h1>', unsafe_allow_html=True)

# Sidebar pour la navigation
st.sidebar.title("Navigation")
pages = {
    "🏠 Accueil": "home",
    "🔐 Chiffrement": "encrypt",
    "🔓 Déchiffrement": "decrypt",
    "📊 Statut Vault": "vault_status",
    "🔄 Test MCP": "mcp_test",
    "🏥 Santé Agent": "health"
}

selected_page = st.sidebar.selectbox("Sélectionnez une page", list(pages.keys()))
current_page = pages[selected_page]

# Vérification de la santé de l'agent
is_healthy, health_data = check_agent_health()

if not is_healthy:
    st.error("❌ L'agent Security Agent n'est pas accessible. Assurez-vous qu'il est démarré sur http://127.0.0.1:8001")
    st.info("💡 Pour démarrer l'agent, exécutez: `python security_agent_consolidated.py`")
    st.stop()

# Indicateur de santé dans la sidebar
if health_data:
    st.sidebar.success("✅ Agent en ligne")
    st.sidebar.json(health_data)
else:
    st.sidebar.warning("⚠️ Problème de santé détecté")

# === PAGE ACCUEIL ===
if current_page == "home":
    st.markdown('<h2 class="section-header">🏠 Accueil</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Fonctionnalités disponibles")
        st.markdown("""
        - **🔐 Chiffrement**: Chiffrez vos fichiers avec AES-256
        - **🔓 Déchiffrement**: Déchiffrez vos fichiers depuis le vault
        - **📊 Statut Vault**: Visualisez le contenu du vault
        - **🔄 Test MCP**: Testez l'intégration MCP avec traitement par lot
        - **🏥 Santé Agent**: Vérifiez l'état de santé de l'agent
        """)
    
    with col2:
        st.markdown("### 🛠️ Architecture")
        st.markdown("""
        L'agent Security Agent MVP utilise:
        - **Chiffrement AES-256** avec salt unique par fichier
        - **Vault SQLite** pour la gestion des métadonnées
        - **Keyring** pour la gestion sécurisée des clés
        - **FastAPI** pour l'API REST
        - **MCP** pour l'intégration avec l'orchestrateur
        """)
    
    # Statistiques rapides
    vault_data = get_vault_status()
    if vault_data:
        st.markdown("### 📈 Statistiques rapides")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Fichiers chiffrés", vault_data["total_files"])
        
        with col2:
            size_mb = vault_data["total_size_bytes"] / (1024 * 1024)
            st.metric("Taille totale", f"{size_mb:.2f} MB")
        
        with col3:
            st.metric("Répertoire vault", vault_data["vault_path"].split("/")[-1])

# === PAGE CHIFFREMENT ===
elif current_page == "encrypt":
    st.markdown('<h2 class="section-header">🔐 Chiffrement de fichiers</h2>', unsafe_allow_html=True)
    
    # Upload de fichier
    uploaded_file = st.file_uploader("Sélectionnez un fichier à chiffrer", type=None)
    
    if uploaded_file is not None:
        # Paramètres de chiffrement
        col1, col2 = st.columns(2)
        
        with col1:
            owner = st.text_input("Propriétaire", value="streamlit_user")
        
        with col2:
            policy = st.selectbox("Politique de chiffrement", ["AES256"])
        
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        st.info(f"📁 Fichier préparé: {uploaded_file.name} ({len(uploaded_file.getvalue())} bytes)")
        
        # Bouton de chiffrement
        if st.button("🔐 Chiffrer le fichier", type="primary"):
            with st.spinner("Chiffrement en cours..."):
                success, result = encrypt_file(tmp_file_path, owner, policy)
            
            if success:
                st.success("✅ Fichier chiffré avec succès!")
                
                # Afficher les résultats
                st.markdown("### 📊 Résultats du chiffrement")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Informations du fichier:**")
                    st.code(f"""
UUID Vault: {result['vault_uuid']}
Chemin original: {result['original_path']}
Propriétaire: {result['owner']}
Politique: {result['policy']}
Date création: {result['created_at']}
                    """)
                
                with col2:
                    st.markdown("**Métadonnées techniques:**")
                    st.code(f"""
Chemin vault: {result['vault_path']}
Hash SHA-256: {result['file_hash'][:32]}...
                    """)
                
                st.json(result)
                
            else:
                st.error(f"❌ Erreur lors du chiffrement: {result}")
        
        # Nettoyer le fichier temporaire
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

# === PAGE DÉCHIFFREMENT ===
elif current_page == "decrypt":
    st.markdown('<h2 class="section-header">🔓 Déchiffrement de fichiers</h2>', unsafe_allow_html=True)
    
    # Récupérer la liste des fichiers dans le vault
    vault_data = get_vault_status()
    
    if vault_data and vault_data["entries"]:
        st.markdown("### 📋 Fichiers disponibles dans le vault")
        
        # Créer un DataFrame pour l'affichage
        df_entries = pd.DataFrame(vault_data["entries"])
        
        # Sélection du fichier
        selected_uuid = st.selectbox(
            "Sélectionnez un fichier à déchiffrer",
            options=df_entries["vault_uuid"].tolist(),
            format_func=lambda x: f"{x} - {df_entries[df_entries['vault_uuid']==x]['original_path'].iloc[0].split('/')[-1]}"
        )
        
        if selected_uuid:
            # Afficher les détails du fichier sélectionné
            selected_entry = df_entries[df_entries["vault_uuid"] == selected_uuid].iloc[0]
            
            st.markdown("### 📄 Détails du fichier sélectionné")
            col1, col2 = st.columns(2)
            
            with col1:
                st.code(f"""
UUID: {selected_entry['vault_uuid']}
Nom original: {selected_entry['original_path'].split('/')[-1]}
Propriétaire: {selected_entry['owner']}
Politique: {selected_entry['policy']}
                """)
            
            with col2:
                st.code(f"""
Chemin vault: {selected_entry['vault_path']}
Hash: {selected_entry['file_hash'][:32]}...
Date création: {selected_entry['created_at']}
                """)
            
            # Chemin de sortie optionnel
            output_path = st.text_input("Chemin de sortie (optionnel)", placeholder="Laissez vide pour utiliser le répertoire par défaut")
            
            # Bouton de déchiffrement
            if st.button("🔓 Déchiffrer le fichier", type="primary"):
                with st.spinner("Déchiffrement en cours..."):
                    success, result = decrypt_file(selected_uuid, output_path if output_path else None)
                
                if success:
                    st.success("✅ Fichier déchiffré avec succès!")
                    
                    st.markdown("### 📊 Résultats du déchiffrement")
                    st.code(f"""
UUID Vault: {result['vault_uuid']}
Chemin original: {result['original_path']}
Chemin déchiffré: {result['decrypted_path']}
Propriétaire: {result['owner']}
                    """)
                    
                    # Proposer le téléchargement si le fichier existe
                    if os.path.exists(result['decrypted_path']):
                        with open(result['decrypted_path'], 'rb') as f:
                            file_data = f.read()
                        
                        st.download_button(
                            label="📥 Télécharger le fichier déchiffré",
                            data=file_data,
                            file_name=os.path.basename(result['original_path']),
                            mime="application/octet-stream"
                        )
                    
                    st.json(result)
                    
                else:
                    st.error(f"❌ Erreur lors du déchiffrement: {result}")
    
    else:
        st.info("📭 Aucun fichier dans le vault. Chiffrez d'abord des fichiers.")

# === PAGE STATUT VAULT ===
elif current_page == "vault_status":
    st.markdown('<h2 class="section-header">📊 Statut du Vault</h2>', unsafe_allow_html=True)
    
    vault_data = get_vault_status()
    
    if vault_data:
        # Métriques principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📁 Fichiers totaux", vault_data["total_files"])
        
        with col2:
            size_mb = vault_data["total_size_bytes"] / (1024 * 1024)
            st.metric("💾 Taille totale", f"{size_mb:.2f} MB")
        
        with col3:
            st.metric("📂 Répertoire vault", vault_data["vault_path"].split("/")[-1])
        
        # Graphiques si on a des données
        if vault_data["entries"]:
            df_entries = pd.DataFrame(vault_data["entries"])
            
            # Graphique par propriétaire
            st.markdown("### 👥 Répartition par propriétaire")
            owner_counts = df_entries["owner"].value_counts()
            fig_owners = px.pie(
                values=owner_counts.values,
                names=owner_counts.index,
                title="Fichiers par propriétaire"
            )
            st.plotly_chart(fig_owners, use_container_width=True)
            
            # Graphique par politique
            st.markdown("### 🔒 Répartition par politique de chiffrement")
            policy_counts = df_entries["policy"].value_counts()
            fig_policies = px.bar(
                x=policy_counts.index,
                y=policy_counts.values,
                title="Fichiers par politique de chiffrement"
            )
            st.plotly_chart(fig_policies, use_container_width=True)
            
            # Timeline des créations
            st.markdown("### 📅 Timeline des créations")
            df_entries["created_at"] = pd.to_datetime(df_entries["created_at"])
            df_entries["date"] = df_entries["created_at"].dt.date
            
            daily_counts = df_entries.groupby("date").size().reset_index(name="count")
            fig_timeline = px.line(
                daily_counts,
                x="date",
                y="count",
                title="Fichiers créés par jour"
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Tableau détaillé
            st.markdown("### 📋 Liste détaillée des fichiers")
            
            # Préparer l'affichage du tableau
            display_df = df_entries.copy()
            display_df["nom_fichier"] = display_df["original_path"].apply(lambda x: x.split("/")[-1])
            display_df["hash_court"] = display_df["file_hash"].apply(lambda x: x[:12] + "...")
            display_df["date_creation"] = display_df["created_at"].dt.strftime("%Y-%m-%d %H:%M")
            
            st.dataframe(
                display_df[["vault_uuid", "nom_fichier", "owner", "policy", "hash_court", "date_creation"]],
                use_container_width=True
            )
        
        else:
            st.info("📭 Le vault est vide. Chiffrez des fichiers pour voir les statistiques.")
    
    else:
        st.error("❌ Impossible de récupérer le statut du vault")

# === PAGE TEST MCP ===
elif current_page == "mcp_test":
    st.markdown('<h2 class="section-header">🔄 Test MCP (Model Context Protocol)</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Cette page permet de tester l'intégration MCP en simulant une requête du File Manager
    pour chiffrer plusieurs fichiers en une seule fois.
    """)
    
    # Upload multiple files
    uploaded_files = st.file_uploader(
        "Sélectionnez plusieurs fichiers à chiffrer via MCP",
        accept_multiple_files=True,
        type=None
    )
    
    if uploaded_files:
        st.markdown(f"### 📁 Fichiers sélectionnés ({len(uploaded_files)})")
        
        # Afficher la liste des fichiers
        for i, file in enumerate(uploaded_files):
            st.markdown(f"**{i+1}.** {file.name} ({len(file.getvalue())} bytes)")
        
        # Paramètres MCP
        col1, col2 = st.columns(2)
        
        with col1:
            owner = st.text_input("Propriétaire MCP", value="mcp_user")
        
        with col2:
            policy = st.selectbox("Politique MCP", ["AES256"])
        
        # Sauvegarder tous les fichiers temporairement
        temp_files = []
        for file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.name}") as tmp_file:
                tmp_file.write(file.getvalue())
                temp_files.append(tmp_file.name)
        
        # Bouton de traitement MCP
        if st.button("🔄 Traiter via MCP", type="primary"):
            with st.spinner("Traitement MCP en cours..."):
                success, result = process_mcp_task(temp_files, owner, policy)
            
            if success:
                st.success("✅ Traitement MCP réussi!")
                
                # Afficher les résultats
                st.markdown("### 📊 Résultats du traitement MCP")
                
                st.markdown("**Métadonnées de la réponse:**")
                st.code(f"""
Thread ID: {result['thread_id']}
Sender: {result['sender']}
Type: {result['type']}
Fichiers traités: {len(result['payload']['vault'])}
                """)
                
                # Tableau des fichiers traités
                if result['payload']['vault']:
                    st.markdown("**Fichiers chiffrés:**")
                    
                    vault_entries = result['payload']['vault']
                    df_mcp = pd.DataFrame(vault_entries)
                    
                    # Préparer l'affichage
                    display_df = df_mcp.copy()
                    display_df["nom_fichier"] = display_df["orig"].apply(lambda x: x.split("/")[-1])
                    display_df["hash_court"] = display_df["hash"].apply(lambda x: x.split(":")[-1][:12] + "...")
                    
                    st.dataframe(
                        display_df[["uuid", "nom_fichier", "hash_court", "timestamp"]],
                        use_container_width=True
                    )
                    
                    # Graphique de répartition
                    st.markdown("### 📈 Visualisation des résultats")
                    fig = go.Figure(data=[
                        go.Bar(
                            x=list(range(1, len(vault_entries) + 1)),
                            y=[len(entry["orig"]) for entry in vault_entries],
                            text=[entry["orig"].split("/")[-1] for entry in vault_entries],
                            textposition="outside"
                        )
                    ])
                    fig.update_layout(
                        title="Longueur des chemins de fichiers traités",
                        xaxis_title="Fichier #",
                        yaxis_title="Longueur du chemin"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # JSON complet
                st.markdown("### 🔍 Réponse JSON complète")
                st.json(result)
                
            else:
                st.error(f"❌ Erreur lors du traitement MCP: {result}")
        
        # Nettoyer les fichiers temporaires
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    else:
        st.info("📤 Sélectionnez des fichiers pour tester le traitement MCP par lot")

# === PAGE SANTÉ AGENT ===
elif current_page == "health":
    st.markdown('<h2 class="section-header">🏥 Santé de l\'Agent</h2>', unsafe_allow_html=True)
    
    # Récupérer les données de santé
    is_healthy, health_data = check_agent_health()
    
    if is_healthy and health_data:
        # Statut global
        status = health_data.get("status", "unknown")
        if status == "healthy":
            st.success("✅ Agent en bonne santé")
        else:
            st.error("❌ Agent en mauvaise santé")
        
        # Métriques principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🕒 Dernière vérification", health_data.get("timestamp", "N/A"))
        
        with col2:
            st.metric("📁 Fichiers dans le vault", health_data.get("total_files", 0))
        
        with col3:
            st.metric("📂 Répertoire vault", health_data.get("vault_path", "N/A").split("/")[-1])
        
        # Statut des composants
        st.markdown("### 🔧 Statut des composants")
        
        components = health_data.get("components", {})
        
        for component, status in components.items():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{component.replace('_', ' ').title()}**")
            
            with col2:
                if status:
                    st.success("✅ OK")
                else:
                    st.error("❌ KO")
        
        # Graphique de santé
        st.markdown("### 📊 Visualisation de la santé")
        
        healthy_count = sum(1 for status in components.values() if status)
        total_count = len(components)
        
        fig = go.Figure(data=[
            go.Pie(
                labels=["Composants OK", "Composants KO"],
                values=[healthy_count, total_count - healthy_count],
                hole=0.3,
                marker_colors=["green", "red"]
            )
        ])
        fig.update_layout(title="Santé des composants")
        st.plotly_chart(fig, use_container_width=True)
        
        # Données JSON complètes
        st.markdown("### 🔍 Données de santé complètes")
        st.json(health_data)
    
    else:
        st.error("❌ Impossible de récupérer les données de santé de l'agent")

# Footer
st.markdown("---")
st.markdown("🔐 **Security Agent MVP** - Interface Streamlit pour test et visualisation")
st.markdown("📚 Architecture: Vision/NLP → File Manager → Security Agent (chiffrement + vault)")
