import csv
import time
from engine.io_utils.board_parser import BoardParser
from engine.model.game_state import GameState
from engine.real_time.real_time_arbiter import RealTimeArbiter
from engine.game_engine import GameEngine
from engine.model.position import Position

BOARD_CSV_PATH = "server/assets/initial_board.csv"

# מילון של כל המשחקים הפעילים: room_id → GameEngine
_games: dict[str, GameEngine] = {}

# שעון לכל משחק: room_id → זמן עדכון אחרון
_last_update: dict[str, float] = {}

# המרה מאות לאינדקס עמודה
COL_FROM_LETTER = {letter: i for i, letter in enumerate("abcdefgh")}


def _load_initial_board() -> str:
    """קורא את קובץ ה-CSV ומחזיר מחרוזת בפורמט שה-BoardParser מבין."""
    rows = []
    with open(BOARD_CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                rows.append(' '.join(row))
    return '\n'.join(rows)


def create_game(room_id: str) -> None:
    """
    יוצר משחק חדש לחדר.
    נקרא כשמאצ'מייקינג מוצא זוג או כשחדר מתמלא.
    """
    board_str = _load_initial_board()
    board = BoardParser.parse(board_str)
    state = GameState(board)
    arbiter = RealTimeArbiter()
    _games[room_id] = GameEngine(state, arbiter)
    _last_update[room_id] = time.time()


def advance_game(room_id: str) -> list:
    """
    מקדם את שעון הפיזיקה של המשחק.
    מחזיר רשימת מלכים שנלכדו (אם יש).
    נקרא מלולאה ברקע בשרת.
    """
    engine = _games.get(room_id)
    if engine is None:
        return []

    now = time.time()
    delta_ms = int((now - _last_update[room_id]) * 1000)
    _last_update[room_id] = now

    return engine.wait(delta_ms)


def _parse_pos(pos_str: str) -> Position:
    """
    ממיר מחרוזת כמו 'e2' ל-Position.
    'e' → עמודה 4, '2' → שורה 1 (בקוד שורות מתחילות מ-0)
    """
    col = COL_FROM_LETTER[pos_str[0]]
    row = int(pos_str[1]) - 1
    return Position(row, col)


def handle_move(room_id: str, command: str) -> dict:
    """
    מטפל בפקודת תזוזה.
    command = "e2e5" — מקור + יעד
    """
    engine = _games.get(room_id)
    if engine is None:
        return {"IS_ACCEPTED": False, "REASON": "GAME_NOT_FOUND"}

    source = _parse_pos(command[:2])
    target = _parse_pos(command[2:])
    return engine.move_request(source, target)


def handle_jump(room_id: str, command: str) -> dict:
    """
    מטפל בפקודת קפיצה.
    command = "a1" — מיקום בלבד
    """
    engine = _games.get(room_id)
    if engine is None:
        return {"IS_ACCEPTED": False, "REASON": "GAME_NOT_FOUND"}

    pos = _parse_pos(command)
    return engine.jump_request(pos)


def get_snapshot(room_id: str):
    """מחזיר snapshot של מצב המשחק."""
    engine = _games.get(room_id)
    if engine is None:
        return None
    return engine.get_snapshot()


def get_active_motions(room_id: str) -> list:
    """מחזיר רשימת כלים בתנועה עם מיקומי אינטרפולציה."""
    engine = _games.get(room_id)
    if engine is None:
        return []
    return engine.get_active_motion_states()


def end_game(room_id: str) -> None:
    """מסיר משחק מהזיכרון בסוף המשחק."""
    _games.pop(room_id, None)
    _last_update.pop(room_id, None)

