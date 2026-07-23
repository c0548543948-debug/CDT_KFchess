from enum import Enum

class GameEvent(Enum):
    MOVE_MADE = "move_made"
    JUMP_MADE = "jump_made"
    GAME_OVER = "game_over"
    PLAYER_CONNECTED = "player_connected"
    PLAYER_DISCONNECTED = "player_disconnected"