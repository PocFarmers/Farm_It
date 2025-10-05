from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GameState(Base):
    """Singleton table for game state"""
    __tablename__ = "game_state"

    id = Column(Integer, primary_key=True, default=1)
    current_step = Column(Integer, default=0)
    max_steps = Column(Integer, default=10)
    is_game_over = Column(Boolean, default=False)

    def __repr__(self):
        return f"<GameState(step={self.current_step}, max_steps={self.max_steps}, game_over={self.is_game_over})>"


class Player(Base):
    """Player resources and state"""
    __tablename__ = "player"

    id = Column(Integer, primary_key=True, default=1)
    shovels = Column(Integer, default=3)
    drops = Column(Integer, default=3)
    score = Column(Integer, default=0)

    def __repr__(self):
        return f"<Player(shovels={self.shovels}, drops={self.drops}, score={self.score})>"


class Tile(Base):
    """Individual tile state"""
    __tablename__ = "tiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    grid_i = Column(Integer, nullable=False)
    grid_j = Column(Integer, nullable=False)
    zone_id = Column(Integer, nullable=False)
    type = Column(String, default="empty")
    owner = Column(String, nullable=True)
    tile_state = Column(String, nullable=True)
    has_water_reserve = Column(Boolean, default=False)
    has_firebreak = Column(Boolean, default=False)
    temperature = Column(Float, default=0.0)
    humidity = Column(Float, default=0.0)
    last_irrigated_step = Column(Integer, default=-1)
    irrigated_this_step = Column(Boolean, default=False)
    exploited = Column(String, default="conserve")

    def __repr__(self):
        return f"<Tile(id={self.id}, pos=({self.grid_i},{self.grid_j}), type={self.type}, owner={self.owner})>"
