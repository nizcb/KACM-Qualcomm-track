"""
audio_summary_agent.py

Detailed Explanation:
---------------------
This script provides a complete audio processing pipeline that transcribes audio files, indexes them in a vector database, and generates AI-powered summaries with security analysis. It combines Whisper for transcription and LLaMA for intelligent content analysis.

How it works:
- Transcribes audio files using OpenAI's Whisper model (with GPU acceleration if available)
- Uses LLaMA (via Ollama) to generate summaries and analyze content for security-sensitive information
- Saves all results (transcripts, metadata, summaries) to the data/audio/ directory

Dependencies:
- whisper: For speech-to-text transcription (pip install openai-whisper)
- torch: For running Whisper with GPU acceleration (pip install torch)
- spacy: For natural language processing (pip install spacy)
- ollama: For running LLaMA models locally (install from https://ollama.ai/)
- subprocess, json, os, re: Python's built-in modules

Key Features:
- Complete audio-to-summary pipeline in one class
- GPU-accelerated transcription when available
- Semantic search capabilities over transcript collection
- AI-powered content analysis and security assessment
- Automatic file organization and metadata management

Usage Examples:
    # Initialize the agent
    agent = AudioSummaryAgent()
    
    # Process a new audio file
    result = agent.summarize_from_audio("meeting.mp3")
    
    # Search existing transcripts and summarize
    result = agent.summarize("What did John say about the budget?")
"""

# Import required libraries
import subprocess  # For running external commands (Ollama)
import json  # For JSON file handling
import os  # For file and directory operations
import re  # For regular expression matching
import whisper  # OpenAI's speech-to-text model
import torch  # PyTorch for GPU acceleration

