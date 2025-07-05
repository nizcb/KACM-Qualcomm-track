#!/usr/bin/env python
"""
Agent IA NLP - Version Agent Autonome
====================================

Agent IA autonome qui peut :
- Analyser des fichiers et détecter les PII
- Raisonner sur les tâches à accomplir
- Planifier ses actions
- Utiliser des outils de manière autonome
- Gérer des demandes complexes

Retourne un JSON avec :
- file_path : chemin du fichier (str)
- resume : résumé du contenu (str) 
- warning : présence d'informations PII (bool)
"""

import os
import sys
import re
import json
import warnings
from typing import Dict, List, Any, Optional

# Suppression des avertissements Pydantic
warnings.filterwarnings("ignore", category=DeprecationWarning)

# LangChain imports
from langchain_community.llms import Ollama
from langchain.tools import tool

# ──────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.2:latest")

# Initialisation du LLM
llm = Ollama(
    model=LLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.7
)

# ──────────────────────────────────────────────────────────────────────────
# Regex patterns pour la détection PII
# ──────────────────────────────────────────────────────────────────────────
PII_REGEXES: Dict[str, re.Pattern] = {
    "EMAIL": re.compile(r"[\w\.\-]+@[\w\.-]+\.[a-z]{2,}", re.I),
    "PHONE": re.compile(r"\+?\d{1,3}[\s\-]?\d[\d\s\-]{8,}\d", re.I),
    "CARD": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
    "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b"),
    "SSN": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"),
}

# ──────────────────────────────────────────────────────────────────────────
# Outils pour l'Agent IA
# ──────────────────────────────────────────────────────────────────────────

@tool
def read_file_tool(file_path: str) -> str:
    """
    Lit le contenu d'un fichier texte.
    
    Args:
        file_path: Chemin vers le fichier à lire
        
    Returns:
        Contenu du fichier sous forme de chaîne de caractères
    """
    try:
        if not os.path.isabs(file_path):
            current_dir = os.getcwd()
            full_path = os.path.join(current_dir, file_path)
        else:
            full_path = file_path
            
        with open(full_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return f"Contenu du fichier '{file_path}':\n{content}"
    except Exception as e:
        return f"Erreur lors de la lecture du fichier '{file_path}': {str(e)}"

@tool
def summarize_text_tool(text: str) -> str:
    """
    Résume un texte en conservant les informations essentielles.
    
    Args:
        text: Texte à résumer
        
    Returns:
        Résumé du texte en 3 phrases maximum
    """
    try:
        # Résumé simple basé sur les premières phrases
        sentences = text.replace('\n', ' ').split('.')
        summary_sentences = []
        for sentence in sentences:
            if sentence.strip() and len(summary_sentences) < 3:
                summary_sentences.append(sentence.strip())
        
        result = '. '.join(summary_sentences) + '.' if summary_sentences else "Résumé non disponible."
        return f"Résumé généré: {result}"
    except Exception as e:
        return f"Erreur lors du résumé: {str(e)}"

@tool
def detect_pii_tool(text: str) -> str:
    """
    Détecte les informations personnelles identifiables (PII) dans un texte.
    
    Args:
        text: Texte à analyser
        
    Returns:
        Information sur la présence de PII trouvées
    """
    try:
        pii_found = []
        
        pii_patterns = {
            "EMAIL": re.compile(r"[\w\.\-]+@[\w\.-]+\.[a-z]{2,}", re.I),
            "PHONE": re.compile(r"\+?\d{1,3}[\s\-]?\d[\d\s\-]{8,}\d", re.I),
            "CARD": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
            "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b"),
            "SSN": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"),
        }
        
        for label, pattern in pii_patterns.items():
            if pattern.search(text):
                pii_found.append(label)
        
        if pii_found:
            return f"⚠️ PII détectées: {', '.join(pii_found)}. ATTENTION: Ce fichier contient des informations sensibles!"
        else:
            return "✅ Aucune PII détectée. Le fichier semble sûr."
            
    except Exception as e:
        return f"Erreur lors de la détection PII: {str(e)}"

