import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board


class TestBoard(unittest.TestCase):

    def setUp(self):
        """פונקציה שרצה אוטומטית לפני כל טסט ומכינה לנו לוח נקי וכלי בדיקה"""
        self.board = Board(width=8, height=8)
        self.pos_0_0 = Position(row=0, col=0)
        self.pos_1_2 = Position(row=1, col=2)

        # יצירת כלים לבדיקה עם מזהים ייחודיים
        self.white_pawn = Piece(piece_id="w_pawn_1", color="white", kind="pawn", cell=self.pos_0_0)
        self.black_king = Piece(piece_id="b_king_1", color="black", kind="king", cell=self.pos_1_2)

    # 1. board dimensions are inferred correctly
    def test_board_dimensions_are_inferred_correctly(self):
        self.assertEqual(self.board.width, 8)
        self.assertEqual(self.board.height, 8)

        # בדיקה שפונקציית הגבולות מזהה נכון מה בפנים ומה בחוץ
        self.assertTrue(self.board.is_in_bounds(Position(row=0, col=0)))
        self.assertTrue(self.board.is_in_bounds(Position(row=7, col=7)))
        self.assertFalse(self.board.is_in_bounds(Position(row=8, col=8)))
        self.assertFalse(self.board.is_in_bounds(Position(row=-1, col=0)))

    # 2. empty cells return no piece
    def test_empty_cells_return_no_piece(self):
        # תשאול של משבצת ריקה לחלוטין צריך להחזיר None
        piece = self.board.get_piece_at(self.pos_1_2)
        self.assertIsNone(piece)

    # 3. occupied cells return the correct piece
    def test_occupied_cells_return_the_correct_piece(self):
        # הוספת כלי ואימות שהוא אכן חוזר בתשאול
        self.board.add_piece(self.white_pawn)

        retrieved_piece = self.board.get_piece_at(self.pos_0_0)
        self.assertEqual(retrieved_piece, self.white_pawn)

    # 4. adding two pieces to the same cell fails
    def test_adding_two_pieces_to_the_same_cell_fails(self):
        self.board.add_piece(self.white_pawn)

        # יצירת כלי נוסף שמנסה להתיישב באותה משבצת (0, 0)
        another_piece = Piece(piece_id="w_rook_1", color="white", kind="rook", cell=self.pos_0_0)

        # אנחנו מצפים שהוספת הכלי השני תזרוק ValueError
        with self.assertRaises(ValueError):
            self.board.add_piece(another_piece)

    # 5. moving a piece updates source and destination
    def test_moving_a_piece_updates_source_and_destination(self):
        self.board.add_piece(self.white_pawn)  # נמצא ב-(0,0)

        # הזזה מ-(0,0) ל-(1,2)
        self.board.move_piece(source=self.pos_0_0, destination=self.pos_1_2)

        # א. בדיקה שמשבצת המקור התרוקנה
        self.assertIsNone(self.board.get_piece_at(self.pos_0_0))
        # ב. בדיקה שמשבצת היעד מכילה את הכלי הנכון
        self.assertEqual(self.board.get_piece_at(self.pos_1_2), self.white_pawn)
        # ג. בדיקה שהשדה הפנימי של הכלי עצמו עודכן למיקום החדש
        self.assertEqual(self.white_pawn.cell, self.pos_1_2)

    # 6. removing a captured piece clears its cell
    def test_removing_a_captured_piece_clears_its_cell(self):
        self.board.add_piece(self.white_pawn)

        # הסרת הכלי מהלוח
        removed_piece = self.board.remove_piece_at(self.pos_0_0)

        # א. בדיקה שהפונקציה החזירה את הכלי הנכון שהוסר
        self.assertEqual(removed_piece, self.white_pawn)
        # ב. בדיקה שהמשבצת בלוח אכן חזרה להיות ריקה (None)
        self.assertIsNone(self.board.get_piece_at(self.pos_0_0))


if __name__ == '__main__':
    unittest.main()