"""
react_audio_agent.py

Detailed Explanation:
---------------------
This script creates a ReAct (Reasoning and Acting) agent using LangChain that can process audio files, 
search transcripts, and generate summaries. It uses LLaMA 3B as the reasoning engine and provides 
tools for audio transcription, database querying, and content analysis.

How it works:
- Uses LangChain's ReAct agent framework for reasoning and tool selection
- Integrates with Ollama to run LLaMA 3B locally
- Provides tools for audio processing, transcript search, and summarization
- Maintains conversation history and can handle complex multi-step tasks

Dependencies:
- langchain: For agent framework and tools (pip install langchain)
- langchain-community: For Ollama integration (pip install langchain-community)
- ollama: For running LLaMA models locally (install from https://ollama.ai/)
- Plus all dependencies from AudioSummaryAgent

Key Features:
- ReAct agent that can reason about tasks and select appropriate tools
- Audio transcription and indexing capabilities
- Semantic search over transcript database
- AI-powered content analysis and security assessment
- Conversational interface with memory

Usage Examples:
    # Initialize the agent
    agent = ReactAudioAgent()
    
    # Process audio and ask questions
    response = agent.run("Please transcribe the file test.mp3 and tell me what it's about")
    
    # Search existing transcripts
    response = agent.run("Find transcripts where someone mentions their fears")
"""

# Import required libraries
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferWindowMemory
import os
import sys

# Add the parent directory to the path to import AudioSummaryAgent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.audio_summary_agent import AudioSummaryAgent

