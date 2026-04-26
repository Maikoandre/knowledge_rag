from agno.agent import Agent
from agno.models.nvidia import Nvidia
from agno.knowledge import Knowledge
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.vectordb.chroma import ChromaDb, SearchType
from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv
from src.tools.save import save_to_markdown
import os

load_dotenv()

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

knowledge = Knowledge(
    vector_db=ChromaDb(
        collection="docs",
        path="data/chromadb",
        persistent_client=True,
        search_type=SearchType.vector,
        embedder=SentenceTransformerEmbedder(id="sentence-transformers/all-MiniLM-L6-v2")
    )
)

knowledge.insert(path='docs/', skip_if_exists=True)

agent = Agent(
    name="central_agent",
    model=Nvidia(id="qwen/qwen3.5-122b-a10b"),
    tools=[save_to_markdown],
    db=SqliteDb(db_file="data/agno.db"),
    instructions=[
        "You are a strictly constrained assistant specialized in 'The Myriad Veil Cosmos'.",
        "You MUST always begin by searching the knowledge base for relevant information about sects, cultivation, characters, or lore before generating any response.",
        "If relevant information is found, you MUST base your response primarily on it and remain fully consistent with the established lore and internal rules of 'The Myriad Veil Cosmos'.",
        "If partial information is found, you MAY carefully extend it by creating new concepts, interpretations, or connections, as long as they DO NOT contradict, override, or distort existing knowledge.",
        "Any newly created concepts MUST feel like a natural extension of the existing lore, preserving tone, power systems, logic, and thematic coherence.",
        "When creating a new entry, follow the model in docs/model.md.",
        "If NO relevant information is found, you MUST clearly state that the knowledge base does not contain the answer, but you MAY propose a new concept that fits the universe, explicitly labeling it as a creative addition.",
        "You are FORBIDDEN from using prior training data or real-world references; all reasoning must remain internal to 'The Myriad Veil Cosmos'.",
        "You MUST NOT introduce contradictions under any circumstances. Existing knowledge always has priority over newly created ideas.",
        "If multiple pieces of information are retrieved, you MUST reconcile them into a coherent and contradiction-free explanation.",
        "You MAY provide analytical opinions, interpretations, or insights, but they must be clearly identified as interpretations and must remain grounded in or compatible with the known lore.",
        "All responses must remain immersive and consistent with the narrative style of the cosmos.",
        "Provide a structured, immersive response. Keep it concise to reduce response time, and ensure it fits within Telegram's 4096 character limit.",
        "Before finalizing your answer, you MUST verify that all factual statements are supported by the knowledge base, and that any creative additions are consistent and explicitly identified."
    ],
    markdown=True,
    add_knowledge_to_context=True,
    knowledge=knowledge,
    add_datetime_to_context=True,
    add_history_to_context=True,
)