"""
react_agent_runner.py

Detailed Explanation:
---------------------
This script creates a LangChain ReAct (Reasoning and Acting) agent that wraps the audio processing pipeline
for command-line usage. It combines the AudioSummaryAgent with LangChain's agent framework to provide
conversational AI capabilities for audio file analysis.

How it works:
- Wraps the AudioSummaryAgent as a LangChain tool for integration with LLM agents
- Creates a ReAct agent using LLaMA 3.1 (via Ollama) for reasoning and tool usage
- Provides a command-line interface for processing audio files with optional language forcing
- Handles both simple file processing and language-specific transcription requests

Key Components:
- ReAct Agent: Uses LangChain's reasoning/acting pattern for structured AI responses
- Tool Wrapper: Converts AudioSummaryAgent methods into LangChain-compatible tools
- Command Line Interface: Accepts audio file paths and optional language parameters
- Error Handling: Robust error handling for malformed LLM responses and tool failures

Dependencies:
- langchain: For agent framework and tool integration
- langchain_ollama: For LLaMA model integration via Ollama
- audio_summary_agent: Custom audio processing pipeline
- sys: For command-line argument processing

Usage Examples:
    # Basic audio processing with auto-detected language
    python react_agent_runner.py meeting.mp3
    
    # Force specific language for transcription
    python react_agent_runner.py meeting.mp3 en
    
    # Process audio in Spanish
    python react_agent_runner.py reunion.mp3 es
"""
from utils.audio_transcript_processor import AudioSummaryAgent
from langchain.tools import tool
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

# Initialize the audio summary agent instance
# This will be used by the LangChain tool wrapper
agent_instance = AudioSummaryAgent()

# System prompt that defines the agent's behavior and constraints
system_prompt = """
You are a local assistant that helps organize, analyze, and protect audio files.
When you call the tool `summarize_audio`, you must:
  1) Use it exactly once.
  2) After seeing the tool's result, immediately provide your Final Answer in JSON format.
  3) Do NOT call the tool again.
IMPORTANT: When you use Action Input, NEVER use quotes or extra formatting. Only use the raw file path, or file path and language code separated by a comma, with NO quotes.
If you were not given a language code, do NOT add one.
Your Final Answer must start with "Final Answer:" and contain a JSON object.
"""

# Wrap summarize_from_audio as a LangChain tool
@tool
def summarize_audio(input_string: str) -> str:
    """
    Summarize and classify the audio file for sensitive content.
    
    This tool wraps the AudioSummaryAgent's summarize_from_audio method to make it
    compatible with LangChain's tool interface. It handles parsing of input parameters
    and formatting of output results.
    
    Args:
        input_string (str): File path, optionally followed by comma and language code 
                           (e.g., "audio.mp3" or "audio.mp3,en")
    
    Returns:
        str: Formatted string containing summary, warning status, and filepath
    """
    # Parse input string to extract file path and optional language code
    input_string = input_string.strip().strip("'").strip('"')
    parts = input_string.strip().split(',')
    file_path = parts[0].strip()
    forced_lang = parts[1].strip() if len(parts) > 1 else None

    try:
        # Call the underlying audio processing pipeline
        result = agent_instance.summarize_from_audio(file_path, forced_lang)
        
        # Format the result clearly for the agent
        return f"""AUDIO ANALYSIS COMPLETE:
Summary: {result['summary']}
Warning: {result['warning']}
Filepath: {result['filepath']}

TASK FINISHED - Provide Final Answer now."""
    except Exception as e:
        # Return error information if processing fails
        return f"Error processing {file_path}: {str(e)}"

# Register tools with LangChain
# Each tool needs a name, description, and function reference
tools = [
    Tool.from_function(
        summarize_audio,
        name="audio_summary",
        description="Use this to transcribe, index, and summarize an audio file with security analysis. Input: file path, optionally followed by comma and language code (e.g., 'audio.mp3' or 'audio.mp3,en')."
    )
]

# Load LLaMA model from Ollama
# Make sure you have llama3.1:8b installed via: ollama pull llama3.1:8b
llm = OllamaLLM(model="llama3.1:8b")

# Create the ReAct prompt template with clear instructions
# This template defines the reasoning/acting loop format the LLM should follow
# Update the ReAct prompt template to be more restrictive
prompt = PromptTemplate.from_template("""You are a local assistant that helps organize, analyze, and protect audio files. Use the audio_summary tool to process an audio file. You must call audio_summary exactly once and then immediately provide your Final Answer.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the file path (and optional language code separated by comma)
Observation: the result of the action
Thought: I now know the final answer
Final Answer: the final answer as a JSON object

IMPORTANT: 
- Call audio_summary exactly ONCE
- After getting the Observation, immediately provide Final Answer
- Do NOT call the tool multiple times
- Action Input must be the raw file path (e.g., test.mp3) or file path and language code (e.g., test.mp3,en) with NO quotes, NO brackets, and NO extra formatting.
- Only include a language code if it was provided in the question.

Question: {input}
{agent_scratchpad}""")

# Combine system prompt with ReAct template
full_template = system_prompt + "\n\n" + prompt.template
prompt = PromptTemplate.from_template(full_template)

# Create the ReAct agent
# This agent will use the LLM to reason about when and how to use tools
agent = create_react_agent(
    llm=llm,           # Language model for reasoning
    tools=tools,       # Available tools the agent can use
    prompt=prompt      # Template that defines the agent's behavior
)

# Create agent executor
# This manages the execution of the agent with error handling and logging
agent_executor = AgentExecutor(
    agent=agent,                    # The ReAct agent instance
    tools=tools,                    # Tools available to the agent
    verbose=True,                   # Enable detailed logging of agent steps
    handle_parsing_errors=True,      # Automatically handle malformed LLM responses
)

# Main execution block - handles command-line usage
if __name__ == "__main__":
    import sys
    
    # Check for required command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python react_agent_runner.py <audio_file1> [audio_file2 ...] [forced_lang]\nforced_lang is optional and applies to all files.")
        sys.exit(1)


    # Detect if the last argument is a language code (e.g., 'en', 'es', 'fr')
    possible_lang = sys.argv[-1]
    audio_files = sys.argv[1:-1] if len(sys.argv) > 2 and len(possible_lang) <= 5 else sys.argv[1:]
    forced_lang = possible_lang if len(sys.argv) > 2 and len(possible_lang) <= 5 else None

    if not audio_files:
        print("No audio files specified.")
        sys.exit(1)

    for file_path in audio_files:
        if forced_lang:
            query = f"Use the audio_summary tool to analyze {file_path} with forced language {forced_lang}. The Action Input should be exactly: {file_path},{forced_lang}"
        else:
            query = f"Use the audio_summary tool to analyze {file_path}. The Action Input should be exactly: {file_path}"

        print(f"\n🤖 Agent response for {file_path}:")
        try:
            result = agent_executor.invoke({"input": query})
            print(result["output"])
        except Exception as e:
            print(f"Error processing {file_path}: {e}")