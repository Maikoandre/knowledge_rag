from fastapi import FastAPI, Request, WebSocket, BackgroundTasks
import os
import requests
import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from src.core.agent import agent
import src.core.logging

logger = logging.getLogger(__name__)


"""
$ uvicorn src.api.telegram:app --reload --port 8000
"""

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    webhook_url = os.getenv("NGROK_URL")
    send_url = f"https://api.telegram.org/bot{telegram_token}/setWebhook"
    try:
        requests.post(send_url, json={"url": webhook_url})
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
    yield

app = FastAPI(lifespan=lifespan)
telegram_token = os.getenv("TELEGRAM_TOKEN")

@app.websocket("/workflows/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass

def process_telegram_message(chat_id: int, text: str):
    logger.info("Running agent in background...")
    response = agent.run(text)
    agent_answer = response.content[:250] if response.content else ""
    if not agent_answer:
        logger.error("No content from agent.")
        return

        
    logger.debug(f"Agent answer length: {len(agent_answer)}")

    send_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    
    # Telegram max length is 4096
    chunks = [agent_answer[i:i+4096] for i in range(0, len(agent_answer), 4096)]
    
    for chunk in chunks:
        payload = {"chat_id": chat_id, "text": chunk}
        try:
            resp = requests.post(send_url, json=payload, timeout=10)
            if not resp.ok:
                logger.error(f"Telegram API failed: {resp.status_code} - {resp.text}")
            else:
                logger.debug(f"Telegram API response: {resp.status_code} - {resp.text}")
        except Exception as e:
            logger.error(f"Telegram API exception: {e}")


@app.post("/webhook")
async def handle_telegram(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    logger.debug(f"Received data: {data}")
    message = data.get("message", {})
    msg_chat_id = message.get("chat", {}).get("id")
    text = message.get("text")
    logger.debug(f"Extracted chat_id: {msg_chat_id} | text: {text}")

    if msg_chat_id and text:
        background_tasks.add_task(process_telegram_message, msg_chat_id, text)

    return {"status": "processed"}