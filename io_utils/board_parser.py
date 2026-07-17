# io_utils.py
from model.position import Position
from model.piece import Piece
from model.board import Board

# הגדרת תווים חוקיים בשחמט (צבע + סוג כלי)
VALID_COLORS = {'w', 'b'}
VALID_KINDS = {'K', 'Q', 'R', 'B', 'N', 'P'}


class BoardParser:
    @staticmethod
    def parse(board_str: str) -> Board:
        lines = [line.strip() for line in board_str.strip().split('\n') if line.strip()]
        if not lines:
            raise ValueError("Empty board")

        first_row_tokens = lines[0].split()
        expected_width = len(first_row_tokens)
        height = len(lines)

        board = Board(width=expected_width, height=height)

        for r_idx, line in enumerate(lines):
            tokens = line.split()
            if len(tokens) != expected_width:
                raise ValueError("ROW_WIDTH_MISMATCH")

            for c_idx, token in enumerate(tokens):
                if token == '.':
                    continue

                # בדיקת תקינות הטוקן (למשל: wK)
                if len(token) != 2 or token[0] not in VALID_COLORS or token[1] not in VALID_KINDS:
                    raise ValueError("UNKNOWN_TOKEN")

                # מיפוי סוגי הכלים למילים מלאות כפי שמוגדר בפרויקט שלך
                kind_map = {
                    'K': 'king', 'Q': 'queen', 'R': 'rook',
                    'B': 'bishop', 'N': 'knight', 'P': 'pawn'
                }
                color_map = {'w': 'white', 'b': 'black'}

                piece = Piece(
                    piece_id=f"{token}_{r_idx}_{c_idx}",
                    color=color_map[token[0]],
                    kind=kind_map[token[1]],
                    cell=Position(row=r_idx, col=c_idx)
                )
                board.add_piece(piece)

        return board


class BoardPrinter:
    @staticmethod
    def print_board(board: Board) -> str:
        lines = []
        # מיפוי חזרה לתווים הקצרים של המודל
        kind_map_rev = {
            'king': 'K', 'queen': 'Q', 'rook': 'R',
            'bishop': 'B', 'knight': 'N', 'pawn': 'P'
        }
        color_map_rev = {'white': 'w', 'black': 'b'}

        for r in range(board.height):
            row_tokens = []
            for c in range(board.width):
                piece = board.get_piece_at(Position(r, c))
                if piece:
                    token = color_map_rev[piece.color] + kind_map_rev[piece.kind]
                    row_tokens.append(token)
                else:
                    row_tokens.append('.')
            lines.append(" ".join(row_tokens))
        return "\n".join(lines)