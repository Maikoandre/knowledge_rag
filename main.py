from agno.os import AgentOS
from src.core.agent import agent

agent_os = AgentOS(agents=[agent], tracing=True)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve("agentos:app", reload=True)