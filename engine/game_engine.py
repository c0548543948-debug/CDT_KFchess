from model.game_state import GameState
from model.position import Position
from real_time.real_time_arbiter import RealTimeArbiter  # שימי לב לנתיב הייבוא אם השתנה
from rules.rule_engine import validate_motion


class GameEngine:
    def __init__(self, game_state: GameState, arbiter: RealTimeArbiter):
        self._state = game_state
        self._arbiter = arbiter

    def get_snapshot(self) -> GameState:
        """מייצר ומחזיר תמונת מצב (Snapshot) לקריאה בלבד עבור ה-Renderer"""
        return self._state.clone()

    def move_request(self, source: Position, target: Position) -> dict:
        """
        השער הציבורי המרכזי לקבלת בקשות תנועה מהשחקנים/טסטים.
        מחזיר מילון בתבנית: {"IS_ACCEPTED": bool, "REASON": string}
        """
        # Guard 1: דחיית כל הבקשות אם המשחק כבר הסתיים
        if self._state.game_over:
            return {"IS_ACCEPTED": False, "REASON": "GAME OVER"}

        piece = self._state.board.get_piece_at(source)
        if piece and piece.cooldown_remaining > 0:
            return {"IS_ACCEPTED": False, "REASON": "PIECE IN COOLDOWN"}

        # Guard 2: דחיית הבקשה אם יש כבר תנועה פעילה במסלול המבוקש (העברנו את ה-board!)
        if self._arbiter.is_route_active(self._state.board, source, target):
            return {"IS_ACCEPTED": False, "REASON": "MOTION IN PROGRESS"}

        # Guard 3: העברת הבקשה ל-RuleEngine לבדיקת חוקיות שחמטית
        rule_result = validate_motion(self._state.board, source, target)

        if not rule_result["IS_VALID"]:
            return {"IS_ACCEPTED": False, "REASON": rule_result["REASON"]}

        # אם כל השומרים עברו בהצלחה - מתחילים את התנועה בזמן אמת!
        self._arbiter.start_motion(self._state.board, source, target)
        return {"IS_ACCEPTED": True, "REASON": "OK"}

    def wait(self, ms: int) -> None:
        """האצלת סמכות לקידום זמן הסימולציה בארביטר (העברנו את ה-board!)"""
        self._arbiter.advance_time(ms, self._state.board)

    def notify_king_captured(self, loser_color: str) -> None:
        """קבלת התראה על אכילת מלך ועדכון מצב סיום המשחק"""
        self._state.game_over = True
        self._state.winner = "black" if loser_color == "white" else "white"