from pydantic import BaseModel
from pathlib import Path
from pong.config_loader import Config
import json


# Load constants from JSON configuration file
CONSTANTS_PATH = Path(__file__).parent.parent.parent / "config" / "constants.json"

with open(CONSTANTS_PATH, "r") as f:
    data = json.load(f)
const = Config(**data)


class BallState(BaseModel):
    x: float # Ball x-position (game units)
    y: float # Ball y-position (game units)
    # vx/vy intentionally omitted for v0.1: server sends every tick, so the
    # client has no gaps to fill. Velocity returns with the extrapolation
    # smoothing layer (see docs/websocket-protocol.md sec 9).


class GameState(BaseModel):
    """Server -> client snapshot. Fields named by role (agent/human),
    never positional, so the wire order can't be gotten wrong."""
    type: str = "state"
    tick: int # monotonic sim tick this snapshot was sampled at
    ball: BallState
    agent: float # agent paddle y-position
    human: float # human paddle y-position
    score: dict[str, int] = {"agent": 0, "human": 0}
    game_over: bool = False


# ============= Frontend -> Backend =============
class HumanInput(BaseModel):
    """Human input, effectively action space"""
    human_input: int # consider bool? char? just checking 0/1

#TODO: Request game, leave game?
class RequestGame(BaseModel):
    """
    Handles client side request to start a game.
    Subsequent step would be create unique game id.
    """
    pass

class LeaveGame(BaseModel):
    """
    Handles finishing a game(id), e.g. broken connection, leave game,
    surrender, decisive outcomes etc.
    This should trigger breaking handshake,
    and creating completed game database instance.
    """
    pass

# ============= Backend -> Frontend =============

# Continued game -- send updated gamestate, matching gameid
# Fresh game -- make a unique gameid

# ================= Other ======================

class ScreenConfig(BaseModel):
    """Collision detection relevant parameters.
    Other relevant parameters for rendering computed in frontend."""
    width: int = const.game_width # 4:3
    height: int = const.game_height # 4:3
    paddle: tuple[int, int] = (const.paddle_width, const.paddle_height)
    ball: int = const.ball_size
