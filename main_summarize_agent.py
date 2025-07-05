import sys
from agents.audio_summary_agent import AudioSummaryAgent

# Check for command-line argument
if len(sys.argv) < 2:
    print("Usage: python main_summarize_agent.py <audio_file_path>")
    sys.exit(1)

audio_path = sys.argv[1]

# Initialize and run the agent
agent = AudioSummaryAgent()
result = agent.summarize_from_audio(audio_path, sys.argv[2])

# Display the result
print("\n🎯 Result:")
for key, value in result.items():
    print(f"{key}: {value}")
