from typing import Dict, Any, Callable
from engine.rules.pawn_rules import get_pawn_destinations
from engine.rules.rook_rules import get_rook_destinations
from engine.rules.bishop_rules import get_bishop_destinations
from engine.rules.queen_rules import get_queen_destinations
from engine.rules.king_rules import get_king_destinations
from engine.rules.knight_rules import get_knight_destinations

# מילון מרכזי שממפה בין מחרוזת של סוג הכלי (piece.kind) לבין הפונקציה המתאימה לו
MOVEMENT_RULES = {
    "pawn": get_pawn_destinations,
    "rook": get_rook_destinations,
    "bishop": get_bishop_destinations,
    "queen": get_queen_destinations,
    "king": get_king_destinations,
    "knight": get_knight_destinations
}