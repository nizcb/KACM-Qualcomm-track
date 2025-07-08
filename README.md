# NeuroSort : File Auto-Organization System

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

### 2. AI Backend Setup (Choose One)

#### Option A: Groq Cloud AI (Recommended - Fast & Reliable)
The system can use **Groq** for fast cloud-based AI processing:

1. **Get a Free Groq API Key:**
   - Visit [console.groq.com](https://console.groq.com)
   - Sign up for a free account
   - Create an API key

2. **Set Environment Variable:**
```bash
# Windows (PowerShell)
$env:GROQ_API_KEY="your_groq_api_key_here"

# Windows (Command Prompt)
set GROQ_API_KEY=your_groq_api_key_here

# Linux/Mac
export GROQ_API_KEY="your_groq_api_key_here"
```

3. **Make it Permanent:**
   - Windows: Add to System Environment Variables
   - Linux/Mac: Add to ~/.bashrc or ~/.zshrc

#### Option B: Ollama (Local AI - Fallback)
**Local AI** for offline processing:

```bash
# Install Ollama
# Download from https://ollama.ai/

# Download Llama 3.2 model
ollama pull llama3.2:latest

# Verify installation
ollama list
```

**Note:** The system automatically detects Groq availability and falls back to Ollama if no internet connection or API key is found.

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

2. **Set up AI Backend**
```bash
# Option A: Set Groq API key (recommended)
$env:GROQ_API_KEY="your_api_key_here"

# Option B: Install Ollama locally
# Download from https://ollama.ai/
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

The system will automatically:
- 🌐 **Use Groq** if API key is configured (fast cloud AI)
- 🏠 **Fall back to Ollama** if offline or no API key (local AI)
- 📊 **Show current backend** in the interface

### Programmatic Usage
```python
from agents.agent_file_manager_intelligent import AgentFileManagerIntelligent

# Create intelligent agent (auto-detects Groq/Ollama)
agent = AgentFileManagerIntelligent()

# Organize a folder
result = agent.organize_folder("/path/to/folder")
print(f"Files organized: {result['total_files']}")
print(f"AI Backend: {result['ai_backend']}")  # Shows Groq or Ollama
```

## 🏗️ System Architecture

### � AI Backend (Unified Intelligence)
- **`agents/ai_backend.py`** - **Unified AI Backend**
  - 🌐 **Groq Integration** - Fast cloud AI (recommended)
  - 🏠 **Ollama Integration** - Local AI fallback
  - 🔄 **Auto-detection** - Automatic backend selection
  - 📊 **Status monitoring** - Real-time backend health
  - ⚡ **Intelligent fallback** - Seamless switching

### �🤖 Multi-Modal Agents
- **`agent_file_manager_intelligent.py`** - Main agent with AI backend
- **`agent_nlp_mcp.py`** - Text analysis and NLP (AI-powered)
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
