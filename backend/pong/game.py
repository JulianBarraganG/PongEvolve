import logging
import numpy as np
from pydantic import BaseModel
import json
from pong.config_loader import Config

from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

CONSTANTS_PATH = Path(__file__).parent.parent.parent / "config" / "constants.json"

class Ball:
    """Class representing the ball in the Pong game."""
    def __init__(self) -> None:
        self.x: float
        self.y: float

    def __repr__(self) -> str:
        return f"Ball with pos=({self.x}, {self.y})"

class Paddle:
    """Class representing a paddle in the Pong game."""
    def __init__(self, x: int, y: float) -> None:
        self.x: int = x
        self.y: float = y

    def __repr__(self) -> str:
        return f"Paddle with pos=({self.x}, {self.y})"

class Pong():
    """Class representing the Pong game state and logic."""
    def __init__(self) -> None:
        self.const: Config = self._load_constants()
        self.init_human_pos: tuple[int, float] = (
            self.const.paddle_offset,
            self.const.game_height / 2
        )
        self.init_agent_pos: tuple[int, float] = (
            self.const.game_height - self.const.paddle_offset - self.const.paddle_width,
            self.const.game_height / 2,
        )
        self.ball: Ball = Ball()
        self.human: Paddle = Paddle(*self.init_human_pos)
        self.agent: Paddle = Paddle(*self.init_agent_pos)
        self.dirvector: np.ndarray
        self.score: dict[str, int] = {"human": 0, "agent": 0}
        self.normal: dict[str, np.ndarray] = {
                "top": np.array([0., 1.]),
                "bottom": np.array([0., -1.]),
                "left": np.array([1., 0.]),
                "right": np.array([-1., 0.]),
            }
        self.game_over: bool = False
        # Get the initial dir vector with:
        self._get_ball_start_position()

    def _load_constants(self) -> Config:
        """Load game constants from the JSON configuration file."""
        with open(CONSTANTS_PATH, "r") as f:
            data = json.load(f)
        return Config(**data)

    def _get_ball_start_position(self) -> None:
        """Initialize the ball with a random y position (sampled from a normal distribution),
        centered x position, and heading towards either paddle."""
        # Compute and set y
        y = np.random.normal(
            loc=self.const.game_height // 2,
            scale=self.const.game_height // 16
        )
        y = int(np.clip(y, 0, self.const.game_height))
        self.ball.y = y
        # Set x always in the middle
        self.ball.x = self.const.game_width // 2
        # Start the ball orthogonally to either left or right paddle
        _ball_heading = 0. if np.random.randint(0, 2) == 1 else 180.
        # Add slight scale within +/- 45 degrees
        _ball_heading = _ball_heading + np.random.uniform(-45., 45.)
        # Avoid perfect vertical angles (perfect reflection edge case)
        if abs(_ball_heading) < 1e-9 or abs(_ball_heading - 180.) < 1e-9:
            _ball_heading = _ball_heading + 10.
        self.dirvector = np.array([
                np.cos(np.radians(_ball_heading)),
                np.sin(np.radians(_ball_heading))
                ])

    def _update_direction_vector(self, normal_dir: str) -> None:
        """
        Assuming perfect reflection, this computes the updated direction vector
        reflected on one of the 4 normals.

        Parameters
        ----------
        normal_dir
            One of "top", "bottom", "left", "right" indicating which normal to reflect on.
        """
        assert normal_dir in self.normal.keys(), (
            "Normal direction must be one of 'top', 'bottom',"
            f" 'left', 'right', not {normal_dir}"
        )
        
        normal = self.normal[normal_dir]
        self.dirvector = self.dirvector - 2*np.dot(self.dirvector, normal)*normal

    def move_paddle(self, human: bool, dir: int) -> None:
        """
        Move the paddle up or down.

        Parameters
        ----------
        human
            If True, move the human paddle. If False, move the agent paddle.
        dir
            Direction to move the paddle. -1 for up, 1 for down.
        """
        assert dir == -1 or dir == 1 or dir == 0, "Up, do nothing, and down are -1, 0, and 1 respectively."
        player = self.human if human else self.agent

        min_y = self.const.paddle_height // 2
        max_y = self.const.game_height - (self.const.paddle_height // 2)

        new_y = player.y + dir*self.const.paddle_velocity
        player.y = int(np.clip(new_y, min_y, max_y))


    def move_ball(self) -> None:
        """
        Move the ball according to its velocity and direction vector.
        Use trigonometry to compute the new position.
        Assumes perfect reflections and no friction.
        """
        def _within_paddle_bound(ball_y: float, paddle_y: float) -> bool:
            """Returns true if ball is within paddle bound (in y-coordinate)"""
            top_half = paddle_y - self.const.paddle_height // 2
            bottom_half = paddle_y + self.const.paddle_height // 2
            return top_half <= ball_y <= bottom_half

        # Logic statements for ball collisions
        hitting_top = self.ball.y <= self.const.ball_size
        hitting_bottom = self.ball.y >= (self.const.game_height - self.const.ball_size)
        hitting_human_paddle = (
            _within_paddle_bound(self.ball.y, self.human.y) and 
            self.ball.x <= self.human.x + self.const.paddle_width + self.const.ball_size
        )
        hitting_agent_paddle = (
            _within_paddle_bound(self.ball.y, self.agent.y) and
            self.ball.x >= self.agent.x - self.const.ball_size
        )
        hitting_paddle = hitting_agent_paddle or hitting_human_paddle

        # Compute new direction vectors for each of 4 cases, only one per frame
        if hitting_agent_paddle:
            self._update_direction_vector("left")
        elif hitting_human_paddle:
            self._update_direction_vector("right")
        elif hitting_top and not hitting_paddle:
            self._update_direction_vector("top")
        elif hitting_bottom and not hitting_paddle:
            self._update_direction_vector("bottom")

        # Handle scoring
        scored_left = self.ball.x <= (
            self.const.paddle_offset + self.const.paddle_width
        ) and not hitting_paddle
        scored_right = self.ball.x >= (
            self.const.game_width - (self.const.paddle_offset + self.const.paddle_width)
        ) and not hitting_paddle
        if scored_left or scored_right:
            logger.info(f"Score update! Agent: {self.score['agent']} | Human: {self.score['human']}")
            # Update scores
            if scored_left:
                self.score["agent"] += 1
                scored_by = "agent"
            else:
                self.score["human"] += 1
                scored_by = "human"

            # Update paddle positions
            self.human.y = self.init_human_pos[1]
            self.agent.y = self.init_agent_pos[1]
            self._get_ball_start_position()

            # Check for game over
            if self.score[scored_by] >= self.const.winning_score:
                self.game_over = True
                logger.info(f"Game Over! {scored_by.capitalize()} wins!")

        # Update position
        self.ball.x += self.const.ball_velocity*self.dirvector[0]
        self.ball.y += self.const.ball_velocity*self.dirvector[1]
