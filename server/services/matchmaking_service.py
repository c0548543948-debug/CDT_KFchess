import time
from server.config import ELO_RANGE, MATCHMAKING_TIMEOUT_SEC

# רשימת ממתינים: [{"username": ..., "rating": ..., "joined_at": ...}]
_waiting: list[dict] = []


def add_to_queue(username: str, rating: int) -> None:
    """מוסיף שחקן לתור המאצ'מייקינג."""
    _waiting.append({
        "username": username,
        "rating": rating,
        "joined_at": time.time()
    })


def remove_from_queue(username: str) -> None:
    """מסיר שחקן מהתור."""
    global _waiting
    _waiting = [p for p in _waiting if p["username"] != username]


def find_match(username: str, rating: int) -> str | None:
    """
    מחפש יריב מתאים בתור.
    מחזיר את שם היריב אם נמצא, None אחרת.
    """
    now = time.time()
    for candidate in _waiting:
        if candidate["username"] == username:
            continue
        # בדיקת פג תוקף
        if now - candidate["joined_at"] > MATCHMAKING_TIMEOUT_SEC:
            continue
        # בדיקת טווח ELO
        if abs(candidate["rating"] - rating) <= ELO_RANGE:
            return candidate["username"]
    return None


def cleanup_expired() -> None:
    """מסיר שחקנים שחיכו יותר מדקה."""
    now = time.time()
    global _waiting
    _waiting = [p for p in _waiting if now - p["joined_at"] <= MATCHMAKING_TIMEOUT_SEC]