class ReactAudioAgent:
    """
    A ReAct agent that can process audio files, search transcripts, and generate summaries.
    
    This agent uses LangChain's ReAct framework to reason about tasks and select appropriate tools
    for audio processing, database querying, and content analysis.
    """
    
    def __init__(self, model_name="llama3.2:3b"):
        """
        Initialize the ReAct Audio Agent.
        
        Args:
            model_name (str): Name of the LLaMA model to use via Ollama
        """
        # Initialize the audio processing backend
        self.audio_agent = AudioSummaryAgent()
        
        # Initialize the LLM via Ollama
        self.llm = Ollama(model=model_name, temperature=0.1)
        
        # Create tools for the agent
        self.tools = self._create_tools()
        
        # Create system prompt for the ReAct agent
        self.system_prompt = self._create_system_prompt()
        
        # Create the ReAct agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.system_prompt
        )
        
        # Create agent executor with memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=5  # Keep last 5 exchanges
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def _create_tools(self):
        """
        Create tools for the ReAct agent.
        
        Returns:
            list: List of LangChain tools
        """
        tools = []
        
        # Tool 1: Transcribe audio file
        def transcribe_audio_tool(audio_path: str) -> str:
            """
            Transcribe an audio file to text and save it to the database.
            
            Args:
                audio_path (str): Path to the audio file
                
            Returns:
                str: Success message with transcript preview
            """
            try:
                # Transcribe the audio
                doc_id, transcript, metadata = self.audio_agent.transcribe_audio(audio_path)
                
                # Index it in the database
                self.audio_agent.index_transcript(doc_id, transcript, metadata)
                
                # Return success message with preview
                preview = transcript[:200] + "..." if len(transcript) > 200 else transcript
                return f"✅ Successfully transcribed {audio_path}\n📝 Preview: {preview}\n🔗 Language: {metadata['language']}"
                
            except Exception as e:
                return f"❌ Error transcribing audio: {str(e)}"
        
        tools.append(Tool(
            name="transcribe_audio",
            description="Transcribe an audio file (MP3, WAV, etc.) to text and save it to the database. Use this when the user asks to transcribe or process an audio file.",
            func=transcribe_audio_tool
        ))
        
        # Tool 2: Search transcript database
        def search_transcripts_tool(query: str) -> str:
            """
            Search the transcript database for relevant content.
            
            Args:
                query (str): Search query
                
            Returns:
                str: Search results with transcript previews
            """
            try:
                # Search the database
                results = self.audio_agent.collection.query(query_texts=[query], n_results=3)
                
                if not results['documents'] or not results['documents'][0]:
                    return "❌ No transcripts found matching your query."
                
                # Format results
                formatted_results = "🔍 Search Results:\n\n"
                for i, (doc_id, transcript, metadata, distance) in enumerate(zip(
                    results['ids'][0], 
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    preview = transcript[:300] + "..." if len(transcript) > 300 else transcript
                    formatted_results += f"📄 Result {i+1}:\n"
                    formatted_results += f"   🔗 File: {metadata['filepath']}\n"
                    formatted_results += f"   📊 Similarity: {distance:.3f}\n"
                    formatted_results += f"   📝 Content: {preview}\n\n"
                
                return formatted_results
                
            except Exception as e:
                return f"❌ Error searching transcripts: {str(e)}"
        
        tools.append(Tool(
            name="search_transcripts",
            description="Search the transcript database using natural language queries. Use this to find specific content, topics, or information across all transcribed audio files.",
            func=search_transcripts_tool
        ))
        
        # Tool 3: Generate summary and analysis
        def analyze_transcript_tool(query: str) -> str:
            """
            Find the most relevant transcript and generate a detailed summary with security analysis.
            
            Args:
                query (str): Query to find relevant transcript
                
            Returns:
                str: Formatted summary and analysis
            """
            try:
                # Use the audio agent's summarize method
                result = self.audio_agent.summarize(query)
                
                # Format the result
                formatted_result = "📋 Summary and Analysis:\n\n"
                formatted_result += f"📝 Summary: {result.get('summary', 'No summary available')}\n\n"
                formatted_result += f"🔒 Contains PII: {'Yes' if result.get('contains_pii') else 'No'}\n"
                formatted_result += f"🛡️ Needs Protection: {'Yes' if result.get('protect') else 'No'}\n"
                formatted_result += f"💡 Reason: {result.get('reason', 'No reason provided')}\n"
                formatted_result += f"📂 File: {result.get('filepath', 'Unknown')}\n"
                
                return formatted_result
                
            except Exception as e:
                return f"❌ Error analyzing transcript: {str(e)}"
        
        tools.append(Tool(
            name="analyze_transcript",
            description="Find the most relevant transcript based on a query and generate a detailed summary with security analysis. Use this when the user wants a comprehensive analysis of content.",
            func=analyze_transcript_tool
        ))
        
        # Tool 4: Complete audio processing pipeline
        def process_audio_complete_tool(audio_path: str) -> str:
            """
            Complete pipeline: transcribe audio, index it, and generate summary.
            
            Args:
                audio_path (str): Path to audio file
                
            Returns:
                str: Complete processing results
            """
            try:
                # Use the complete pipeline
                result = self.audio_agent.summarize_from_audio(audio_path)
                
                # Format the result
                formatted_result = "🎯 Complete Audio Processing Results:\n\n"
                formatted_result += f"📝 Summary: {result.get('summary', 'No summary available')}\n\n"
                formatted_result += f"🔒 Contains PII: {'Yes' if result.get('contains_pii') else 'No'}\n"
                formatted_result += f"🛡️ Needs Protection: {'Yes' if result.get('protect') else 'No'}\n"
                formatted_result += f"💡 Reason: {result.get('reason', 'No reason provided')}\n"
                formatted_result += f"📂 File: {result.get('filepath', 'Unknown')}\n"
                
                return formatted_result
                
            except Exception as e:
                return f"❌ Error processing audio: {str(e)}"
        
        tools.append(Tool(
            name="process_audio_complete",
            description="Complete audio processing pipeline: transcribe, index, and analyze an audio file in one step. Use this when the user wants full processing of a new audio file.",
            func=process_audio_complete_tool
        ))
        
        return tools
    
    def _create_system_prompt(self):
        """
        Create the system prompt for the ReAct agent.
        
        Returns:
            PromptTemplate: LangChain prompt template
        """
        template = """You are an intelligent audio processing assistant that can help users transcribe audio files, search through transcripts, and analyze content for security concerns.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Guidelines:
1. Always transcribe audio files before searching or analyzing them
2. When searching, use natural language queries that match what the user is looking for
3. Be helpful and provide clear explanations of what you're doing
4. If a file needs protection due to sensitive information, clearly explain why
5. Emotions, fears, and personal opinions are NOT considered sensitive information
6. Only flag content as sensitive if it contains actual security risks (passwords, credit cards, SSN, etc.)

Previous conversation:
{chat_history}

Question: {input}
{agent_scratchpad}"""

        return PromptTemplate.from_template(template)
    
    def run(self, query: str) -> str:
        """
        Run the ReAct agent with a user query.
        
        Args:
            query (str): User's question or request
            
        Returns:
            str: Agent's response
        """
        try:
            # Print the query for debugging
            print(f"🤖 Processing query: {query}")
            
            # Run the agent
            response = self.agent_executor.invoke({"input": query})
            
            # Return the output
            return response.get("output", "No response generated")
            
        except Exception as e:
            return f"❌ Error processing query: {str(e)}"

# Example usage and testing
if __name__ == "__main__":
    # Initialize the agent
    print("🚀 Initializing ReAct Audio Agent...")
    agent = ReactAudioAgent()
    
    print("\n🎯 ReAct Audio Agent is ready!")
    print("You can now ask questions like:")
    print("- 'Please transcribe the file test.mp3'")
    print("- 'Search for transcripts about fears or emotions'")
    print("- 'Analyze the content of my audio files for security risks'")
    print("- 'Process the audio file meeting.mp3 completely'")
    
    # Interactive loop
    while True:
        try:
            user_input = input("\n🎤 Ask me anything (or 'quit' to exit): ")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if user_input.strip():
                response = agent.run(user_input)
                print(f"\n🤖 Agent Response:\n{response}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")