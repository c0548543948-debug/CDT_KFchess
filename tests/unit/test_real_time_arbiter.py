import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board
from real_time.real_time_arbiter import RealTimeArbiter
from config import STEP_DURATION_MS


class TestRealTimeArbiter(unittest.TestCase):

    def setUp(self):
        """הכנת לוח וארביטר נקיים לפני כל טסט"""
        self.board = Board(width=8, height=8)
        self.arbiter = RealTimeArbiter()

    def test_is_route_active_only_blocks_if_piece_is_already_moving(self):
        """בדיקה שאין יותר חסימת מסלולים מראש, אלא רק מניעת פקודה כפולה לאותו כלי"""
        rook = Piece("w_rook_1", kind="rook", color="white", cell=Position(0, 0))
        self.board.add_piece(rook)

        # מתחילים תנועה לצריח הלבן
        self.arbiter.start_motion(self.board, Position(0, 0), Position(4, 0))

        # בדיקה 1: הצריח עצמו חסום לפקודה חדשה (כי הוא כבר זז)
        self.assertTrue(self.arbiter.is_route_active(self.board, Position(0, 0), Position(1, 0)))

        # בדיקה 2: כלי אחר (למשל רץ שחור) שרוצה לחצות את המסלול שלו - לא נחסם מראש!
        bishop = Piece("b_bishop_1", kind="bishop", color="black", cell=Position(0, 2))
        self.board.add_piece(bishop)

        # בלוגיקה החדשה, המעבר דרך (2,0) מאושר להתחלה וההתנגשות תיפתר באוויר במידת הצורך
        self.assertFalse(self.arbiter.is_route_active(self.board, Position(0, 2), Position(2, 0)))

    def test_friend_collision_causes_last_initiator_to_block_early(self):
        """
        בדיקה שהתנגשות חברים (אותו צבע) גורמת לכלי שיזם אחרון (הגיע מאוחר יותר)
        להיבלם ולהיעצר משבצת אחת לפני נקודת המפגש.
        """
        # 1. מלכה לבנה מתחילה לזוז מ-(4, 0) ל-(4, 7) [מהלך אופקי]
        queen = Piece("w_queen_1", kind="queen", color="white", cell=Position(4, 0))
        self.board.add_piece(queen)
        self.arbiter.start_motion(self.board, Position(4, 0), Position(4, 7))

        # נקדם את הזמן ב-1500ms: המלכה עברה את (4,0) ו-(4,1) ונמצאת כרגע ב-(4,1) בדרך ל-(4,2)
        self.arbiter.advance_time(1500, self.board)

        # 2. כעת צריח לבן ב-(0, 4) מתחיל לזוז ל-(7, 4) [מהלך אנכי, נפגשים ב-(4, 4)]
        # הצריח הוא "היוזם האחרון" (התחיל מאוחר יותר, ה-elapsed_time שלו קטן יותר)
        rook = Piece("w_rook_2", kind="rook", color="white", cell=Position(0, 4))
        self.board.add_piece(rook)
        self.arbiter.start_motion(self.board, Position(0, 4), Position(7, 4))

        # נריץ את שארית הסימולציה קדימה
        self.arbiter.advance_time(6000, self.board)

        # המלכה שהגיעה קודם הייתה צריכה להמשיך בדרכה ליעד הסופי (4, 7) באין מפריע
        self.assertEqual(len(self.arbiter._active_motions), 0)

        landed_queen = self.board.get_piece_at(Position(4, 7))
        self.assertIsNotNone(landed_queen)
        self.assertEqual(landed_queen, queen)

        # הצריח (היוזם האחרון) היה צריך לזהות את המלכה ב-(4,4), להיבלם ולהיעצר ב-(3,4)
        landed_rook = self.board.get_piece_at(Position(3, 4))
        self.assertIsNotNone(landed_rook)
        self.assertEqual(landed_rook, rook)

    def test_enemy_collision_causes_last_initiator_to_capture(self):
        """
        בדיקה שהתנגשות אויבים (צבעים שונים) גורמת לכלי שיזם אחרון (הגיע מאוחר יותר)
        לאכול את הכלי שהגיע קודם, ולהיעצר במשבצת שלו.
        """
        # 1. רץ שחור (אויב) מתחיל לזוז מ-(0, 0) ל-(4, 4)
        enemy_bishop = Piece("b_bishop_1", kind="bishop", color="black", cell=Position(0, 0))
        self.board.add_piece(enemy_bishop)
        self.arbiter.start_motion(self.board, Position(0, 0), Position(4, 4))

        # 2. צריח לבן ב-(2, 0) מתחיל לזוז ל-(2, 4) באותו הזמן בדיוק!
        # שניהם ייפגשו ב-(2, 2) כעבור 2000ms.
        # הצריח הלבן שוגר אחרון ולכן הוא היוזם האחרון (והוא הטורף)
        player_rook = Piece("w_rook_1", kind="rook", color="white", cell=Position(2, 0))
        self.board.add_piece(player_rook)
        self.arbiter.start_motion(self.board, Position(2, 0), Position(2, 4))

        # מריצים את המשחק קדימה עד לסיום התנועות (5000ms)
        self.arbiter.advance_time(5000, self.board)

        # הצריח הלבן (היוזם האחרון) היה צריך לאכול את הרץ השחור ב-(2, 2) ולהיעצר שם
        landed_rook = self.board.get_piece_at(Position(2, 2))
        self.assertIsNotNone(landed_rook)
        self.assertEqual(landed_rook, player_rook)

        # הרץ השחור (הנאכל) צריך להיעלם לחלוטין מהלוח ומהארביטר
        self.assertEqual(len(self.arbiter._active_motions), 0)

        # מוודאים ששאר המסלול המקורי של הצריח ב-(2,4) נשאר ריק
        self.assertIsNone(self.board.get_piece_at(Position(2, 4)))

    def test_static_enemy_collision_causes_capture(self):
        """בדיקה שכלי בתנועה אוכל כלי אויב שעומד סטטי לחלוטין על הלוח"""
        # אויב עומד סטטי ב-(2, 2)
        static_enemy = Piece("b_bishop_2", kind="bishop", color="black", cell=Position(2, 2))
        self.board.add_piece(static_enemy)

        # צריח לבן מתחיל לזוז מ-(2, 0) ל-(2, 4)
        moving_rook = Piece("w_rook_3", kind="rook", color="white", cell=Position(2, 0))
        self.board.add_piece(moving_rook)
        self.arbiter.start_motion(self.board, Position(2, 0), Position(2, 4))

        # מריצים את הזמן קדימה
        self.arbiter.advance_time(4000, self.board)

        # הצריח היה צריך לאכול את האויב ב-(2,2) ולהיעצר שם
        self.assertIsNone(self.board.get_piece_at(Position(2, 0)))
        landed_rook = self.board.get_piece_at(Position(2, 2))
        self.assertIsNotNone(landed_rook)
        self.assertEqual(landed_rook, moving_rook)

