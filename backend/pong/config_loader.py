from pydantic import BaseModel

class Config(BaseModel):
    """This class represents the configuration settings for the application."""
    game_width: int
    game_height: int
    paddle_height: int
    paddle_width: int
    paddle_offset: int
    ball_size: int
    ball_velocity: int
    paddle_velocity: int
    winning_score: int
