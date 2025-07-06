#!/bin/bash

# Script de démarrage pour Security Agent
echo "🚀 Démarrage du Security Agent..."
echo "🔐 Interface Streamlit disponible sur: http://localhost:8501"
echo ""

# Lancer Streamlit
streamlit run security_interface.py --server.port=8501 --server.headless=true
