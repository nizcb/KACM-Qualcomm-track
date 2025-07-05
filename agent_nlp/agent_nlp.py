import os
import sys
import re
import json
import warnings
from typing import Dict, List, Any

# Suppression des avertissements Pydantic
warnings.filterwarnings("ignore", category=DeprecationWarning)

# LangChain imports
from langchain_community.llms import Ollama

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
# Agent NLP Principal
# ──────────────────────────────────────────────────────────────────────────
class AgentNLP:
    """Agent NLP pour résumé et détection PII"""
    
    def __init__(self, llm=None, offline_mode=False):
        self.llm = llm
        self.offline_mode = offline_mode
    
    def read_file(self, file_path: str) -> str:
        """Lit le contenu d'un fichier"""
        try:
            if not os.path.isabs(file_path):
                current_dir = os.getcwd()
                full_path = os.path.join(current_dir, file_path)
            else:
                full_path = file_path
                
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du fichier : {str(e)}")
    
    def generate_summary(self, text: str) -> str:
        """Génère un résumé du texte"""
        if self.offline_mode or not self.llm:
            return self._simple_summary(text)
        
        try:
            prompt = f"""Résume le texte suivant en 3 phrases maximum en français, en gardant les informations essentielles :

Texte : {text}

Résumé :
Ne commence jamais le résumé par une introduction de type "Voici le résumé" ou similaire.
"""
            
            response = self.llm.invoke(prompt)
            return response.strip()
        except Exception as e:
            print(f"Erreur LLM, passage en mode offline : {e}")
            return self._simple_summary(text)
    
    def _simple_summary(self, text: str) -> str:
        """Crée un résumé simple basé sur les premières phrases"""
        sentences = text.replace('\n', ' ').split('.')
        summary_sentences = []
        for sentence in sentences:
            if sentence.strip() and len(summary_sentences) < 3:
                summary_sentences.append(sentence.strip())
        
        return '. '.join(summary_sentences) + '.' if summary_sentences else "Résumé non disponible."
    
    def detect_pii(self, text: str) -> bool:
        """Détecte les informations personnelles et retourne True si trouvées"""
        for label, pattern in PII_REGEXES.items():
            if pattern.search(text):
                return True
        return False
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Traite un fichier et retourne le résultat au format JSON"""
        try:
            # Lecture du fichier
            content = self.read_file(file_path)
            
            # Génération du résumé
            resume = self.generate_summary(content)
            
            # Détection PII
            warning = self.detect_pii(content)
            
            # Construction du résultat final
            result = {
                "file_path": os.path.abspath(file_path),
                "resume": resume,
                "warning": warning
            }
            
            return result
            
        except Exception as e:
            return {
                "file_path": file_path,
                "resume": f"Erreur lors du traitement : {str(e)}",
                "warning": False
            }

# ──────────────────────────────────────────────────────────────────────────
# Fonctions utilitaires
# ──────────────────────────────────────────────────────────────────────────
def process_file(file_path: str, offline_mode: bool = False) -> Dict[str, Any]:
    """Traite un fichier et retourne le résultat JSON"""
    agent = AgentNLP(llm if not offline_mode else None, offline_mode)
    return agent.process_file(file_path)

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

# ──────────────────────────────────────────────────────────────────────────
# Tests et exemples
# ──────────────────────────────────────────────────────────────────────────
def test_agent():
    """Test de l'agent avec différents fichiers"""
    print("=== Test Agent NLP ===\n")
    
    # Test 1: Fichier sans PII
    print("1. Test fichier sans PII")
    print("-" * 23)
    try:
        if os.path.exists("recit.txt"):
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
    print("2. Test fichier avec PII")
    print("-" * 23)
    
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
        print("Agent NLP - Résumé et Détection PII")
        print("===================================")
        print("Usage:")
        print("  python agent_nlp.py <fichier>                    # Sauvegarde automatique")
        print("  python agent_nlp.py <fichier> <sortie.json>      # Sauvegarde personnalisée")
        print("  python agent_nlp.py <fichier> --offline          # Mode offline")
        print("  python agent_nlp.py --test                       # Tests")
        print("\nExemples:")
        print("  python agent_nlp.py recit.txt                    # → recit_analysis.json")
        print("  python agent_nlp.py rapport.txt resultat.json")
        print("  python agent_nlp.py rapport.txt --offline")
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
            print("Connexion à Ollama...")
            try:
                test_response = llm.invoke("Test")
                print("✅ Connexion réussie")
            except:
                print("⚠️  Connexion Ollama échouée, passage en mode offline")
                offline_mode = True
        
        print(f"Traitement du fichier : {file_path}")
        print(f"Mode : {'Offline' if offline_mode else 'Online'}")
        
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
            
            print("\nRésultat JSON :")
            print(json_output)
            print(f"\n✅ Résultat sauvegardé dans : {output_file}")
        
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main()
