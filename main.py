from src.core.agent import agent
from agno.os import AgentOS

agent_os = AgentOS(agents=[agent], tracing=True)
app = agent_os.get_app()