class AudioSummaryAgent:
    """
    A comprehensive audio processing agent that handles transcription, indexing, and AI-powered summarization.
    
    This class provides a complete pipeline for:
    - Audio transcription using Whisper
    - AI-powered content analysis using LLaMA
    """
    
    def __init__(self, data_path="data/audio"):
        """
        Initialize the AudioSummaryAgent with necessary components.
        
        Args:
            data_path (str): Path to store audio transcripts and metadata
        """
        # Store configuration paths
        self.data_path = data_path

        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)

        # Initialize Whisper model with GPU support if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"  # Check for GPU availability
        # Print device information
        print("🔧 PyTorch version:", torch.__version__)
        print("🖥️ Using device:", self.device.upper())
        print("📊 CUDA available:", torch.cuda.is_available())
        print("📊 CUDA device count:", torch.cuda.device_count())
        
        # Print GPU information if available
        if torch.cuda.is_available():
            print("⚡ GPU:", torch.cuda.get_device_name(0))
            print("💾 GPU memory:", f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            print("⚠️ Running on CPU - GPU acceleration not available")
        # Existing models: "tiny", "base", "small", "medium", or "large"
        self.whisper_model = whisper.load_model("medium").to(self.device)  # Load medium model and move to device

    def transcribe_audio(self, audio_path, forced_lang=None):
        """
        Transcribe an audio file to text using Whisper.
        
        Args:
            audio_path (str): Path to the audio file
            forced_lang (str, optional): Force a specific language for transcription
            
        Returns:
            tuple: (document_id, transcript_text, metadata_dict)
        """
        # Print transcription status
        print(f"🎧 Transcribing: {audio_path}")
        
        # Run Whisper transcription with or without language forcing
        result = self.whisper_model.transcribe(audio_path, language=forced_lang) if forced_lang else self.whisper_model.transcribe(audio_path)
        
        # Extract transcript text from result
        transcript = result["text"]
        # Generate base filename without extension for file naming
        base = os.path.splitext(os.path.basename(audio_path))[0]

        # Create metadata dictionary with file info
        metadata = {
            "filepath": os.path.abspath(audio_path),  # Absolute path to original audio
            "language": result.get("language", "unknown"),  # Detected language
            "transcript": transcript  # Full transcript text
        }
        # Return document ID, transcript, and metadata
        return base, transcript, metadata

    def summarize_from_audio(self, audio_path: str, forced_lang=None, model_name="llama3.1:8b") -> dict:
        """
        Complete pipeline: transcribe audio, index it, and generate summary.
        
        Args:
            audio_path (str): Path to audio file to process
            forced_lang (str, optional): Force specific language for transcription
            model_name (str): LLaMA model name for summarization
            
        Returns:
            dict: Summary and analysis results from LLaMA
        """
        # Step 1: Transcribe the audio file
        doc_id, transcript, metadata = self.transcribe_audio(audio_path, forced_lang)
        
        # Step 2: Generate summary using LLaMA
        return self._run_llama(doc_id, transcript, metadata, model_name)

    def _run_llama(self, doc_id, transcript, metadata, model_name):
        """
        Run LLaMA model to analyze transcript and generate summary.
        
        Args:
            doc_id (str): Document identifier
            transcript (str): Full transcript text
            metadata (dict): Document metadata
            model_name (str): LLaMA model name
            
        Returns:
            dict: Parsed JSON response from LLaMA or error information
        """
        # Create detailed prompt for LLaMA analysis
        prompt = f'''
You are an assistant helping organize and protect user files. The following is a transcript of an audio file:

"""{transcript}"""

Your task is to:
1. Summarize the file content in no more than 100 words. Make it concise and clear, focusing on the main points discussed in the audio.
2. Identify if the speaker shared any SECURITY-SENSITIVE information such as:
   - Credit card numbers, passwords, API keys, tokens
   - Social security numbers, government IDs
   - Names, addresses, phone numbers, emails
   - Age, birthdate, personal contracts
   - Any information that could be used for identity theft or scams

IMPORTANT: Do NOT classify emotions, fears, opinions, or general personal thoughts as sensitive information.

3. Determine if this file needs to be protected based ONLY on:
   - Actual sensitive security data (like passwords, credit cards, SSN, etc.)
   - Nudity or sexual content
   - Information that could be used for identity theft or scams

Do NOT protect files that only contain emotions, fears, or personal opinions.

Return your response as a valid JSON object in this format:

{{
  "summary": "<A concise summary of the transcript in no more than 6 lines>",
  "warning": false,
  "filepath": "{metadata['filepath']}"
}}

and make sure the filepath is correctly formatted with double backslashes (\\) for Windows paths. And for macOs and Linux, use single forward slashes (/).

'''

        # Print status message
        print("🦙 Running LLaMA via Ollama...")

        # Check if Ollama is available
        try:
            # Test if ollama command exists
            subprocess.run(["ollama", "--version"], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {
                "summary": None,
                "warning": None,
                "filepath": metadata['filepath']
            }
        
        # Execute Ollama command with the prompt
        result = subprocess.run(
            ["ollama", "run", model_name, prompt],  # Command to run LLaMA
            stdout=subprocess.PIPE,  # Capture standard output
            stderr=subprocess.PIPE,  # Capture error output
            text=True, encoding="utf-8"  # Text mode with UTF-8 encoding
        )

        try:
            # Extract JSON from LLaMA output using regex
            match = re.search(r"\{[\s\S]*\}", result.stdout)  # Find JSON pattern
            if match:
                # Parse the JSON response
                llama_json = json.loads(match.group(0))
            else:
                # Raise error if no JSON found
                raise ValueError("No JSON found in LLaMA output.")

            # Save LLaMA summary to file
            llama_path = os.path.join(self.data_path, f"{doc_id}.metadata.json")
            with open(llama_path, "w", encoding="utf-8") as f:
                json.dump(llama_json, f, indent=2, ensure_ascii=False)  # Pretty print with UTF-8

            # Return parsed JSON response
            return llama_json

        except Exception as e:
            # Return error information if parsing fails
            return {
                "summary": None,
                "warning": None,
                "filepath": metadata['filepath']
            }