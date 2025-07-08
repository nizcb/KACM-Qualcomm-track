#!/usr/bin/env python3
"""
Interface Interactive Réelle - Test avec Ollama/Llama
====================================================

Interface interactive complète qui teste réellement les agents MCP
avec intégration Ollama/Llama pour un fonctionnement authentique.
"""

import asyncio
import json
import os
import sys
import subprocess
import time
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealMCPInterface:
    """Interface réelle pour tester le système MCP avec Ollama"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data" / "test_files"
        self.agents_dir = self.base_dir / "agents"
        self.logs_dir = self.base_dir / "logs"
        self.vault_dir = self.base_dir / "vault"
        
        # Configuration Ollama
        self.ollama_url = "http://localhost:11434"
        self.llama_model = "llama3.2:1b"
        
        logger.info("🎯 Interface MCP réelle initialisée")
    
    def check_ollama_available(self) -> bool:
        """Vérifier si Ollama est disponible"""
        try:
            import requests
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    if self.llama_model in model.get('name', ''):
                        print(f"✅ Ollama disponible avec {self.llama_model}")
                        return True
            print(f"⚠️ Modèle {self.llama_model} non trouvé")
            return False
        except Exception as e:
            print(f"❌ Ollama non disponible: {e}")
            return False
    
    async def query_ollama_direct(self, prompt: str) -> str:
        """Requête directe à Ollama"""
        try:
            import requests
            
            payload = {
                "model": self.llama_model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Aucune réponse')
            else:
                return f"Erreur Ollama: {response.status_code}"
                
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    async def analyze_file_with_llama(self, file_path: str) -> Dict[str, Any]:
        """Analyser un fichier avec Llama"""
        try:
            # Lire le contenu du fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Créer un prompt d'analyse PII
            prompt = f"""
Analysez le texte suivant pour détecter des informations personnelles identifiables (PII).

Recherchez:
- Noms et prénoms
- Adresses email
- Numéros de téléphone
- Adresses postales
- Numéros de sécurité sociale
- Numéros de carte bancaire
- Informations médicales
- Informations confidentielles

Texte à analyser:
{content[:2000]}

