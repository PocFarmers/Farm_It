"""
Custom exceptions for game logic.
These exceptions are caught by routers and converted to appropriate HTTP responses.
"""


class GameException(Exception):
    """Base exception for all game-related errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InsufficientResourcesError(GameException):
    """Raised when player doesn't have enough resources for an action"""
    pass


class TileNotOwnedError(GameException):
    """Raised when trying to perform action on non-owned tile"""
    pass


class TileAlreadyOwnedError(GameException):
    """Raised when trying to buy a tile that's already owned"""
    pass


class InvalidTileStateError(GameException):
    """Raised when tile is in wrong state for requested action"""
    pass


class TileNotFoundError(GameException):
    """Raised when tile ID doesn't exist"""
    pass


class GameNotInitializedError(GameException):
    """Raised when trying to access game that hasn't been initialized"""
    pass


class InvalidActionError(GameException):
    """Raised when action is invalid or not allowed"""
    pass
