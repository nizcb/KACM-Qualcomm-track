#!/bin/bash

# Script de démarrage pour Security Agent

echo "🚀 Démarrage du Security Agent..."
echo "📂 Répertoire: $(pwd)"
echo "🔐 Interface Streamlit disponible sur: http://localhost:8501"
echo ""

# Lancer Streamlit avec la nouvelle interface
streamlit run security_interface.py --server.port=8501 --server.headless=true
