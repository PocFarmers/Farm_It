from typing import List, Tuple
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.models import Tile


def get_neighbors(grid_i: int, grid_j: int, ny: int, nx: int) -> List[Tuple[int, int]]:
    """
    Get 8-neighbor coordinates with boundary checking.

    Args:
        grid_i: Row index of center tile
        grid_j: Column index of center tile
        ny: Total number of rows
        nx: Total number of columns

    Returns:
        List of (i, j) tuples for valid neighbors
    """
    # 8-direction offsets: N, NE, E, SE, S, SW, W, NW
    offsets = [
        (-1, -1), (-1, 0), (-1, 1),  # Top row
        (0, -1),           (0, 1),    # Middle row (left, right)
        (1, -1),  (1, 0),  (1, 1)     # Bottom row
    ]

    neighbors = []
    for di, dj in offsets:
        ni, nj = grid_i + di, grid_j + dj
        # Check boundaries
        if 0 <= ni < ny and 0 <= nj < nx:
            neighbors.append((ni, nj))

    return neighbors


def get_adjacent_tiles(tile: Tile, db: Session) -> List[Tile]:
    """
    Get all adjacent tiles from database for a given tile.

    Args:
        tile: The center tile
        db: Database session

    Returns:
        List of adjacent Tile objects
    """
    # Get grid dimensions from database
    max_i_result = db.query(Tile.grid_i).order_by(Tile.grid_i.desc()).first()
    max_j_result = db.query(Tile.grid_j).order_by(Tile.grid_j.desc()).first()

    if not max_i_result or not max_j_result:
        return []

    ny = max_i_result[0] + 1
    nx = max_j_result[0] + 1

    # Get neighbor coordinates
    neighbor_coords = get_neighbors(tile.grid_i, tile.grid_j, ny, nx)

    # Query adjacent tiles
    adjacent_tiles = []
    for ni, nj in neighbor_coords:
        neighbor = db.query(Tile).filter(
            Tile.grid_i == ni,
            Tile.grid_j == nj
        ).first()
        if neighbor:
            adjacent_tiles.append(neighbor)

    return adjacent_tiles


def count_adjacent_conserved_forests(tile: Tile, db: Session) -> int:
    """
    Count adjacent tiles that are conserved forests.

    Args:
        tile: The center tile
        db: Database session

    Returns:
        Number of adjacent conserved forests
    """
    adjacent_tiles = get_adjacent_tiles(tile, db)
    count = sum(
        1 for t in adjacent_tiles
        if t.type == "forest" and t.exploited == "conserve"
    )
    return count


def has_adjacent_water_reserve(tile: Tile, db: Session) -> bool:
    """
    Check if any adjacent tile has a water reserve.

    Args:
        tile: The center tile
        db: Database session

    Returns:
        True if at least one adjacent tile has a water reserve
    """
    adjacent_tiles = get_adjacent_tiles(tile, db)
    return any(t.has_water_reserve for t in adjacent_tiles)


def get_tiles_adjacent_to_water_reserves(db: Session) -> List[Tile]:
    """
    Get all tiles that are adjacent to water reserves.
    Useful for auto-irrigation logic.

    Args:
        db: Database session

    Returns:
        List of tiles adjacent to water reserves
    """
    # Find all tiles with water reserves
    water_reserve_tiles = db.query(Tile).filter(Tile.has_water_reserve == True).all()

    # Collect all adjacent tiles
    adjacent_tiles_set = set()
    for wr_tile in water_reserve_tiles:
        adjacent = get_adjacent_tiles(wr_tile, db)
        for tile in adjacent:
            adjacent_tiles_set.add(tile.id)

    # Query and return all adjacent tiles
    if adjacent_tiles_set:
        return db.query(Tile).filter(Tile.id.in_(adjacent_tiles_set)).all()
    return []
