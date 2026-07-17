from __future__ import annotations

from model.board import Board
from model.piece import Piece
from model.position import Position
from typing import Set


def get_pawn_destinations(board: Board, piece: Piece) -> Set[Position]:
    """מחזיר את כל המיקומים החוקיים שאליהם הרגלי יכול לצעוד או לאכול, כולל צעד כפול מהתחלה"""
    destinations = set()
    current_pos = piece.cell

    # 1. קביעת כיוון הצעדה לפי צבע הכלי
    # לבן עולה למעלה (מפחית שורה), שחור יורד למטה (מוסיף שורה)
    direction = -1 if piece.color == "white" else 1

    # --- תנועה קדימה (צעד אחד) ---
    forward_pos = Position(row=current_pos.row + direction, col=current_pos.col)
    forward_clear = False

    if board.is_in_bounds(forward_pos):
        # רגלי יכול ללכת קדימה אך ורק אם המשבצת ריקה!
        if board.get_piece_at(forward_pos) is None:
            destinations.add(forward_pos)
            forward_clear = True

    # --- תנועה כפולה קדימה מהשורה הראשונית (Double Step) ---
    # לבן מתחיל בשורה ה-2 מלמטה (board.height - 2), שחור מתחיל בשורה ה-2 מלמעלה (אינדקס 1)
    is_at_start = (
        (piece.color == "white" and current_pos.row == board.height - 2) or
        (piece.color == "black" and current_pos.row == 1)
    )

    if is_at_start and forward_clear:
        double_forward_pos = Position(row=current_pos.row + (direction * 2), col=current_pos.col)
        if board.is_in_bounds(double_forward_pos):
            if board.get_piece_at(double_forward_pos) is None:
                destinations.add(double_forward_pos)

    # --- אכילה באלכסונים ---
    diagonal_cols = [current_pos.col - 1, current_pos.col + 1]

    for diag_col in diagonal_cols:
        diag_pos = Position(row=current_pos.row + direction, col=diag_col)

        if board.is_in_bounds(diag_pos):
            target_piece = board.get_piece_at(diag_pos)
            # אם יש שם כלי, והצבע שלו שונה מהצבע שלי (אויב) -> המהלך חוקי לאכילה
            if target_piece is not None and target_piece.color != piece.color:
                destinations.add(diag_pos)

    return destinations