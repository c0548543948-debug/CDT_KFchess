from server.db.room_repository import create_room, get_room, join_room, delete_room

_next_room_id = 1


def create_new_room(username: str) -> dict:
    """יוצר חדר חדש ומחזיר את פרטיו."""
    global _next_room_id
    room_id = str(_next_room_id)
    _next_room_id += 1
    create_room(room_id, username)
    return get_room(room_id)


def join_existing_room(room_id: str, username: str) -> dict | None:
    """
    מצטרף לחדר קיים.
    מחזיר פרטי החדר אם הצליח, None אם החדר לא קיים.
    """
    return join_room(room_id, username)


def get_room_by_id(room_id: str) -> dict | None:
    """מחזיר פרטי חדר לפי ID, או None אם לא קיים."""
    return get_room(room_id)


def close_room(room_id: str) -> None:
    """סוגר חדר בסוף משחק."""
    delete_room(room_id)

def create_match_room(white: str, black: str) -> dict:
    """
    יוצר חדר עבור שני שחקנים שמצא המאצ'מייקינג.
    """
    global _next_room_id
    room_id = str(_next_room_id)
    _next_room_id += 1
    create_room(room_id, white)
    join_room(room_id, black)
    return get_room(room_id)