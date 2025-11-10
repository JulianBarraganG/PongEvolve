from const import (
        BALL_SIZE,
        BALL_VELOCITY,
        BUFFER,
        CANVAS_HEIGHT,
        CANVAS_WIDTH,
        PADDLE_HEIGHT,
        PADDLE_VELOCITY,
        PADDLE_WIDTH,
)

import logging
import numpy as np


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)


class Ball:
    def __init__(self) -> None:
        self.x: float
        self.y: float

    def __repr__(self) -> str:
        return f"Ball with pos=({self.x}, {self.y})"

class Paddle:
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

    def __repr__(self) -> str:
        return f"Paddle with pos=({self.x}, {self.y})"

class Pong():
    """Class representing the Pong game state and logic."""
    def __init__(self) -> None:
        self.init_human_pos: tuple[int, int] = (PADDLE_WIDTH, CANVAS_HEIGHT // 2)
        self.init_agent_pos: tuple[int, int] = (CANVAS_WIDTH - BUFFER - PADDLE_WIDTH, CANVAS_HEIGHT // 2)
        self.human: Paddle = Paddle(*self.init_human_pos)
        self.agent: Paddle = Paddle(*self.init_agent_pos)
        self.paddle_speed: int = PADDLE_VELOCITY
        self.ball: Ball = Ball()
        self.ball_speed: int = BALL_VELOCITY
        self.ball_heading: float
        self.dirvector: np.ndarray
        self.score: dict[str, int] = {"human": 0, "agent": 0}
        self.winning_score: int = 3
        self.normal: dict[str, np.ndarray] = {
                "top": np.array([0., 1.]),
                "bottom": np.array([0., -1.]),
                "left": np.array([1., 0.]),
                "right": np.array([-1., 0.]),
            }
        self.game_over: bool = False
        self._get_ball_start_position()

    def _get_ball_start_position(self) -> None:
        """Initialize the ball with a random y position (sampled from a normal distribution),
        centered x position, and heading towards either paddle."""
        # Compute and set y
        y = np.random.normal(loc=CANVAS_HEIGHT // 2, scale=CANVAS_HEIGHT // 16)
        y = int(np.clip(y, 0, CANVAS_HEIGHT))
        self.ball.y = y
        # Set x always in the middle
        self.ball.x = CANVAS_WIDTH // 2
        # Start the ball orthogonally to either left or right paddle
        self.ball_heading = 0. if np.random.randint(0, 2) == 1 else 180.
        # Add slight scale within +/- 45 degrees
        self.ball_heading = self.ball_heading + np.random.uniform(-45., 45.)
        # Avoid perfect vertical angles (perfect reflection edge case)
        if abs(self.ball_heading) < 1e-9 or abs(self.ball_heading - 180.) < 1e-9:
            self.ball_heading = self.ball_heading + 10.
        self.dirvector = np.array([
                np.cos(np.radians(self.ball_heading)),
                np.sin(np.radians(self.ball_heading))
                ])

    def _update_direction_vector(self, normal_dir: str) -> None:
        """
        Assuming perfect reflection, this computes the updated direction vector reflected on one of the 4 normals.
        Parameters
        ----------
        normal_dir : str
            One of "top", "bottom", "left", "right" indicating which normal to reflect on.
        """
        assert normal_dir in self.normal.keys(), "Normal direction must be one of 'top', 'bottom', 'left', 'right'."
        normal = self.normal[normal_dir]
        self.dirvector = self.dirvector - 2*np.dot(self.dirvector, normal)*normal

    def move_paddle(self, human: bool, dir: int) -> None:
        """
        Move the paddle up or down.

        Parameters
        ----------
        human : bool
            If True, move the human paddle. If False, move the agent paddle.
        dir : int
            Direction to move the paddle. -1 for up, 1 for down.

        NOTE
        ----
        I tried to do cool smart logic, but it didn't work. Did bare minimum viable product instead.
        """
        assert dir == -1 or dir == 1, "Up and down should be given by -1 and 1 respectively."
        player = self.human if human else self.agent

        min_y = PADDLE_HEIGHT // 2
        max_y = CANVAS_HEIGHT - (PADDLE_HEIGHT // 2)

        new_y = player.y + dir*self.paddle_speed
        player.y = int(np.clip(new_y, min_y, max_y))


    def move_ball(self) -> None:
        """
        Move the ball according to its velocity and heading.
        Use basic trigonometry to compute the new position.
        Assume perfect reflections and no friction.
        """
        # Handle paddle and wall collisions
        hitting_top = self.ball.y <= BALL_SIZE
        hitting_bottom = self.ball.y >= CANVAS_HEIGHT - BALL_SIZE
        def within_paddle_bound(ball_y: float, paddle_y: float) -> bool:
            top_half = paddle_y - PADDLE_HEIGHT // 2
            bottom_half = paddle_y + PADDLE_HEIGHT // 2
            return top_half <= ball_y <= bottom_half
        hitting_human_paddle = within_paddle_bound(self.ball.y, self.human.y) and \
                            self.ball.x <= self.human.x + PADDLE_WIDTH + BALL_SIZE
        hitting_agent_paddle = within_paddle_bound(self.ball.y, self.agent.y) and \
                            self.ball.x >= self.agent.x - BALL_SIZE
        hitting_paddle = hitting_agent_paddle or hitting_human_paddle

        # Compute new direction vectors for each of 4 cases, only one per frame
        if hitting_human_paddle:
            self._update_direction_vector("left")
        elif hitting_agent_paddle:
            self._update_direction_vector("right")
        elif hitting_top and not hitting_paddle:
            self._update_direction_vector("top")
        elif hitting_bottom and not hitting_paddle:
            self._update_direction_vector("bottom")

        # Handle scoring
        scored_left = self.ball.x <= (BUFFER + PADDLE_WIDTH) and not hitting_paddle
        scored_right = self.ball.x >= CANVAS_WIDTH - (BUFFER + PADDLE_WIDTH) and not hitting_paddle
        if scored_left or scored_right:
            logger.info(f"Score update! Human: {self.score['human']} | Agent: {self.score['agent']}")
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
            if self.score[scored_by] >= self.winning_score:
                self.game_over = True
                logger.info(f"Game Over! {scored_by.capitalize()} wins!")

        # Update position
        self.ball.x += self.ball_speed*self.dirvector[0]
        self.ball.y += self.ball_speed*self.dirvector[1]