@tool
def save_json_tool(data: str, filename: str) -> str:
    """
    Sauvegarde des données au format JSON dans un fichier.
    
    Args:
        data: Données à sauvegarder (format JSON string)
        filename: Nom du fichier de sortie
        
    Returns:
        Confirmation de la sauvegarde
    """
    try:
        # Parse du JSON pour validation
        json_data = json.loads(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return f"✅ Données sauvegardées avec succès dans '{filename}'"
    except Exception as e:
        return f"Erreur lors de la sauvegarde: {str(e)}"

@tool
def list_files_tool(directory: str = ".") -> str:
    """
    Liste les fichiers dans un répertoire.
    
    Args:
        directory: Répertoire à explorer (par défaut le répertoire courant)
        
    Returns:
        Liste des fichiers du répertoire
    """
    try:
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                files.append(f"📄 {item}")
            elif os.path.isdir(item_path):
                files.append(f"📁 {item}/")
        
        return f"Contenu du répertoire '{directory}':\n" + "\n".join(files)
    except Exception as e:
        return f"Erreur lors de la liste des fichiers: {str(e)}"

# ──────────────────────────────────────────────────────────────────────────
# Agent IA Principal
# ──────────────────────────────────────────────────────────────────────────
class AgentIA:
    """Agent IA autonome pour l'analyse NLP avec capacité de raisonnement"""
    
    def __init__(self, llm=None, offline_mode=False):
        self.llm = llm
        self.offline_mode = offline_mode
        self.conversation_history = []  # Mémoire simple
        
        # Outils disponibles pour l'agent
        self.tools = [
            read_file_tool,
            summarize_text_tool,
            detect_pii_tool,
            save_json_tool,
            list_files_tool
        ]
        
        # Initialisation de l'agent simplifié
        self.agent = None
        if not self.offline_mode and self.llm:
            self.agent = self  # L'agent est lui-même avec ses outils
    
    def reason_and_act(self, query: str) -> str:
        """Raisonne et agit sur une requête donnée"""
        if not self.llm or self.offline_mode:
            return "Agent IA non disponible, utilisation du mode fallback"
        
        # Template de raisonnement ReAct simplifié
        prompt = f"""Tu es un agent IA spécialisé en analyse NLP et détection PII.

Tu as accès aux outils suivants:
1. read_file_tool(file_path) - Lit un fichier
2. summarize_text_tool(text) - Résume un texte
3. detect_pii_tool(text) - Détecte les PII
4. save_json_tool(data, filename) - Sauvegarde en JSON
5. list_files_tool(directory) - Liste les fichiers

Utilise le format de raisonnement suivant:
Thought: [Ce que je dois faire]
Action: [Outil à utiliser]
Action Input: [Paramètres de l'outil]
Observation: [Résultat de l'action]
... (répète si nécessaire)
Final Answer: [Réponse finale]

Question: {query}

Commence par réfléchir:"""

        try:
            # Génération de la réponse avec raisonnement
            response = self.llm.invoke(prompt)
            
            # Traitement de la réponse pour extraire les actions
            return self._process_reasoning_response(response, query)
        except Exception as e:
            return f"Erreur lors du raisonnement: {e}"
    
    def _process_reasoning_response(self, response: str, original_query: str) -> str:
        """Traite la réponse de raisonnement et exécute les actions"""
        lines = response.split('\n')
        result = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Action:'):
                action = line.replace('Action:', '').strip()
                result.append(f"🔧 Action: {action}")
            elif line.startswith('Thought:'):
                thought = line.replace('Thought:', '').strip()
                result.append(f"💭 Réflexion: {thought}")
            elif line.startswith('Final Answer:'):
                answer = line.replace('Final Answer:', '').strip()
                result.append(f"✅ Réponse finale: {answer}")
        
        return '\n'.join(result) if result else response
    
    def process_file_with_reasoning(self, file_path: str) -> Dict[str, Any]:
        """Traite un fichier en utilisant le raisonnement de l'agent IA"""
        
        if self.agent and not self.offline_mode:
            try:
                # Utilisation de l'agent IA pour traiter le fichier
                query = f"""Analyse le fichier '{file_path}' et produis un résultat JSON avec:
                1. Lis le contenu du fichier
                2. Génère un résumé du contenu
                3. Détecte la présence de PII
                4. Crée un JSON avec file_path, resume, et warning (boolean)
                5. Sauvegarde le résultat dans un fichier nommé '{os.path.splitext(os.path.basename(file_path))[0]}_analysis.json'
                
                Retourne uniquement le JSON final."""
                
                # Raisonnement de l'agent
                reasoning = self.reason_and_act(query)
                print(f"🧠 Raisonnement de l'agent:\n{reasoning}\n")
                
                # Exécution directe des outils pour obtenir le résultat
                return self._execute_analysis(file_path)
                
            except Exception as e:
                print(f"Erreur avec l'agent IA: {e}")
                return self._fallback_process_file(file_path)
        else:
            return self._fallback_process_file(file_path)
    
    def _generate_smart_summary(self, content: str) -> str:
        """Génère un résumé intelligent avec LLM si disponible"""
        if not self.offline_mode and self.llm:
            try:
                prompt = f"""Résume le texte suivant en 3 phrases maximum en français, en gardant les informations essentielles :

Texte : {content}

Résumé :
Ne commence jamais le résumé par une introduction de type "Voici le résumé" ou similaire.
"""
                response = self.llm.invoke(prompt)
                return response.strip()
            except Exception as e:
                print(f"⚠️ Erreur LLM, passage en mode offline : {e}")
        
        # Fallback : résumé simple
        sentences = content.replace('\n', ' ').split('.')
        summary_sentences = []
        for sentence in sentences:
            if sentence.strip() and len(summary_sentences) < 3:
                summary_sentences.append(sentence.strip())
        
        return '. '.join(summary_sentences) + '.' if summary_sentences else "Résumé non disponible."
    def _execute_analysis(self, file_path: str) -> Dict[str, Any]:
        """Exécute l'analyse avec les outils disponibles"""
        try:
            # Lecture du fichier directement (sans passer par l'outil)
            print("🔧 Lecture du fichier...")
            if not os.path.isabs(file_path):
                current_dir = os.getcwd()
                full_path = os.path.join(current_dir, file_path)
            else:
                full_path = file_path
                
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Génération du résumé intelligent
            print("🔧 Génération du résumé...")
            resume = self._generate_smart_summary(content)
            
            # Détection PII
            print("🔧 Détection des PII...")
            pii_found = False
            pii_patterns = {
                "EMAIL": re.compile(r"[\w\.\-]+@[\w\.-]+\.[a-z]{2,}", re.I),
                "PHONE": re.compile(r"\+?\d{1,3}[\s\-]?\d[\d\s\-]{8,}\d", re.I),
                "CARD": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
                "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b"),
                "SSN": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"),
            }
            
            for label, pattern in pii_patterns.items():
                if pattern.search(content):
                    pii_found = True
                    break
            
            # Construction du résultat final
            result = {
                "file_path": os.path.abspath(file_path),
                "resume": resume,
                "warning": pii_found
            }
            
            # Sauvegarde automatique
            output_file = f"{os.path.splitext(os.path.basename(file_path))[0]}_analysis.json"
            print(f"🔧 Sauvegarde dans {output_file}...")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return result
            
        except Exception as e:
            return {
                "file_path": os.path.abspath(file_path) if os.path.exists(file_path) else file_path,
                "resume": f"Erreur lors du traitement : {str(e)}",
                "warning": False
            }
    
    def _fallback_process_file(self, file_path: str) -> Dict[str, Any]:
        """Traitement de fichier en mode fallback (sans agent IA)"""
        try:
            # Lecture du fichier directement
            print("📁 Lecture du fichier...")
            if not os.path.isabs(file_path):
                current_dir = os.getcwd()
                full_path = os.path.join(current_dir, file_path)
            else:
                full_path = file_path
                
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Génération du résumé intelligent
            print("✍️ Génération du résumé...")
            resume = self._generate_smart_summary(content)
            
            # Détection PII
            print("🔍 Détection des PII...")
            pii_found = False
            pii_patterns = {
                "EMAIL": re.compile(r"[\w\.\-]+@[\w\.-]+\.[a-z]{2,}", re.I),
                "PHONE": re.compile(r"\+?\d{1,3}[\s\-]?\d[\d\s\-]{8,}\d", re.I),
                "CARD": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
                "IBAN": re.compile(r"\b[A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b"),
                "SSN": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"),
            }
            
            for label, pattern in pii_patterns.items():
                if pattern.search(content):
                    pii_found = True
                    break
            
            # Construction du résultat final
            result = {
                "file_path": os.path.abspath(file_path),
                "resume": resume,
                "warning": pii_found
            }
            
            return result
            
        except Exception as e:
            return {
                "file_path": os.path.abspath(file_path) if os.path.exists(file_path) else file_path,
                "resume": f"Erreur lors du traitement : {str(e)}",
                "warning": False
            }
    
    def chat(self, message: str) -> str:
        """Interface de chat avec l'agent IA"""
        if self.agent and not self.offline_mode:
            try:
                return self.reason_and_act(message)
            except Exception as e:
                return f"Erreur lors du chat: {e}"
        else:
            return "Mode offline activé. Utilisez les commandes directes pour traiter les fichiers."

