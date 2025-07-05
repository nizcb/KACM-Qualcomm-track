from audio_summary_agent import AudioSummaryAgent
from langchain.tools import tool
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

# Initialize the audio summary agent
agent_instance = AudioSummaryAgent()

# Wrap summarize_from_audio as a LangChain tool
@tool
def summarize_audio(file_path: str) -> str:
    """Summarize and classify the audio file for sensitive content."""
    result = agent_instance.summarize_from_audio(file_path)
    return f"Summary: {result['summary']}\nProtect: {result['protect']}\nReason: {result['reason']}"

# Register tools with LangChain
tools = [
    Tool.from_function(
        summarize_audio,
        name="audio_summary",
        description="Use this to transcribe, index, and summarize an audio file with security analysis."
    )
]

# Load LLaMA 3B from Ollama
llm = Ollama(model="llama3")

# Create the ReAct prompt template
prompt = PromptTemplate.from_template("""You are a local assistant that helps organize, analyze, and protect audio files. Use the audio_summary tool to process an audio file. Only summarize what is relevant and flag security-sensitive content.

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

Question: {input}
{agent_scratchpad}""")

# Create the ReAct agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# Create agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Run the agent interactively
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python react_agent_runner.py <audio_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    query = f"Summarize the file called '{file_path}' and tell me if it's sensitive."

    print("\n🤖 Agent response:")
    result = agent_executor.invoke({"input": query})
    print(result["output"])