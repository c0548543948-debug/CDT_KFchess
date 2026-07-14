import unittest
from model.position import Position
from model.piece import Piece
from model.motion import Motion
from config import STEP_DURATION_MS


class TestMotion(unittest.TestCase):

    def test_straight_route_calculation(self):
        """בדיקה שצריח שמבצע תנועה ישרה מחשב נכון את מערך הצעדים הסדור"""
        rook = Piece(piece_id="w_rook_1", kind="rook", color="white", cell=Position(0, 0))
        target = Position(3, 0)

        motion = Motion(rook, target)

        # בודקים שהמסלול חושב כמערך סדור (list) עם הצעדים הנכונים
        expected_steps = [
            Position(0, 0),
            Position(1, 0),
            Position(2, 0),
            Position(3, 0)
        ]

        self.assertEqual(motion.steps, expected_steps)
        self.assertEqual(motion.total_steps, 3)
        self.assertEqual(motion.total_duration_ms, 3 * STEP_DURATION_MS)

    def test_diagonal_route_calculation(self):
        """בדיקה שרץ שמבצע תנועה באלכסון מחשב נכון את מערך הצעדים הסדור"""
        bishop = Piece(piece_id="b_bishop_1", kind="bishop", color="black", cell=Position(0, 2))
        target = Position(3, 5)

        motion = Motion(bishop, target)

        expected_steps = [
            Position(0, 2),
            Position(1, 3),
            Position(2, 4),
            Position(3, 5)
        ]

        self.assertEqual(motion.steps, expected_steps)
        self.assertEqual(motion.total_steps, 3)

    def test_knight_route_skips_intermediate_cells(self):
        """בדיקה שפרש מדלג ומכיל במערך הצעדים רק את המקור והיעד"""
        knight = Piece(piece_id="w_knight_1", kind="knight", color="white", cell=Position(0, 1))
        target = Position(2, 2)

        motion = Motion(knight, target)

        expected_steps = [
            Position(0, 1),
            Position(2, 2)
        ]

        self.assertEqual(motion.steps, expected_steps)
        self.assertEqual(motion.total_steps, 1)  # עבור הפרש זו קפיצה אחת ישירה

    def test_advance_time_and_finish(self):
        """בדיקה שקידום הזמן מגדיל את הזמן שחלף ומסיים את התנועה בזמן"""
        pawn = Piece(piece_id="w_pawn_1", kind="pawn", color="white", cell=Position(1, 1))
        target = Position(2, 1)  # מהלך של צעד אחד (1000ms לפי ה-config)

        motion = Motion(pawn, target)

        self.assertFalse(motion.is_finished)
        self.assertEqual(motion.elapsed_time, 0)

        # מתקדמים 400 מילישניות
        motion.advance_time(400)
        self.assertEqual(motion.elapsed_time, 400)
        self.assertFalse(motion.is_finished)

        # משלימים את ה-600 שנותרו
        motion.advance_time(600)
        self.assertEqual(motion.elapsed_time, STEP_DURATION_MS)
        self.assertTrue(motion.is_finished)

    def test_advance_time_does_not_exceed_total_duration(self):
        """בדיקה שהזמן שחלף לעולם לא עוקף את הזמן הכולל המתוכנן של התנועה"""
        pawn = Piece(piece_id="w_pawn_2", kind="pawn", color="white", cell=Position(1, 1))
        target = Position(2, 1)  # מהלך של צעד אחד (STEP_DURATION_MS)

        motion = Motion(pawn, target)

        # נקדם ביותר מהזמן המתוכנן
        motion.advance_time(STEP_DURATION_MS + 200)

        # הזמן שחלף צריך להיעצר בדיוק בזמן הכולל המקסימלי
        self.assertEqual(motion.elapsed_time, STEP_DURATION_MS)
        self.assertTrue(motion.is_finished)

    def test_get_current_physical_position(self):
        """בדיקה שהמיקום הפיזי באוויר מחושב במדויק לפי הזמן שחלף"""
        rook = Piece(piece_id="w_rook_1", kind="rook", color="white", cell=Position(0, 0))
        target = Position(3, 0)  # מסלול: (0,0) -> (1,0) -> (2,0) -> (3,0)

        motion = Motion(rook, target)

        # בהתחלה (elapsed_time = 0): נמצאים במקור
        self.assertEqual(motion.get_current_physical_position(), Position(0, 0))

        # אחרי 1200ms: סיימנו צעד אחד (1000ms) ואנחנו באמצע הצעד השני -> ב-(1, 0)
        motion.advance_time(1200)
        self.assertEqual(motion.get_current_physical_position(), Position(1, 0))

        # אחרי עוד 1000ms (סה"כ 2200ms): נמצאים ב-(2, 0)
        motion.advance_time(1000)
        self.assertEqual(motion.get_current_physical_position(), Position(2, 0))

        # אחרי הגעה לסוף (3000ms ומעלה): נמצאים ביעד (3, 0)
        motion.advance_time(1000)
        self.assertEqual(motion.get_current_physical_position(), Position(3, 0))