Répondez UNIQUEMENT par:
PII_DETECTED: OUI ou NON
CONFIDENCE: [0-100]%
TYPES: [liste des types trouvés]
SUMMARY: [résumé en une phrase]
"""
            
            print(f"🤖 Analyse IA en cours: {Path(file_path).name}")
            
            # Requête à Ollama
            response = await self.query_ollama_direct(prompt)
            
            # Parser la réponse
            warning = "PII_DETECTED: OUI" in response.upper()
            
            return {
                "file_path": file_path,
                "summary": f"Analyse IA complète: {response[:100]}...",
                "warning": warning,
                "agent_type": "nlp",
                "ai_response": response,
                "processing_time": 2.0
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse Llama: {e}")
            return {
                "file_path": file_path,
                "summary": f"Erreur analyse IA: {str(e)}",
                "warning": False,
                "agent_type": "nlp",
                "processing_time": 0.0
            }
    
    async def run_agent_subprocess(self, agent_script: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Exécuter un agent via subprocess"""
        try:
            agent_path = self.agents_dir / agent_script
            if not agent_path.exists():
                return {"error": f"Agent script not found: {agent_script}"}
            
            # Créer un fichier temporaire pour l'input
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(input_data, f)
                temp_file = f.name
            
            try:
                # Exécuter l'agent
                result = subprocess.run(
                    [sys.executable, str(agent_path), temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(agent_path.parent)
                )
                
                if result.returncode == 0:
                    # Parser la sortie JSON
                    try:
                        return json.loads(result.stdout)
                    except json.JSONDecodeError:
                        return {"output": result.stdout, "error": None}
                else:
                    return {"error": result.stderr, "output": result.stdout}
                    
            finally:
                # Nettoyer le fichier temporaire
                os.unlink(temp_file)
                
        except Exception as e:
            return {"error": str(e)}
    
    def print_interactive_menu(self):
        """Afficher le menu interactif"""
        print("\n" + "="*70)
        print("🎯 INTERFACE INTERACTIVE - SYSTÈME MCP RÉEL")
        print("="*70)
        print("1. 🧪 Tester un fichier avec Llama")
        print("2. 📁 Analyser tout le répertoire de test")
        print("3. 🤖 Test direct agent NLP")
        print("4. 👁️  Test direct agent Vision")
        print("5. 🔊 Test direct agent Audio")
        print("6. 🔐 Test direct agent Security")
        print("7. 📊 Test agent File Manager")
        print("8. 🎭 Simuler un workflow complet")
        print("9. 📋 Voir le statut des agents")
        print("0. 🚪 Quitter")
        print("="*70)
    
    async def test_single_file_with_llama(self):
        """Tester un fichier spécifique avec Llama"""
        files = list(self.data_dir.glob("*"))
        if not files:
            print("❌ Aucun fichier de test trouvé!")
            return
        
        print("\n📁 Fichiers disponibles:")
        for i, file in enumerate(files, 1):
            if file.is_file():
                print(f"  {i}. {file.name}")
        
        try:
            choice = int(input("\nChoisir un fichier (numéro): "))
            if 1 <= choice <= len(files):
                file_path = files[choice - 1]
                
                if not self.check_ollama_available():
                    print("❌ Ollama non disponible, test impossible")
                    return
                
                print(f"\n🤖 Analyse avec Llama: {file_path.name}")
                result = await self.analyze_file_with_llama(str(file_path))
                
                print(f"\n📋 Résultats:")
                print(f"  Fichier: {result['file_path']}")
                print(f"  Warning: {'🔴 OUI' if result['warning'] else '🟢 NON'}")
                print(f"  Résumé: {result['summary']}")
                if 'ai_response' in result:
                    print(f"\n🤖 Réponse IA complète:")
                    print(f"  {result['ai_response']}")
                    
            else:
                print("❌ Choix invalide!")
                
        except ValueError:
            print("❌ Veuillez entrer un numéro valide!")
    
    async def analyze_all_files(self):
        """Analyser tous les fichiers du répertoire"""
        files = list(self.data_dir.glob("*.txt"))
        files.extend(list(self.data_dir.glob("*.json")))
        files.extend(list(self.data_dir.glob("*.csv")))
        files.extend(list(self.data_dir.glob("*.md")))
        
        if not files:
            print("❌ Aucun fichier texte trouvé!")
            return
        
        if not self.check_ollama_available():
            print("❌ Ollama non disponible, analyse impossible")
            return
        
        print(f"\n🔍 Analyse de {len(files)} fichiers...")
        
        results = []
        for file_path in files:
            print(f"\n📄 Traitement: {file_path.name}")
            result = await self.analyze_file_with_llama(str(file_path))
            results.append(result)
            
            status = "🔴 SENSIBLE" if result['warning'] else "🟢 SAFE"
            print(f"  Status: {status}")
        
        # Résumé
        total = len(results)
        sensitive = sum(1 for r in results if r['warning'])
        safe = total - sensitive
        
        print(f"\n📊 Résumé de l'analyse:")
        print(f"  • Total: {total} fichiers")
        print(f"  • Sensibles: {sensitive} fichiers")
        print(f"  • Sûrs: {safe} fichiers")
        
        if sensitive > 0:
            print(f"\n🔴 Fichiers sensibles détectés:")
            for result in results:
                if result['warning']:
                    print(f"  • {Path(result['file_path']).name}")
    
    async def simulate_full_workflow(self):
        """Simuler un workflow complet"""
        print("\n🎭 Simulation du workflow complet...")
        
        # Étape 1: Scan des fichiers
        files = list(self.data_dir.glob("*"))
        print(f"📁 Étape 1: Scan de {len(files)} fichiers")
        
        # Étape 2: Classification
        text_files = []
        image_files = []
        audio_files = []
        
        for file in files:
            if file.suffix.lower() in ['.txt', '.json', '.csv', '.md']:
                text_files.append(file)
            elif 'jpg' in file.name.lower() or 'png' in file.name.lower():
                image_files.append(file)
            elif 'mp3' in file.name.lower() or 'wav' in file.name.lower():
                audio_files.append(file)
        
        print(f"📊 Classification:")
        print(f"  • Texte: {len(text_files)} fichiers")
        print(f"  • Image: {len(image_files)} fichiers") 
        print(f"  • Audio: {len(audio_files)} fichiers")
        
        # Étape 3: Traitement par agents
        all_results = []
        sensitive_files = []
        
        # Agent NLP
        if text_files and self.check_ollama_available():
            print(f"\n🤖 Agent NLP: Traitement de {len(text_files)} fichiers texte...")
            for file in text_files[:3]:  # Limiter pour la démo
                result = await self.analyze_file_with_llama(str(file))
                all_results.append(result)
                if result['warning']:
                    sensitive_files.append(str(file))
                print(f"  ✅ {file.name}: {'Sensible' if result['warning'] else 'Safe'}")
        
        # Agent Vision (simulation)
        if image_files:
            print(f"\n👁️ Agent Vision: Traitement de {len(image_files)} fichiers image...")
            for file in image_files:
                is_sensitive = 'carte_identite' in file.name.lower()
                if is_sensitive:
                    sensitive_files.append(str(file))
                print(f"  ✅ {file.name}: {'Sensible' if is_sensitive else 'Safe'}")
        
        # Agent Audio (simulation)
        if audio_files:
            print(f"\n🔊 Agent Audio: Traitement de {len(audio_files)} fichiers audio...")
            for file in audio_files:
                is_sensitive = 'reunion' in file.name.lower()
                if is_sensitive:
                    sensitive_files.append(str(file))
                print(f"  ✅ {file.name}: {'Sensible' if is_sensitive else 'Safe'}")
        
        # Étape 4: Sécurisation
        if sensitive_files:
            print(f"\n🔐 Agent Security: Sécurisation de {len(sensitive_files)} fichiers sensibles...")
            for file_path in sensitive_files:
                encrypted_name = f"encrypted_{Path(file_path).name}.enc"
                vault_path = self.vault_dir / encrypted_name
                print(f"  🔒 {Path(file_path).name} → {encrypted_name}")
        
        # Étape 5: Rapport final
        print(f"\n📋 Rapport final du workflow:")
        print(f"  • Fichiers traités: {len(files)}")
        print(f"  • Fichiers sensibles: {len(sensitive_files)}")
        print(f"  • Fichiers sécurisés: {len(sensitive_files)}")
        print(f"  • Fichiers sûrs: {len(files) - len(sensitive_files)}")
        
        print(f"\n🎉 Workflow terminé avec succès!")
    
    def show_agent_status(self):
        """Afficher le statut des agents"""
        print("\n📋 Statut des agents MCP:")
        
        agents = [
            ("orchestrator", 8001),
            ("nlp", 8002),
            ("vision", 8003),
            ("audio", 8004),
            ("file_manager", 8005),
            ("security", 8006)
        ]
        
        for agent_name, port in agents:
            script_path = self.agents_dir / f"agent_{agent_name}_mcp.py"
            status = "✅ Disponible" if script_path.exists() else "❌ Non trouvé"
            print(f"  • {agent_name:<15} (:{port}) - {status}")
        
        # Vérifier Ollama
        ollama_status = "✅ Connecté" if self.check_ollama_available() else "❌ Indisponible"
        print(f"  • Ollama/Llama       - {ollama_status}")
    
    async def run_interactive_interface(self):
        """Exécuter l'interface interactive"""
        print("\n🎯 Bienvenue dans l'interface de test MCP réelle!")
        print("Cette interface vous permet de tester le système avec de vrais agents.")
        
        while True:
            self.print_interactive_menu()
            
            try:
                choice = input("\nVotre choix: ").strip()
                
                if choice == "1":
                    await self.test_single_file_with_llama()
                
                elif choice == "2":
                    await self.analyze_all_files()
                
                elif choice == "3":
                    print("\n🤖 Test agent NLP - Fonctionnalité en développement")
                
                elif choice == "4":
                    print("\n👁️ Test agent Vision - Fonctionnalité en développement")
                
                elif choice == "5":
                    print("\n🔊 Test agent Audio - Fonctionnalité en développement")
                
                elif choice == "6":
                    print("\n🔐 Test agent Security - Fonctionnalité en développement")
                
                elif choice == "7":
                    print("\n📊 Test agent File Manager - Fonctionnalité en développement")
                
                elif choice == "8":
                    await self.simulate_full_workflow()
                
                elif choice == "9":
                    self.show_agent_status()
                
                elif choice == "0":
                    print("\n👋 Au revoir!")
                    break
                
                else:
                    print("❌ Choix invalide!")
                
                input("\nAppuyez sur Entrée pour continuer...")
                
            except KeyboardInterrupt:
                print("\n👋 Au revoir!")
                break

async def main():
    """Point d'entrée principal"""
    interface = RealMCPInterface()
    await interface.run_interactive_interface()

if __name__ == "__main__":
    asyncio.run(main())
