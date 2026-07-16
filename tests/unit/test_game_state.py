import unittest
from model.board import Board
from model.position import Position
from model.piece import Piece
from model.game_state import GameState


class TestGameState(unittest.TestCase):

    def setUp(self):
        """הכנת לוח, כלים ומצב משחק נקיים לפני כל טסט"""
        self.board = Board(width=8, height=8)

        # נוסיף שני כלים ללוח המקור
        self.white_pawn = Piece("w_pawn_1", color="white", kind="pawn", cell=Position(1, 3))
        self.black_knight = Piece("b_knight_1", color="black", kind="knight", cell=Position(7, 1))

        # נגדיר להם ידנית זמני צינון שונים
        self.white_pawn.cooldown_remaining = 1500
        self.black_knight.cooldown_remaining = 3000

        self.board.add_piece(self.white_pawn)
        self.board.add_piece(self.black_knight)

        # ניצור את ה-GameState המרכזי
        self.state = GameState(self.board)

    def test_clone_creates_different_objects(self):
        """בדיקה שהשכפול מייצר אובייקטים חדשים בזיכרון ולא מצביע למקור"""
        cloned_state = self.state.clone()

        # ה-GameState המשוכפל חייב להיות אובייקט שונה
        self.assertIsNot(self.state, cloned_state)

        # הלוח המשוכפל חייב להיות אובייקט שונה
        self.assertIsNot(self.state.board, cloned_state.board)

    def test_clone_copies_primitive_attributes(self):
        """בדיקה שהמשתנים הפשוטים מועתקים במדויק לקлон"""
        self.state.game_over = True
        self.state.winner = "white"

        cloned_state = self.state.clone()

        self.assertTrue(cloned_state.game_over)
        self.assertEqual(cloned_state.winner, "white")

    def test_clone_deep_copies_pieces_and_retains_cooldown(self):
        """בדיקה שהכלים משוכפלים בצורה עמוקה ושומרים על זמני הצינון שלהם"""
        cloned_state = self.state.clone()

        # נשלוף את הכלים מהלוח המשוכפל
        cloned_pawn = cloned_state.board.get_piece_at(Position(1, 3))
        cloned_knight = cloned_state.board.get_piece_at(Position(7, 1))

        # 1. מוודאים שהכלים קיימים בלוח המשוכפל
        self.assertIsNotNone(cloned_pawn)
        self.assertIsNotNone(cloned_knight)

        # 2. מוודאים שהם אובייקטים שונים פיזית בזיכרון (לא אותם רפרנסים)
        self.assertIsNot(self.white_pawn, cloned_pawn)
        self.assertIsNot(self.black_knight, cloned_knight)

        # 3. מוודאים שנתוני הצינון הועתקו במדויק
        self.assertEqual(cloned_pawn.cooldown_remaining, 1500)
        self.assertEqual(cloned_knight.cooldown_remaining, 3000)

    def test_mutation_on_original_does_not_affect_clone(self):
        """בדיקה ששינוי המצב המקורי או הכלים המקוריים לא משפיע על השכפול הקפוא"""
        cloned_state = self.state.clone()

        # נשנה את המצב והכלים המקוריים