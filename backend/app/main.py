import asyncio
import logging
import random

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect

from app.config import get_settings
from pong.game import Pong
from pong.game_state import GameState

app = FastAPI()

SIM_HZ = 60  # fixed simulation tick rate

logger = logging.getLogger(__name__)

@app.get("/ping")
async def health():
    settings = Depends(get_settings)
    return {
        "ping": "pong",
        "environment": settings.environment,
        "testing": settings.testing,
    }

@app.websocket("/ws/{game_id}")
async def game_ws(ws: WebSocket, game_id: str):
    await ws.accept()
    game = Pong()
    tick = 0
    # Ended tag will help us track terminated vs truncated DB for training data
    ended = "victory"  # vs "disconnected"
    human_dir = 0

    async def reader():
        nonlocal human_dir
        while True:
            msg = await ws.receive_json()
            if msg.get("type") == "input":
                human_dir = msg.get("dir", 0)

    read_task = asyncio.create_task(reader())

    try:
        while not game.game_over:
            game.move_paddle(human=True, dir=human_dir)
            game.move_paddle(human=False, dir=0)
            game.move_ball()
            # Currently we just send data, we don't receive input from frontend
            await ws.send_json(GameState.from_pong(game, tick).model_dump())
            tick += 1
            await asyncio.sleep(1 / SIM_HZ)
    except WebSocketDisconnect:
        ended = "disconnect"
    finally:
        read_task.cancel()
        logger.info(f"game {game_id} ended in {ended} at tick {tick}")
