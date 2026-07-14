from model.position import Position
from model.board import Board
from model.motion import Motion


class RealTimeArbiter:
    def __init__(self):
        # אוסף התנועות הפעילות כרגע במשחק (מחוץ ללוח)
        self._active_motions: list[Motion] = []

    def is_piece_moving(self, piece) -> bool:
        """בודק האם כלי מסוים נמצא כרגע באמצע הליכה"""
        return any(m.piece == piece and not m.is_finished for m in self._active_motions)

    def is_route_active(self, board: Board, source: Position, target: Position) -> bool:
        """
        בלוגיקה החדשה: אין חסימת מסלולים מראש!
        הבדיקה היחידה היא האם הכלי שרוצה לזוז כבר נמצא באמצע תנועה אחרת.
        """
        actual_piece = board.get_piece_at(source)
        if not actual_piece:
            return False

        # מניעת פקודה כפולה לאותו כלי בלבד
        return self.is_piece_moving(actual_piece)

    def start_motion(self, board: Board, source: Position, target: Position) -> None:
        """רושמת תנועה חדשה בארביטר. הלוח הלוגי לא משתנה עד לרגע ההגעה!"""
        piece = board.get_piece_at(source)
        if not piece:
            return

        # יצירת אובייקט התנועה והוספתו לארביטר
        new_motion = Motion(piece, target)
        self._active_motions.append(new_motion)

    def advance_time(self, ms: int, board: Board) -> list[str]:
        """
        מקדמת את זמן הסימולציה בצעדים קטנים (Ticks) לפתרון מדויק של התנגשויות.
        """
        finished_pieces_kinds = []
        remaining_ms = ms

        tick_size = 100
        while remaining_ms > 0:
            current_tick = min(tick_size, remaining_ms)
            remaining_ms -= current_tick

            # 1. נקדם את הזמן לכל הכלים הפעילים
            for motion in self._active_motions:
                if not motion.is_finished:
                    motion.advance_time(current_tick)

            # 2. נפתור חסימות והתנגשויות שהתרחשו ב-Tick הזה
            self._resolve_collisions(board)

            # 3. ננחית כלים שסיימו את התנועה שלהם
            for motion in list(self._active_motions):
                if motion.is_finished:
                    self._handle_arrival(motion, board)
                    finished_pieces_kinds.append(motion.piece.kind)
                    self._active_motions.remove(motion)

        return finished_pieces_kinds

    def _resolve_collisions(self, board: Board) -> None:
        """מזהה ופותרת התנגשויות (חברים ואויבים) בין כלים הנמצאים באוויר ועל הלוח"""
        motions_to_remove = set()
        motions_to_arrive_instantly = set()

        for motion in self._active_motions:
            if motion in motions_to_remove or motion in motions_to_arrive_instantly or motion.is_finished:
                continue

            next_pos = motion.get_next_physical_position()
            if not next_pos:
                continue

            # 1. בדיקת התנגשות עם כלי דינמי אחר באוויר (שחוסם את משבצת היעד הבאה שלנו)
            active_piece_there = None
            other_motion_to_kill = None

            for other_motion in self._active_motions:
                if other_motion == motion or other_motion.is_finished or other_motion in motions_to_remove or other_motion in motions_to_arrive_instantly:
                    continue

                # התנגשות באוויר: הכלי האחר נמצא כרגע או יהיה ב-next_pos שלנו ב-Tick הזה
                if (other_motion.get_current_physical_position() == next_pos or
                        other_motion.get_next_physical_position() == next_pos):

                    # שומר שוויון אמין: מי שאינדקס הרישום שלו בארביטר גבוה יותר הוא היוזם האחרון
                    idx_motion = self._active_motions.index(motion)
                    idx_other = self._active_motions.index(other_motion)

                    if idx_motion > idx_other:
                        active_piece_there = other_motion.piece
                        other_motion_to_kill = other_motion
                        break

            # 2. בדיקת התנגשות עם כלי סטטי על הלוח (במידה ואין התנגשות דינמית באוויר)
            static_piece = None
            if not active_piece_there:
                static_piece = board.get_piece_at(next_pos)

            blocking_piece = static_piece or active_piece_there
            if blocking_piece:
                # א. התנגשות חברים (אותו צבע) -> הכלי שיזם אחרון נבלם משבצת אחת קודם (במיקומו הנוכחי)
                if blocking_piece.color == motion.piece.color:
                    current_idx = motion.get_current_physical_step_idx()
                    motion.force_stop_at_step(current_idx)

                    # ננחית את הכלי מיידית ביעדו החדש
                    motions_to_arrive_instantly.add(motion)

                # ב. התנגשות אויבים (צבעים שונים) -> הכלי שיזם אחרון אוכל ונעצר ב-next_pos
                else:
                    current_idx = motion.get_current_physical_step_idx()
                    motion.force_stop_at_step(current_idx + 1)

                    # ננחית את הכלי התוקף מיידית ביעדו המעודכן (משבצת האכילה)
                    motions_to_arrive_instantly.add(motion)

                    # הסרת האויב הסטטי מהלוח
                    if static_piece:
                        board.remove_piece_at(next_pos)

                    # הסרת האויב הדינמי מהלוח ומהארביטר
                    if other_motion_to_kill:
                        board.remove_piece_at(other_motion_to_kill.source)
                        motions_to_remove.add(other_motion_to_kill)

        # הנחתה מיידית של הכלים שנעצרו/אכלו
        for m in motions_to_arrive_instantly:
            self._handle_arrival(m, board)
            if m in self._active_motions:
                self._active_motions.remove(m)

        # הסרה מסודרת של תנועות האויבים שנאכלו
        for m in motions_to_remove:
            if m in self._active_motions:
                self._active_motions.remove(m)
    def _handle_arrival(self, motion: Motion, board: Board) -> None:
        """מטפלת ברגע הנחיתה הלוגי של הכלי ביעד החדש שלו"""
        # 1. הסרה לוגית ממשבצת המקור (רק אם הכלי אכן זז ממנה פיזית)
        if motion.source != motion.target:
            board.remove_piece_at(motion.source)

        # 2. ניקוי כלי אויב שעומד ביעד (במידה ויש אכילה סופית)
        target_piece = board.get_piece_at(motion.target)
        if target_piece and target_piece.color != motion.piece.color:
            board.remove_piece_at(motion.target)

        # 3. נחיתת הכלי ועדכון מיקומו החדש
        motion.piece.cell = motion.target
        board.add_piece(motion.piece)