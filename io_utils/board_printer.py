from model.position import Position
from model.piece import Piece
from model.board import Board
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