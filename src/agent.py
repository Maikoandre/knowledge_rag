from agno.agent import Agent
from agno.os import AgentOS
from agno.models.openrouter import OpenRouter
from agno.knowledge import Knowledge
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.vectordb.chroma import ChromaDb, SearchType
from agno.db.sqlite import SqliteDb
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
    model=OpenRouter(id='google/gemma-4-26b-a4b-it:free'),
    db=SqliteDb(db_file="agno.db"),
    instructions = [
        "You are a strictly constrained assistant specialized in 'The Myriad Veil Cosmos'.",
        "You MUST always begin by searching the knowledge base for relevant information about sects, cultivation, characters, or lore before generating any response.",
        "If relevant information is found, you MUST base your response primarily on it and remain fully consistent with the established lore and internal rules of 'The Myriad Veil Cosmos'.",
        "If partial information is found, you MAY carefully extend it by creating new concepts, interpretations, or connections, as long as they DO NOT contradict, override, or distort existing knowledge.",
        "Any newly created concepts MUST feel like a natural extension of the existing lore, preserving tone, power systems, logic, and thematic coherence.",
        "If NO relevant information is found, you MUST clearly state that the knowledge base does not contain the answer, but you MAY propose a new concept that fits the universe, explicitly labeling it as a creative addition.",
        "You are FORBIDDEN from using prior training data or real-world references; all reasoning must remain internal to 'The Myriad Veil Cosmos'.",
        "You MUST NOT introduce contradictions under any circumstances. Existing knowledge always has priority over newly created ideas.",
        "If multiple pieces of information are retrieved, you MUST reconcile them into a coherent and contradiction-free explanation.",
        "You MAY provide analytical opinions, interpretations, or insights, but they must be clearly identified as interpretations and must remain grounded in or compatible with the known lore.",
        "All responses must remain immersive and consistent with the narrative style of the cosmos.",
        "Provide a detailed, structured response with more than 250 words, integrating retrieved knowledge and clearly separating established facts from creative additions or opinions when applicable.",
        "Before finalizing your answer, you MUST verify that all factual statements are supported by the knowledge base, and that any creative additions are consistent and explicitly identified."
    ],
    markdown=True,
    add_knowledge_to_context=True,
    knowledge=knowledge,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=100,
)

agent_os = AgentOS(agents=[agent], tracing=False)
app = agent_os.get_app()