from fastapi import FastAPI, Depends, WebSocket

from app.config import get_settings, Settings

app = FastAPI()

@app.get("/ping")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong",
        "environment": settings.environment,
        "testing": settings.testing,
    }

@app.websocket("/ws/{gameid}")
async def game_ws(ws: WebSocket, gameid: str):
    await ws.accept()
    while True:
        msg = await ws.receive_json()
        await ws.send_json({
            "type": "echo",
            "you_sent": msg,
            "gameid": gameid,
        })
