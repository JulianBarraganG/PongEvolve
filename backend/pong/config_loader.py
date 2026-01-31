from pydantic import BaseModel, ConfigDict, Field

class Config(BaseModel):
    """This class represents the configuration settings for the application."""
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True  # Allow both field name and alias
    )
    
    game_width: int = Field(alias="GAME_WIDTH")
    game_height: int = Field(alias="GAME_HEIGHT")
    paddle_height: int = Field(alias="PADDLE_HEIGHT")
    paddle_width: int = Field(alias="PADDLE_WIDTH")
    paddle_offset: int = Field(alias="PADDLE_OFFSET")
    ball_size: int = Field(alias="BALL_SIZE")
    ball_velocity: int = Field(alias="BALL_VELOCITY")
    paddle_velocity: int = Field(alias="PADDLE_VELOCITY")
    winning_score: int = Field(alias="WINNING_SCORE")
