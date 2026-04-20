from agno.agent import Agent
from agno.models.llama_cpp import LlamaCpp

agent = Agent(
    model=LlamaCpp(
        id='ggml-org/gemma-3-1b-it-GGUF',
        base_url="http://localhost:8080/v1"
    ),
    markdown=True
)

agent.print_response("Who is the god of the sea in the Chinese mythology?")