from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.nvidia import Nvidia
from agno.os import AgentOS
from agno.tools.mcp import MCPTools
from dotenv import load_dotenv

load_dotenv()

agno_assist = Agent(
    name="Agno Assist",
    model=Nvidia(id="qwen/qwen3.5-122b-a10b"),
    db=SqliteDb(db_file="agno.db"),                     # session storage
    tools=[MCPTools(url="https://docs.agno.com/mcp")],  # Agno docs via MCP
    add_datetime_to_context=True,
    add_history_to_context=True,                         # include past runs
    num_history_runs=3,                                  # last 3 conversations
    markdown=True,
)

# Serve via AgentOS → streaming, auth, session isolation, API endpoints
agent_os = AgentOS(agents=[agno_assist], tracing=True)
app = agent_os.get_app()