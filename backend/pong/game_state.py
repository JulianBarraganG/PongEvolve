from pydantic import BaseModel

from pong.const import BALL_SIZE, CANVAS_HEIGHT, CANVAS_WIDTH, PADDLE_HEIGHT, PADDLE_WIDTH

class GameState(BaseModel):
    x: int # Ball x-position
    y: int # Ball y-position
    vx: int # Ball x-velocity
    vy: int # Ball y-velocity
    p1: int # Player 1 y-position
    p2: int # Player 2 y-position
    score: tuple[int, int] = (0, 0) # (Player 1 score, Player 2 score)
    timestamp: int # 0 through end of game
    gameid: int # Unique game identifier

# ============= Frontend -> Backend =============
class HumanInput(BaseModel):
    """Human input, effectively action space"""
    human_input: int # 1 down, 0 hold, -1 up

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
    width: int = CANVAS_WIDTH # 4:3
    height: int = CANVAS_HEIGHT # 4:3
    paddle: tuple[int, int] = (PADDLE_WIDTH, PADDLE_HEIGHT)
    ball: int = BALL_SIZE
