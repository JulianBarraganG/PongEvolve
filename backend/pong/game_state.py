from pydantic import BaseModel
from pathlib import Path
from pong.config_loader import Config
import json


# Load constants from JSON configuration file
CONSTANTS_PATH = Path(__file__).parent.parent.parent / "config" / "constants.json"

with open(CONSTANTS_PATH, "r") as f:
    data = json.load(f)
const = Config(**data)


class GameState(BaseModel):
    x: int # Ball x-position
    y: int # Ball y-position
    vel: float # Ball velocity
    angle: float # Ball angle
    p1: int # Player 1 y-position
    p2: int # Player 2 y-position
    score: tuple[int, int] = (0, 0) # (Player 1 score, Player 2 score)
    timestamp: int # 0 through end of game
    gameid: int # Unique game identifier


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
    width: int = const.canvas_width # 4:3
    height: int = const.canvas_eight # 4:3
    paddle: tuple[int, int] = (const.paddle_width, const.paddle_height)
    ball: int = const.ball_size
