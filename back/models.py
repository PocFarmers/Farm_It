from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class GameState(Base):
    __tablename__ = "game_state"

    id = Column(Integer, primary_key=True, index=True)
    current_stage = Column(Integer, default=0)  # 0-49 (50 stages total)
    shovels = Column(Integer, default=10)       # Currency
    water_drops = Column(Integer, default=10)   # Water resource
    score = Column(Integer, default=0)          # Player score

    # Relationship
    parcels = relationship("Parcel", back_populates="game_state", cascade="all, delete-orphan")

class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)
    game_state_id = Column(Integer, ForeignKey("game_state.id"), nullable=False)

    # Location
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    # Zone and type
    zone_id = Column(String, nullable=False)  # cold, arid, tropical, temperate
    parcel_type = Column(String, nullable=False)  # field, forest
    owned = Column(Boolean, default=False)

    # Crop information
    crop_type = Column(String, nullable=True)  # banana, potato, sorghum, None
    crop_stage = Column(String, nullable=True)  # seed, growing, harvest, None
    crop_stage_counter = Column(Integer, default=0)  # stages in current phase (0-3)

    # Improvements
    has_water_reserve = Column(Boolean, default=False)
    has_firebreak = Column(Boolean, default=False)
    is_forest_preserved = Column(Boolean, default=True)  # for forest parcels

    # Relationship
    game_state = relationship("GameState", back_populates="parcels")
