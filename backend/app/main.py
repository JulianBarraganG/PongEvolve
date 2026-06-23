import asyncio
import logging

from fastapi import FastAPI, Depends, WebSocket

from app.config import get_settings, Settings
from pong.game import Pong
from pong.game_state import BallState, GameState

app = FastAPI()

SIM_HZ = 60  # fixed simulation tick rate

logger = logging.getLogger(__name__)

def serialize(game: Pong, tick: int) -> GameState:
    """Adapter (spec sec 7): translate the authoritative Pong object into a
    wire snapshot. Casts numpy scalars to Python floats so JSON works."""
    return GameState(
        tick=tick,
        ball=BallState(x=float(game.ball.x), y=float(game.ball.y)),
        agent=float(game.agent.y),
        human=float(game.human.y),
        score=game.score,
        game_over=game.game_over,
    )

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
        await ws.send_json(serialize(game, tick).model_dump())
        tick += 1
        await asyncio.sleep(1 / SIM_HZ)