# ──────────────────────────────────────────────────────────────────────────
# Fonctions utilitaires
# ──────────────────────────────────────────────────────────────────────────
def process_file(file_path: str, offline_mode: bool = False) -> Dict[str, Any]:
    """Traite un fichier et retourne le résultat JSON"""
    agent = AgentIA(llm if not offline_mode else None, offline_mode)
    return agent.process_file_with_reasoning(file_path)

def process_file_to_json_string(file_path: str, offline_mode: bool = False) -> str:
    """Traite un fichier et retourne le JSON sous forme de string"""
    result = process_file(file_path, offline_mode)
    return json.dumps(result, indent=2, ensure_ascii=False)

def save_result_to_file(file_path: str, output_file: str, offline_mode: bool = False):
    """Traite un fichier et sauvegarde le résultat"""
    result = process_file(file_path, offline_mode)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Résultat sauvegardé dans : {output_file}")

def chat_mode():
    """Mode chat interactif avec l'agent IA"""
    print("🤖 Mode Chat Interactif - Agent IA NLP")
    print("=====================================")
    print("Tapez 'quit' pour quitter, 'help' pour l'aide")
    
    agent = AgentIA(llm, offline_mode=False)
    
    if not agent.agent:
        print("⚠️ Agent IA non disponible, vérifiez Ollama")
        return
    
    print("\n💬 Chat prêt ! Posez vos questions...")
    
    while True:
        try:
            user_input = input("\n👤 Vous: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Au revoir!")
                break
            
            if user_input.lower() == 'help':
                print("""
🤖 Commandes disponibles:
- Analysez un fichier: "Analyse le fichier recit.txt"
- Listez les fichiers: "Quels fichiers sont disponibles?"
- Posez des questions: "Résume-moi ce document"
- Détection PII: "Y a-t-il des informations sensibles?"
- quit/exit: Quitter le chat
                """)
                continue
            
            if not user_input:
                continue
            
            print("\n🤖 Agent IA: ", end="")
            response = agent.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")

