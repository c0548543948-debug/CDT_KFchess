from __future__ import annotations
from engine.model.board import Board
from engine.model.piece import Piece
from engine.model.position import Position


def get_knight_destinations(board: Board, piece: Piece) -> set[Position]:
    """מחזיר את כל המיקומים החוקיים של הפרש (8 קפיצות בצורת L, מתעלם מחסימות בדרך)"""
    destinations = set()
    current_pos = piece.cell

    # הגדרת 8 קפיצות ה-L האפשריות של הפרש: (שינוי בשורה, שינוי בעמודה)
    moves_offsets = [
        (2, 1), (2, -1),   # שניים למעלה, אחד ימינה/שמאלה
        (-2, 1), (-2, -1),  # שניים למטה, אחד ימינה/שמאלה
        (1, 2), (1, -2),   # אחד למעלה, שניים ימינה/שמאלה
        (-1, 2), (-1, -2)  # אחד למטה, שניים ימינה/שמאלה
    ]

    for d_row, d_col in moves_offsets:
        # מחשבים ישירות את משבצת הנחיתה (הפרש מדלג על מה שבדרך!)
        next_pos = Position(row=current_pos.row + d_row, col=current_pos.col + d_col)

        if board.is_in_bounds(next_pos):
            target_piece = board.get_piece_at(next_pos)

            # המהלך חוקי אם המשבצת ריקה או שיש שם אויב (אסור לנחות על חבר)
            if target_piece is None or target_piece.color != piece.color:
                destinations.add(next_pos)

    return destinations