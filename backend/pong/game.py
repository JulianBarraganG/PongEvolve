from const import (
        BALL_SIZE,
        BUFFER,
        CANVAS_HEIGHT,
        CANVAS_WIDTH,
        PADDLE_HEIGHT,
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
        self.heading: float # direction in degrees
        self.speed: float = 7.0

    def __repr__(self) -> str:
        return f"Ball with pos=({self.x}, {self.y}), velocity={self.speed} and heading={self.heading}"

class Paddle:
    def __init__(self, x: int, y: int, vel: int = 5) -> None:
        self.x: int = x
        self.y: int = y
        self.vel: int = vel 

    def __repr__(self) -> str:
        return f"Paddle with pos=({self.x}, {self.y}) and velocity={self.vel}"

class Pong():
    def __init__(self) -> None:
        self.human: Paddle = Paddle(PADDLE_WIDTH, (CANVAS_HEIGHT // 2))
        self.agent: Paddle = Paddle(CANVAS_WIDTH - BUFFER + PADDLE_WIDTH, (CANVAS_HEIGHT // 2))
        self.ball: Ball = Ball()
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
        self.ball.heading = 0. if np.random.randint(0, 2) == 1 else 180.
        # Add slight scale withing +/- 45 degrees
        self.ball.heading = self.ball.heading + np.random.uniform(-45., 45.)
        # TEMPORARY
        self.ball.heading = 80.
        self.dirvector = np.array([
                np.cos(self.ball.heading*self.ball.x),
                np.sin(self.ball.heading*self.ball.y)
                ])

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
        if human and dir == 1: # Try to move human paddle down
            if self.human.y + PADDLE_HEIGHT < CANVAS_HEIGHT:
                new_pos = self.human.y + dir*self.human.vel
                if new_pos + PADDLE_HEIGHT > CANVAS_HEIGHT:
                    self.human.y = CANVAS_HEIGHT - PADDLE_HEIGHT
                else:
                    self.human.y = new_pos
        elif human and dir == -1: # Try to move human paddle up
            if self.human.y - PADDLE_HEIGHT > 0:
                new_pos = self.human.y + dir*self.human.vel
                if new_pos - PADDLE_HEIGHT < 0: 
                    self.human.y = PADDLE_HEIGHT
                else:   
                    self.human.y = new_pos
        elif not human and dir == 1: # Try to move agent paddle down
            if self.agent.y + PADDLE_HEIGHT < CANVAS_HEIGHT:
                new_pos = self.agent.y + dir*self.agent.vel
                if new_pos + PADDLE_HEIGHT > CANVAS_HEIGHT:
                    self.agent.y = CANVAS_HEIGHT - PADDLE_HEIGHT
                else:
                    self.agent.y = new_pos
        elif not human and dir == -1: # Try to move agent paddle up
            if self.agent.y - PADDLE_HEIGHT > 0:
                new_pos = self.agent.y + dir*self.agent.vel
                if new_pos - PADDLE_HEIGHT < 0: 
                    self.agent.y = PADDLE_HEIGHT
                else:   
                    self.agent.y = new_pos

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
                            self.ball.x >= self.agent.x - BALL_SIZE # y is leftmost on agent paddle
        hitting_paddle = hitting_agent_paddle or hitting_human_paddle
        # Compute new direction vectors for each of 4 cases
        if hitting_top and not hitting_paddle:
            print("top hit!")
            self.dirvector = 2*np.dot(-self.dirvector, self.normal["top"]) + self.dirvector
        if hitting_bottom and not hitting_paddle:
            print("bottom hit!")
            # TODO: Fix buttom hit reflection, potentially others
            self.dirvector = 2*np.dot(-self.dirvector, self.normal["bottom"]) + self.dirvector
        if hitting_human_paddle:
            print("human paddle hit!")
            self.dirvector = 2*np.dot(-self.dirvector, self.normal["left"]) + self.dirvector
        if hitting_agent_paddle:
            print("agent paddle hit!")
            self.dirvector = 2*np.dot(-self.dirvector, self.normal["right"]) + self.dirvector
        # Handle scoring
        if self.ball.x >= CANVAS_WIDTH - (BUFFER + PADDLE_WIDTH) and not hitting_paddle: # human point
            self.score["human"] += 1
            print(f"Score update! Human: {self.score['human']} | Agent: {self.score['agent']}")
            if self.score["human"] >= self.winning_score:
                self.game_over = True
            self._get_ball_start_position()
        elif self.ball.x <= (BUFFER + PADDLE_WIDTH) and not hitting_paddle:
            self.score["agent"] += 1
            print(f"Score update! Human: {self.score['human']} | Agent: {self.score['agent']}")
            if self.score["agent"] >= self.winning_score:
                self.game_over = True
            self._get_ball_start_position()
        # Update position
        self.ball.x += self.ball.speed*self.dirvector[0]
        self.ball.y += self.ball.speed*self.dirvector[1]


if __name__ == "__main__":
    game = Pong()
    while not game.game_over:
        print(f"Ball currently at position ({game.ball.x}, {game.ball.y})")
        game.move_ball()
