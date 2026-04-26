from agno.agent import Agent
from agno.models.nvidia import Nvidia
from agno.tools.telegram import TelegramTools
from src.tools.save import save_to_markdown
from agno.knowledge import Knowledge
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.vectordb.chroma import ChromaDb, SearchType
from agno.db.sqlite import SqliteDb
from fastapi import FastAPI, Request, WebSocket, BackgroundTasks
import os
import requests
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

"""
$ uvicorn src.api.telegram:app --reload --port 8000
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set webhook on startup
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    webhook_url = "https://adena-readjustable-anaya.ngrok-free.dev/webhook"
    send_url = f"https://api.telegram.org/bot{telegram_token}/setWebhook"
    try:
        requests.post(send_url, json={"url": webhook_url})
    except Exception as e:
        print(f"Failed to set webhook: {e}")
    yield

app = FastAPI(lifespan=lifespan)

telegram_token = os.getenv("TELEGRAM_TOKEN")
chat_id = "6354092683"

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
    name="telegram",
    db=SqliteDb(db_file="agno.db"),
    model=Nvidia(id="deepseek-ai/deepseek-v4-flash"),
    instructions=[
        "You are a helpful assistant via Telegram.",
        "If I ask you to save your response, use the 'save_to_markdown' tool.",
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
    tools=[TelegramTools(token=telegram_token, chat_id=chat_id), save_to_markdown],
    add_knowledge_to_context=True,
    knowledge=knowledge,
    add_datetime_to_context=True,
    add_history_to_context=True,
)

@app.websocket("/workflows/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass



def process_telegram_message(chat_id: int, text: str):
    print("DEBUG: Running agent in background...")
    response = agent.run(text)
    agent_answer = response.content
    print(f"DEBUG: Agent answer length: {len(agent_answer)}")

    send_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    
    # Split into chunks of 4000 chars to fit Telegram API limits
    chunk_size = 4000
    for i in range(0, len(agent_answer), chunk_size):
        chunk = agent_answer[i:i + chunk_size]
        payload = {"chat_id": chat_id, "text": chunk}
        resp = requests.post(send_url, json=payload)
        print(f"DEBUG: Telegram API response: {resp.status_code} - {resp.text}")

@app.post("/webhook")
async def handle_telegram(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    print(f"DEBUG: Received data: {data}")
    message = data.get("message", {})
    msg_chat_id = message.get("chat", {}).get("id")
    text = message.get("text")
    print(f"DEBUG: Extracted chat_id: {msg_chat_id} | text: {text}")

    if msg_chat_id and text:
        background_tasks.add_task(process_telegram_message, msg_chat_id, text)

    return {"status": "processed"}

    # https://adena-readjustable-anaya.ngrok-free.dev/