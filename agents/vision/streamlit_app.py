#!/usr/bin/env python3
"""
Interface Streamlit pour tester l'Agent Vision
Analyse de documents visuels avec détection PII avancée
"""

import streamlit as st
import asyncio
import json
import time
from pathlib import Path
import pandas as pd
from agent import analyze_document, VisionArgs, ONNX_AVAILABLE, PDF_AVAILABLE

# Configuration de la page
st.set_page_config(
    page_title="🔍 Agent Vision - Analyseur de Documents",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour améliorer l'apparence
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 0.375rem;
    padding: 1rem;
    margin: 1rem 0;
}
.warning-box {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 0.375rem;
    padding: 1rem;
    margin: 1rem 0;
}
.error-box {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 0.375rem;
    padding: 1rem;
    margin: 1rem 0;
}
.metric-card {
    background-color: #f8f9fa;
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 0.5rem 0;
    border-left: 4px solid #1f77b4;
}
</style>
""", unsafe_allow_html=True)

def display_system_status():
    """Affiche le statut du système"""
    st.sidebar.header("📊 Statut du Système")
    
    # Statut des dépendances
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if ONNX_AVAILABLE:
            st.success("✅ ONNX")
        else:
            st.error("❌ ONNX")
    
    with col2:
        if PDF_AVAILABLE:
            st.success("✅ PDF")
        else:
            st.error("❌ PDF")
    
    # Informations sur les capacités
    st.sidebar.subheader("🔧 Capacités")
    capabilities = [
        "📝 OCR Multilingue (FR/EN)",
        "🔍 Détection PII Textuelle",
        "👁️ Détection PII Visuelle",
        "🚨 Détection NSFW",
        "📄 Support PDF Multi-pages",
        "🏷️ Tags Sémantiques",
        "📋 Résumé Intelligent"
    ]
    
    for cap in capabilities:
        st.sidebar.write(cap)

def format_pii_types(pii_types):
    """Formate les types PII pour l'affichage"""
    pii_mapping = {
        "EMAIL": "📧 Email",
        "PHONE": "📞 Téléphone", 
        "CARD_NUMBER": "💳 Carte Bancaire",
        "CARD_PHOTO": "💳 Photo Carte",
        "IBAN": "🏦 IBAN",
        "SSN": "🆔 Sécurité Sociale",
        "ID_DOC": "🆔 Document Identité",
        "NUDITY": "🚨 Contenu NSFW"
    }
    
    return [pii_mapping.get(pii, pii) for pii in pii_types]

