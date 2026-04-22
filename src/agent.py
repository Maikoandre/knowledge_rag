from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.knowledge import Knowledge
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.vectordb.chroma import ChromaDb, SearchType
from dotenv import load_dotenv

load_dotenv()

knowledge = Knowledge(
    vector_db=ChromaDb(
        collection="docs",
        path="tmp/chromadb",
        persistent_client=True,
        search_type=SearchType.vector,
        embedder=SentenceTransformerEmbedder(id="sentence-transformers/all-MiniLM-L6-v2")
    )
)

knowledge.insert(path='docs/', skip_if_exists=True)

agent = Agent(
    model=OpenRouter(
        id='openai/gpt-oss-120b:free',
    ),
    instructions = [
        "You are a strictly constrained assistant specialized in 'The Myriad Veil Cosmos'.",
        "You MUST only use information retrieved from the knowledge base when answering.",
        "Before generating any response, you MUST search the knowledge base for relevant information about sects, cultivation, characters, or lore.",
        "If relevant information is found, you MUST base your entire response exclusively on it.",
        "If NO relevant information is found, you MUST explicitly state that the knowledge base does not contain the answer and refuse to speculate or use external knowledge.",
        "You are FORBIDDEN from using prior training data, making assumptions, or inventing details not present in the knowledge base.",
        "You must not expand beyond the scope of the retrieved context under any circumstances.",
        "All responses must remain fully consistent with the internal lore and rules of 'The Myriad Veil Cosmos'.",
        "If multiple pieces of information are retrieved, you MUST reconcile them without contradiction and stay within their combined scope.",
        "Provide a detailed and structured response with more than 250 words, strictly grounded in the retrieved information.",
        "Before finalizing your answer, you MUST verify that every statement is directly supported by the retrieved knowledge base content. If any part is unsupported, remove it."
    ],
    markdown=True,
    add_knowledge_to_context=True,
    knowledge=knowledge
)

agent.print_response("What is the Nine Heavens?")