import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board
from rules.pawn_rules import get_pawn_destinations


class TestPawnRules(unittest.TestCase):

    def setUp(self):
        self.board = Board(width=8, height=8)

    def test_pawn_moves_forward_when_empty(self):
        """בדיקה שרגלי לבן זז שורה אחת קדימה כשהדרך פנויה"""
        pawn = Piece(piece_id="w_pawn_1", color="white", kind="pawn", cell=Position(row=1, col=3))
        self.board.add_piece(pawn)

        moves = get_pawn_destinations(self.board, pawn)

        # צפוי לזוז רק ל-(2, 3)
        self.assertEqual(moves, {Position(row=2, col=3)})

    def test_pawn_is_blocked_by_any_piece(self):
        """בדיקה שרגלי חסום לחלוטין אם יש כלי ישירות מולו"""
        pawn = Piece(piece_id="w_pawn_1", color="white", kind="pawn", cell=Position(row=1, col=3))
        blocking_piece = Piece(piece_id="b_rook_1", color="black", kind="rook", cell=Position(row=2, col=3))

        self.board.add_piece(pawn)
        self.board.add_piece(blocking_piece)

        moves = get_pawn_destinations(self.board, pawn)

        # הדרך חסומה, לא אמורים להיות מהלכים בכלל
        self.assertEqual(moves, set())

    def test_pawn_can_capture_enemies_diagonally(self):
        """בדיקה שרגלי יכול לאכול אויבים שנמצאים באלכסון קדימה"""
        pawn = Piece(piece_id="w_pawn_1", color="white", kind="pawn", cell=Position(row=1, col=3))
        enemy = Piece(piece_id="b_pawn_1", color="black", kind="pawn", cell=Position(row=2, col=4))
        friend = Piece(piece_id="w_pawn_2", color="white", kind="pawn", cell=Position(row=2, col=2))

        self.board.add_piece(pawn)
        self.board.add_piece(enemy)  # אויב באלכסון ימין - מותר לאכול
        self.board.add_piece(friend)  # חבר באלכסון שמאל - אסור לאכול

        moves = get_pawn_destinations(self.board, pawn)

        # אמור להיות מסוגל ללכת קדימה (2,3) או לאכול באלכסון ימין (2,4)
        expected_moves = {Position(row=2, col=3), Position(row=2, col=4)}
        self.assertEqual(moves, expected_moves)


if __name__ == '__main__':
    unittest.main()