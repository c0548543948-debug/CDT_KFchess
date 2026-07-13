from model.board import Board
from model.piece import Piece
from model.position import Position


def get_pawn_destinations(board: Board, piece: Piece) -> set[Position]:
    """מחזיר את כל המיקומים החוקיים שאליהם הרגלי יכול לצעוד או לאכול"""
    destinations = set()
    current_pos = piece.cell

    # 1. קביעת כיוון הצעדה לפי צבע הכלי
    # לבן עולה למעלה (שורה + 1), שחור יורד למטה (שורה - 1)
    direction = 1 if piece.color == "white" else -1

    # --- תנועה קדימה (צעד אחד) ---
    forward_pos = Position(row=current_pos.row + direction, col=current_pos.col)

    if board.is_in_bounds(forward_pos):
        # רגלי יכול ללכת קדימה אך ורק אם המשבצת ריקה!
        if board.get_piece_at(forward_pos) is None:
            destinations.add(forward_pos)

    # --- אכילה באלכסונים ---
    # רגלי יכול לזוז לאלכסון (ימין או שמאל) אך ורק אם עומד שם כלי של האויב
    diagonal_cols = [current_pos.col - 1, current_pos.col + 1]

    for diag_col in diagonal_cols:
        diag_pos = Position(row=current_pos.row + direction, col=diag_col)

        if board.is_in_bounds(diag_pos):
            target_piece = board.get_piece_at(diag_pos)
            # אם יש שם כלי, והצבע שלו שונה מהצבע שלי (אויב) -> המהלך חוקי לאכילה
            if target_piece is not None and target_piece.color != piece.color:
                destinations.add(diag_pos)

    return destinations