def display_results(result):
    """Affiche les résultats de l'analyse"""
    
    # En-tête avec métriques principales
    st.markdown("## 📊 Résultats de l'Analyse")
    
    # Métriques en colonnes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 Type de fichier",
            value=result.file_type.upper(),
            delta=f"{result.pages_processed} page(s)" if result.pages_processed > 0 else None
        )
    
    with col2:
        st.metric(
            label="📝 Caractères extraits",
            value=len(result.text),
            delta="OCR réussi" if len(result.text) > 0 else "Aucun texte"
        )
    
    with col3:
        st.metric(
            label="🏷️ Tags générés",
            value=len(result.tags),
            delta="Classification automatique"
        )
    
    with col4:
        status_color = "🔴" if result.pii_detected else "🟢"
        st.metric(
            label="🔒 Statut PII",
            value=f"{status_color} {'Détectés' if result.pii_detected else 'Aucun'}",
            delta=f"{len(result.pii_types)} type(s)" if result.pii_detected else None
        )
    
    # Statut général
    if result.status == "ok":
        st.markdown('<div class="success-box">✅ <strong>Analyse réussie</strong> - Document traité avec succès</div>', unsafe_allow_html=True)
    elif "error" in result.status:
        st.markdown(f'<div class="error-box">❌ <strong>Erreur</strong> - {result.summary}</div>', unsafe_allow_html=True)
        return
    
    # Alerte PII si détectés
    if result.pii_detected:
        formatted_pii = format_pii_types(result.pii_types)
        st.markdown(f'<div class="warning-box">⚠️ <strong>Données sensibles détectées :</strong> {", ".join(formatted_pii)}</div>', unsafe_allow_html=True)
    
    # Tabs pour organiser l'affichage
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 Résumé", "📝 Texte OCR", "🏷️ Tags", "🔒 PII Détaillés", "📊 JSON Complet"])
    
    with tab1:
        st.subheader("📄 Résumé Intelligent")
        if result.summary:
            st.write(result.summary)
        else:
            st.info("Aucun résumé généré")
    
    with tab2:
        st.subheader("📝 Texte Extrait (OCR)")
        if result.text:
            # Affichage avec numérotation des lignes
            lines = result.text.split('\n')
            text_display = "\n".join([f"{i+1:3d} | {line}" for i, line in enumerate(lines)])
            st.code(text_display, language="text")
            
            # Statistiques du texte
            st.write("**Statistiques du texte :**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"📊 Caractères : {len(result.text)}")
            with col2:
                st.write(f"📝 Mots : {len(result.text.split())}")
            with col3:
                st.write(f"📄 Lignes : {len(lines)}")
        else:
            st.info("Aucun texte détecté par l'OCR")
    
    with tab3:
        st.subheader("🏷️ Tags Sémantiques")
        if result.tags:
            # Affichage des tags comme des badges
            tag_html = ""
            tag_colors = {
                "confidentiel": "#dc3545",
                "banque": "#28a745", 
                "identité": "#ffc107",
                "facture": "#17a2b8",
                "pdf": "#6f42c1",
                "multi-pages": "#fd7e14"
            }
            
            for tag in result.tags:
                color = tag_colors.get(tag, "#6c757d")
                tag_html += f'<span style="background-color: {color}; color: white; padding: 0.25rem 0.5rem; margin: 0.25rem; border-radius: 0.25rem; display: inline-block;">{tag}</span>'
            
            st.markdown(tag_html, unsafe_allow_html=True)
            
            # Tableau des tags avec descriptions
            tag_descriptions = {
                "confidentiel": "Document contenant des informations sensibles",
                "banque": "Document bancaire ou financier",
                "identité": "Document d'identité officiel",
                "facture": "Facture ou document de facturation",
                "pdf": "Document au format PDF",
                "multi-pages": "Document de plusieurs pages",
                "contact": "Contient des informations de contact",
                "administratif": "Document administratif officiel",
                "urgent": "Document nécessitant une attention urgente",
                "numérique": "Document riche en données numériques"
            }
            
            df_tags = pd.DataFrame([
                {"Tag": tag, "Description": tag_descriptions.get(tag, "Tag personnalisé")}
                for tag in result.tags
            ])
            st.dataframe(df_tags, use_container_width=True)
        else:
            st.info("Aucun tag généré")
    
    with tab4:
        st.subheader("🔒 Analyse PII Détaillée")
        if result.pii_detected:
            # Types PII détectés
            st.write("**Types PII détectés :**")
            formatted_pii = format_pii_types(result.pii_types)
            for pii in formatted_pii:
                st.write(f"- {pii}")
            
            # Positions détaillées des PII dans le texte
            if result.pii_spans:
                st.write("**Positions dans le texte :**")
                df_pii = pd.DataFrame([
                    {
                        "Type": format_pii_types([span.label])[0],
                        "Position": f"{span.start}-{span.end}",
                        "Texte": result.text[span.start:span.end] if span.end <= len(result.text) else "Position invalide"
                    }
                    for span in result.pii_spans
                ])
                st.dataframe(df_pii, use_container_width=True)
        else:
            st.success("✅ Aucune donnée sensible détectée dans ce document")
    
    with tab5:
        st.subheader("📊 Réponse JSON Complète")
        st.write("Format de sortie complet de l'agent (compatible API) :")
        
        # Conversion en dictionnaire pour l'affichage JSON
        result_dict = {
            "path": result.path,
            "source": result.source,
            "text": result.text,
            "summary": result.summary,
            "tags": result.tags,
            "pii_detected": result.pii_detected,
            "pii_types": result.pii_types,
            "pii_spans": [
                {"start": span.start, "end": span.end, "label": span.label}
                for span in result.pii_spans
            ],
            "status": result.status,
            "pages_processed": result.pages_processed,
            "file_type": result.file_type
        }
        
        st.json(result_dict)
        
        # Bouton pour télécharger le JSON
        json_str = json.dumps(result_dict, indent=2, ensure_ascii=False)
        st.download_button(
            label="💾 Télécharger JSON",
            data=json_str,
            file_name=f"analysis_{Path(result.path).stem}.json",
            mime="application/json"
        )

def main():
    """Interface principale"""
    
    # En-tête
    st.markdown('<h1 class="main-header">🔍 Agent Vision - Analyseur de Documents</h1>', unsafe_allow_html=True)
    st.markdown("**Analyse intelligente de documents visuels avec détection PII avancée**")
    
    # Sidebar avec statut système
    display_system_status()
    
    # Zone principale
    st.markdown("## 📁 Sélection du Document")
    
    # Méthodes d'entrée
    input_method = st.radio(
        "Choisissez la méthode d'entrée :",
        ["📝 Chemin de fichier", "📤 Upload de fichier"],
        horizontal=True
    )
    
    file_path = None
    uploaded_file = None
    
    if input_method == "📝 Chemin de fichier":
        # Champ pour le chemin de fichier
        file_path = st.text_input(
            "Chemin vers votre fichier :",
            placeholder="C:/Documents/mon_document.pdf ou C:/Images/facture.jpg",
            help="Formats supportés : JPG, PNG, PDF, TIFF, BMP"
        )
        
        # Validation du chemin
        if file_path:
            if not Path(file_path).exists():
                st.error(f"❌ Fichier non trouvé : {file_path}")
                file_path = None
            else:
                file_info = Path(file_path)
                st.success(f"✅ Fichier trouvé : {file_info.name} ({file_info.stat().st_size / 1024:.1f} KB)")
    
    else:
        # Upload de fichier
        uploaded_file = st.file_uploader(
            "Uploadez votre document :",
            type=['jpg', 'jpeg', 'png', 'pdf', 'tiff', 'bmp'],
            help="Glissez-déposez votre fichier ou cliquez pour sélectionner"
        )
        
        if uploaded_file:
            # Sauvegarder temporairement le fichier uploadé
            temp_path = Path("temp_upload") / uploaded_file.name
            temp_path.parent.mkdir(exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())
            
            file_path = str(temp_path)
            st.success(f"✅ Fichier uploadé : {uploaded_file.name} ({len(uploaded_file.getvalue()) / 1024:.1f} KB)")
    
    # Options avancées pour PDF
    extract_pages = None
    if file_path and file_path.lower().endswith('.pdf'):
        st.markdown("### ⚙️ Options PDF")
        
        pdf_option = st.radio(
            "Pages à analyser :",
            ["Toutes les pages", "Pages spécifiques"],
            horizontal=True
        )
        
        if pdf_option == "Pages spécifiques":
            pages_input = st.text_input(
                "Numéros de pages (ex: 1,3,5 ou 1-3) :",
                placeholder="1,2,5"
            )
            
            if pages_input:
                try:
                    # Parser l'entrée des pages
                    if '-' in pages_input:
                        start, end = map(int, pages_input.split('-'))
                        extract_pages = list(range(start, end + 1))
                    else:
                        extract_pages = [int(p.strip()) for p in pages_input.split(',')]
                    
                    st.info(f"📄 Pages sélectionnées : {extract_pages}")
                except ValueError:
                    st.error("❌ Format invalide. Utilisez : 1,2,3 ou 1-5")
    
    # Bouton d'analyse
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🔍 Analyser le Document",
            type="primary",
            disabled=not file_path,
            use_container_width=True
        )
    
    # Traitement de l'analyse
    if analyze_button and file_path:
        with st.spinner("🔄 Analyse en cours... Veuillez patienter"):
            start_time = time.time()
            
            try:
                # Préparation des arguments
                args = VisionArgs(
                    path=file_path,
                    extract_pages=extract_pages
                )
                
                # Exécution de l'analyse
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(analyze_document(args))
                loop.close()
                
                # Calcul du temps de traitement
                processing_time = time.time() - start_time
                
                # Affichage des résultats
                st.markdown("---")
                
                # Métrique de performance
                perf_color = "🟢" if processing_time < 3 else "🟡" if processing_time < 10 else "🔴"
                st.markdown(f"**⏱️ Temps de traitement :** {perf_color} {processing_time:.2f}s")
                
                # Affichage des résultats détaillés
                display_results(result)
                
                # Nettoyage du fichier temporaire si nécessaire
                if uploaded_file and Path(file_path).exists():
                    Path(file_path).unlink()
                
            except Exception as e:
                st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
                
                # Nettoyage en cas d'erreur
                if uploaded_file and Path(file_path).exists():
                    Path(file_path).unlink()
    
    # Instructions d'utilisation
    with st.expander("ℹ️ Instructions d'utilisation"):
        st.markdown("""
        ### 🚀 Comment utiliser l'Agent Vision
        
        1. **Sélectionnez votre document** :
           - Copiez le chemin complet de votre fichier
           - Ou uploadez directement le fichier
        
        2. **Formats supportés** :
           - 📸 Images : JPG, PNG, TIFF, BMP
           - 📄 PDF : Single et multi-pages
        
        3. **Fonctionnalités** :
           - 📝 OCR automatique (français/anglais)
           - 🔍 Détection PII (emails, téléphones, cartes bancaires...)
           - 👁️ Détection visuelle (cartes, documents ID, contenu NSFW)
           - 📋 Résumé intelligent automatique
           - 🏷️ Classification par tags sémantiques
        
        4. **Options PDF** :
           - Analysez toutes les pages ou seulement certaines
           - Format : 1,2,5 ou 1-3
        
        5. **Résultats** :
           - Résumé et tags automatiques
           - Texte complet extrait
           - Détection de données sensibles
           - Export JSON pour intégration API
        """)

if __name__ == "__main__":
    main()
