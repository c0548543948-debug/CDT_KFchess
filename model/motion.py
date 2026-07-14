from model.position import Position
from model.piece import Piece
from config import STEP_DURATION_MS  # <--- הייבוא החדש!
class Motion:
    def __init__(self, piece: Piece, target: Position):
        self.piece: Piece = piece
        self.source: Position = piece.cell
        self.target: Position = target

        # חישוב רשימת הצעדים המלאה (כולל משבצת המקור ומשבצת היעד)
        self.steps: list[Position] = self._calculate_steps_path()
        self.total_steps: int = len(self.steps) - 1

        # שימוש בקבוע מתוך קובץ ה-config
        self.step_duration_ms: int = STEP_DURATION_MS
        self.total_duration_ms: int = self.total_steps * self.step_duration_ms

        # הזמן שחלף מתחילת התנועה
        self.elapsed_time: int = 0

        # האם התנועה נבלמה או נעצרה מוקדם מהצפוי בגלל התנגשות
        self.is_blocked: bool = False
        self.blocked_at_step: int = -1

    def _calculate_steps_path(self) -> list[Position]:
        """מחשב ומחזיר רשימה סדורה של כל המשבצות בדרך מהמקור ליעד"""
        steps = [self.source]

        # אם זה פרש, הוא מדלג ישירות ליעד (צעד יחיד)
        if self.piece.kind == "knight":
            steps.append(self.target)
            return steps

        # חישוב כיוון ההתקדמות עבור שאר הכלים (ישר, אלכסון וכו')
        row_diff = self.target.row - self.source.row
        col_diff = self.target.col - self.source.col

        step_row = (row_diff // abs(row_diff)) if row_diff != 0 else 0
        step_col = (col_diff // abs(col_diff)) if col_diff != 0 else 0

        current_row = self.source.row + step_row
        current_col = self.source.col + step_col

        while (current_row, current_col) != (self.target.row, self.target.col):
            steps.append(Position(row=current_row, col=current_col))
            current_row += step_row
            current_col += step_col

        steps.append(self.target)
        return steps

    def advance_time(self, ms: int) -> None:
        """מקדמת את הזמן שחלף עבור התנועה הזו, ללא חריגה מהזמן הכולל"""
        if self.is_blocked:
            return
        self.elapsed_time = min(self.total_duration_ms, self.elapsed_time + ms)

    def get_current_physical_step_idx(self) -> int:
        """מחזירה את אינדקס המשבצת הנוכחית בה הכלי נמצא פיזית באוויר"""
        if self.is_blocked:
            return self.blocked_at_step
        return min(self.elapsed_time // self.step_duration_ms, self.total_steps)

    def get_current_physical_position(self) -> Position:
        """מחזירה את אובייקט ה-Position הפיזי שהכלי תופס ברגע זה באוויר"""
        idx = self.get_current_physical_step_idx()
        return self.steps[idx]

    def get_next_physical_position(self) -> Position | None:
        """מחזירה את המשבצת הבאה אליה הכלי מנסה להיכנס, או None אם הגיע ליעד"""
        if self.is_blocked:
            return None
        current_idx = self.get_current_physical_step_idx()
        if current_idx >= self.total_steps:
            return None
        return self.steps[current_idx + 1]

    def get_interpolated_position(self) -> tuple[float, float]:
        """
        פונקציה קריטית עבור ממשק המשתמש (Renderer):
        מחזירה קואורדינטות רציפות (float) המייצגות החלקה חלקה של הכלי על המסך.
        """
        if self.is_blocked:
            pos = self.steps[self.blocked_at_step]
            return float(pos.row), float(pos.col)

        idx = self.get_current_physical_step_idx()
        if idx >= self.total_steps:
            target_pos = self.steps[self.total_steps]
            return float(target_pos.row), float(target_pos.col)

        # חישוב אחוז ההתקדמות (fraction) בתוך הצעד הנוכחי (בין 0.0 ל-1.0)
        fraction = (self.elapsed_time % self.step_duration_ms) / float(self.step_duration_ms)

        p1 = self.steps[idx]
        p2 = self.steps[idx + 1]

        interpolated_row = p1.row + (p2.row - p1.row) * fraction
        interpolated_col = p1.col + (p2.col - p1.col) * fraction
        return interpolated_row, interpolated_col

    def force_stop_at_step(self, step_idx: int) -> None:
        """בולמת את הכלי ומקבעת אותו במשבצת מסוימת במסלול עקב חסימה"""
        self.is_blocked = True
        self.blocked_at_step = step_idx
        self.elapsed_time = step_idx * self.step_duration_ms
        self.target = self.steps[step_idx]  # היעד החדש הופך להיות משבצת הבלימה

    @property
    def is_finished(self) -> bool:
        """התנועה מסתיימת כשהזמן מגיע לסופו או כשהכלי נבלם אקטיבית"""
        if self.is_blocked:
            return True
        return self.elapsed_time >= self.total_duration_ms