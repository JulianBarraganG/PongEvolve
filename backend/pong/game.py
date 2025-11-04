from pong.const import CANVAS_HEIGHT, CANVAS_WIDTH, PADDLE_WIDTH

import numpy as np

class Ball:
    def __init__(self) -> None:
        self.x: int = 0
        self.y: int = 0
        self.vx: float = 0.
        self.vy: float = 0.

class Paddle:
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

class Game():
    def __init__(self) -> None:
        self.ball: Ball | None = None
        self.player1: Paddle = Paddle(PADDLE_WIDTH, (CANVAS_HEIGHT // 2))
        self.player2: Paddle = Paddle(CANVAS_WIDTH - 2*PADDLE_WIDTH, (CANVAS_HEIGHT // 2))
        self._get_ball_position()

    def _get_ball_position(self) -> None:
        self.ball = Ball()
        # Compute and set y 
        y = np.random.normal(loc=CANVAS_HEIGHT // 2, scale=CANVAS_HEIGHT // 8)
        y = int(np.clip(y, 0, CANVAS_HEIGHT))
        self.ball.y = y
        # Set x
        self.ball.x = CANVAS_WIDTH // 2
        # Set velocity (0 for now)
        self.ball.vx = 0.
        self.ball.vy = 0.