def test_agent():
    """Test de l'agent IA avec différents fichiers"""
    print("=== Test Agent IA NLP ===\n")
    
    # Test 1: Fichier sans PII
    print("1. Test fichier sans PII avec Agent IA")
    print("-" * 40)
    try:
        if os.path.exists("recit.txt"):
            agent = AgentIA(llm, offline_mode=False)
            
            if agent.agent:
                print("🤖 Test avec Agent IA...")
                result = agent.process_file_with_reasoning("recit.txt")
            else:
                print("⚠️ Agent IA non disponible, test en mode offline...")
                result = process_file("recit.txt", offline_mode=True)
            
            print(f"File path: {result['file_path']}")
            print(f"Resume: {result['resume'][:100]}...")
            print(f"Warning: {result['warning']}")
        else:
            print("Fichier recit.txt non trouvé")
    except Exception as e:
        print(f"Erreur: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Fichier avec PII
    print("2. Test fichier avec PII avec Agent IA")
    print("-" * 40)
    
    test_content = """
    Rapport de contact client.
    
    Nom : Marie Dupont
    Email : marie.dupont@email.com
    Téléphone : +33 6 12 34 56 78
    Carte : 4242 4242 4242 4242
    
    Demande de remboursement.
    """
    
    with open("test_pii.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        agent = AgentIA(llm, offline_mode=False)
        
        if agent.agent:
            print("🤖 Test avec Agent IA...")
            result = agent.process_file_with_reasoning("test_pii.txt")
        else:
            print("⚠️ Agent IA non disponible, test en mode offline...")
            result = process_file("test_pii.txt", offline_mode=True)
        
        print(f"File path: {result['file_path']}")
        print(f"Resume: {result['resume'][:100]}...")
        print(f"Warning: {result['warning']}")
        
        # Affichage du JSON complet
        print("\nJSON complet :")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        if os.path.exists("test_pii.txt"):
            os.remove("test_pii.txt")

# ──────────────────────────────────────────────────────────────────────────
# Interface en ligne de commande
# ──────────────────────────────────────────────────────────────────────────
def main():
    """Interface principale"""
    if len(sys.argv) < 2:
        print("Agent IA NLP - Analyse Intelligente et Détection PII")
        print("=========================================================")
        print("🤖 Agent IA autonome avec capacité de raisonnement")
        print("\nUsage:")
        print("  python agent_nlp.py <fichier>                    # Analyse avec agent IA")
        print("  python agent_nlp.py <fichier> <sortie.json>      # Sauvegarde personnalisée")
        print("  python agent_nlp.py <fichier> --offline          # Mode offline (sans agent IA)")
        print("  python agent_nlp.py --test                       # Tests")
        print("  python agent_nlp.py --chat                       # Mode chat interactif")
        print("\nExemples:")
        print("  python agent_nlp.py recit.txt                    # → recit_analysis.json")
        print("  python agent_nlp.py rapport.txt resultat.json   # → resultat.json")
        print("  python agent_nlp.py rapport.txt --offline       # → mode fallback")
        print("\nCapacités de l'Agent IA:")
        print("  🧠 Raisonnement autonome sur les tâches")
        print("  📊 Planification d'actions")
        print("  🔧 Utilisation d'outils spécialisés")
        print("  💭 Mémoire conversationnelle")
        print("  🔍 Analyse contextuelle avancée")
        print("\nFormat de sortie JSON:")
        print('  {')
        print('    "file_path": "chemin/vers/fichier",')
        print('    "resume": "résumé du contenu",')
        print('    "warning": true/false')
        print('  }')
        return
    
    if sys.argv[1] == "--test":
        test_agent()
        return
    
    if sys.argv[1] == "--chat":
        chat_mode()
        return
    
    file_path = sys.argv[1]
    output_file = None
    offline_mode = False
    
    # Analyse des arguments
    if len(sys.argv) > 2:
        if sys.argv[2] == "--offline":
            offline_mode = True
        elif sys.argv[2].endswith('.json'):
            output_file = sys.argv[2]
        
        if len(sys.argv) > 3 and sys.argv[3] == "--offline":
            offline_mode = True
    
    try:
        if not offline_mode:
            print("🤖 Initialisation de l'Agent IA...")
            try:
                test_response = llm.invoke("Test")
                print("✅ Agent IA prêt")
            except:
                print("⚠️ Connexion Ollama échouée, passage en mode offline")
                offline_mode = True
        else:
            print("📋 Mode offline activé")
        
        print(f"📂 Traitement du fichier : {file_path}")
        print(f"🔧 Mode : {'Offline (Fallback)' if offline_mode else 'Agent IA'}")
        
        if output_file:
            save_result_to_file(file_path, output_file, offline_mode)
        else:
            # Sauvegarde automatique avec nom basé sur le fichier d'entrée
            result = process_file(file_path, offline_mode)
            json_output = json.dumps(result, indent=2, ensure_ascii=False)
            
            # Génération du nom de fichier de sortie
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = f"{base_name}_analysis.json"
            
            # Sauvegarde
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print("\n📋 Résultat JSON :")
            print(json_output)
            print(f"\n✅ Résultat sauvegardé dans : {output_file}")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    main()
