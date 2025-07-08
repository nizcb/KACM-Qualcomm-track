# Enterprise File Auto-Organization System

## 📋 Project Description

This project is an **intelligent enterprise file auto-organization system** that uses artificial intelligence to automatically classify your documents according to a strict and secure business structure.

### 🎯 Problem Solved
- **Disorganization** of scattered enterprise files
- **Time wasted** searching and manually classifying
- **Lack of security** for sensitive documents
- **Absence of coherent business structure**

### ✨ Proposed Solution
An intelligent multi-agent system that:
- **Automatically analyzes** file content (text, audio, images)
- **Intelligently classifies** according to predefined business structure
- **Secures** sensitive documents with AES-256 encryption
- **Completely avoids** generic categories ("general", "others", etc.)
- **Provides a modern and intuitive** graphical interface

## 🛠️ Prerequisites

### 1. Python 3.11+
```bash
python --version  # Check version
```

### 2. Ollama (Artificial Intelligence)
**Required** for intelligent classification:

```bash
# Install Ollama
# Download from https://ollama.ai/

# Download Llama 3.2 model
ollama pull llama3.2:latest

# Verify installation
ollama list
```

### 3. Python Dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Installation

1. **Clone the project**
```bash
git clone <your-repo>
cd KACM-Qualcomm-track
```

2. **Install Ollama and model**
```bash
# Download Ollama from https://ollama.ai/
ollama pull llama3.2:latest
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Launch the interface**
```bash
python start_gui.py
```

## 🖥️ Usage

### Graphical Interface (Recommended)
```bash
python start_gui.py
```

### Programmatic Usage
```python
from agents.agent_file_manager_intelligent import AgentFileManagerIntelligent

# Create intelligent agent
agent = AgentFileManagerIntelligent()

# Organize a folder
result = agent.organize_folder("/path/to/folder")
print(f"Files organized: {result['total_files']}")
```

## 🏗️ System Architecture

### 🤖 Multi-Modal Agents
- **`agent_file_manager_intelligent.py`** - Main agent with Llama AI
- **`agent_nlp_mcp.py`** - Text analysis and NLP
- **`agent_audio_mcp.py`** - Audio transcription and analysis
- **`agent_vision_mcp.py`** - Image recognition and OCR
- **`agent_security_mcp.py`** - Encryption and security
- **`agent_orchestrator_mcp.py`** - Workflow orchestration

### 🖥️ Interface
- **`gui_file_organizer.py`** - Tkinter graphical interface
- **`start_gui.py`** - Startup script

### 🔧 Utilities
- **`agents/utils/`** - Specialized processors (audio, etc.)

## ⚡ Main Features

### 🧠 Artificial Intelligence
- **Contextual classification** via Llama 3.2 model
- **Semantic analysis** of file content
- **Thematic scoring** for automatic decision-making
- **Zero generic categories** (no more "general" or "others")

### 🔐 Advanced Security
- **AES-256 encryption** for sensitive folders
- **Automatic detection** of confidential content
- **Secure management** of passwords
- **Automatic public/secure** classification

### 📁 Strict Business Structure
```
organized/
├── public/                          # Public documents
│   ├── administration_hr/           # HR and administration
│   ├── commercial_sales/            # Commercial and sales
│   ├── communication_marketing/     # Communication and marketing
│   ├── accounting_finance/          # Accounting and finance
│   ├── it_technical/               # IT and technical
│   ├── legal_juridical/            # Legal and juridical
│   ├── operations_production/       # Operations and production
│   └── multimedia_resources/        # Media and resources
└── secure/                         # Encrypted documents (same structure)
    ├── administration_hr/
    ├── commercial_sales/
    └── ...
```

### 🎯 Multi-Modal Analysis
- **Text**: NLP analysis, entity extraction, thematic classification
- **Audio**: Automatic transcription, spoken content analysis
- **Images**: OCR, object recognition, text extraction
- **Metadata**: File property analysis

## 🔧 Technologies Used

- **Python 3.11+** - Main language
- **Ollama + Llama 3.2** - Artificial intelligence
- **Tkinter** - Graphical interface
- **Cryptography** - AES-256 encryption
- **OpenCV** - Image processing
- **SpeechRecognition** - Audio transcription



## 📊 Project Statistics

- ✅ **100% business classification** (zero "general")
- ✅ **Enterprise-grade security** (AES-256)
- ✅ **Modern and intuitive** graphical interface
- ✅ **Multi-modal** (text, audio, images)
- ✅ **Contextual artificial intelligence**
- ✅ **Scalable multi-agent** architecture
