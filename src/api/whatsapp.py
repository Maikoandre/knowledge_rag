from fastapi import FastAPI, Request, WebSocket
import requests
import os
from src.core.agent import agent

"""
$ uvicorn src.api.whatsapp:app --reload --port 8000
"""

app = FastAPI()

EVOLUTION_URL = "https://evolution.imepag.com.br"
INSTANCE_NAME = "agno"
API_KEY = os.getenv("API_KEY")

@app.websocket("/workflows/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass

@app.post("/webhook")
async def handle_whatsapp(request: Request):
    data = await request.json()
    message_text = data.get("data", {}).get("message", {}).get("conversation")
    key = data.get("data", {}).get("key", {})
    remote_jid = key.get("remoteJid", "")
    from_me = key.get("fromMe", False)
    number = remote_jid.split("@")[0] if remote_jid else ""
    
    print(f"Texto: {message_text} | Remetente: {number} | fromMe: {from_me}")

    if message_text and number and not from_me:
        response = agent.run(message_text)
        agent_answer = response.content

        send_url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
        headers = {"apikey": API_KEY, "Content-Type": "application/json"}
        payload = {"number": number, "text": agent_answer}
        r = requests.post(send_url, json=payload, headers=headers)

    return {"status": "processed"}