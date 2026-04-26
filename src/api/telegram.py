from fastapi import FastAPI, Request, WebSocket, BackgroundTasks
import os
import requests
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from src.core.agent import agent

"""
$ uvicorn src.api.telegram:app --reload --port 8000
"""

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    chunk_size = 1000
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