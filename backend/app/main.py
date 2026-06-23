import asyncio
import logging

from fastapi import FastAPI, Depends, WebSocket

from app.config import get_settings, Settings
from pong.game import Pong
from pong.game_state import GameState

app = FastAPI()

SIM_HZ = 60  # fixed simulation tick rate

logger = logging.getLogger(__name__)

@app.get("/ping")
async def health(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong",
        "environment": settings.environment,
        "testing": settings.testing,
    }

@app.websocket("/ws/{gameid}")
async def game_ws(ws: WebSocket, gameid: str):
    await ws.accept()
    game = Pong()
    tick = 0
    while not game.game_over:
        game.move_paddle(human=False, dir=1)
        game.move_ball()
        # Currently we just send data, we don't receive input from frontend
        await ws.send_json(GameState.from_pong(game, tick).model_dump())
        tick += 1
        await asyncio.sleep(1 / SIM_HZ)
