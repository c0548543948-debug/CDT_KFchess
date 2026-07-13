import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board
from rules.knight_rules import get_knight_destinations


# 2. הוסיפי את המחלקה הזו בסוף הקובץ:
class TestKnightRules(unittest.TestCase):

    def setUp(self):
        self.board = Board(width=8, height=8)

    def test_knight_moves_in_l_shapes(self):
        """בדיקה שפרש במרכז לוח ריק מקבל בדיוק את 8 משבצות ה-L שלו"""
        knight = Piece(piece_id="w_knight_1", color="white", kind="knight", cell=Position(row=3, col=3))
        self.board.add_piece(knight)

        moves = get_knight_destinations(self.board, knight)

        # פרש במרכז שולט על 8 משבצות
        self.assertEqual(len(moves), 8)
        # ודא משבצות נחיתה ספציפיות
        self.assertIn(Position(row=5, col=4), moves)  # 2 למעלה, 1 ימינה
        self.assertIn(Position(row=4, col=5), moves)  # 1 למעלה, 2 ימינה

    def test_knight_jumps_over_pieces_but_blocked_at_destination(self):
        """בדיקה שהפרש מדלג בהצלחה על כלים בדרך, אך נחסם אם חבר עומד במשבצת הנחיתה"""
        knight = Piece(piece_id="w_knight_1", color="white", kind="knight", cell=Position(row=3, col=3))

        # כלים שעומדים ממש ליד הפרש (הוא אמור להתעלם מהם ולדלג מעליהם בהצלחה)
        obstacle1 = Piece(piece_id="w_pawn_1", color="white", kind="pawn", cell=Position(row=4, col=3))
        obstacle2 = Piece(piece_id="b_pawn_1", color="black", kind="pawn", cell=Position(row=5, col=3))

        # כלי חבר שעומד בדיוק במשבצת נחיתה (חוסם את הנחיתה!)
        friend_at_dest = Piece(piece_id="w_pawn_2", color="white", kind="pawn", cell=Position(row=5, col=4))

        self.board.add_piece(knight)
        self.board.add_piece(obstacle1)
        self.board.add_piece(obstacle2)
        self.board.add_piece(friend_at_dest)

        moves = get_knight_destinations(self.board, knight)

        # ודא שהמשבצת של החבר (5,4) חסומה
        self.assertNotIn(Position(row=5, col=4), moves)
        # ודא שמשבצת נחיתה אחרת (למשל 5,2 - שניים למעלה, אחד שמאלה) עדיין זמינה, למרות הכלים בדרך
        self.assertIn(Position(row=5, col=2), moves)