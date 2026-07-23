import asyncio
import json
import websockets
from server.bus.event_bus import bus
from server.bus.events import GameEvent
from server.services import auth_service, game_service, matchmaking_service, room_service

# מילון: username → websocket (כדי שנוכל לשלוח הודעות ליריב)
_connections: dict[str, any] = {}


async def send(ws, data: dict):
    """שולח הודעה ללקוח אחד."""
    await ws.send(json.dumps(data))

async def handler(ws):
    """מטפל בחיבור של לקוח אחד — רץ כל עוד הלקוח מחובר."""
    username = None
    room_id = None

    try:
        async for raw in ws:
            data = json.loads(raw)
            msg_type = data.get("type")

            if msg_type == "login":
                username, room_id = await handle_login(ws, data)

            elif msg_type == "play":
                room_id = await handle_play(ws, username)

            elif msg_type == "room":
                room_id = await handle_room(ws, username, data)

            elif msg_type == "move":
                await handle_move(ws, username, room_id, data)

            elif msg_type == "jump":
                await handle_jump(ws, username, room_id, data)

    finally:
        if username:
            _connections.pop(username, None)
            bus.publish(GameEvent.PLAYER_DISCONNECTED, {
                "username": username,
                "room_id": room_id
            })


async def handle_login(ws, data: dict):
    result = auth_service.login(data["username"], data["password"])

    if not result["success"]:
        await send(ws, {"type": "login_failed", "message": result["message"]})
        return None, None

    username = data["username"]
    _connections[username] = ws
    await send(ws, {"type": "login_ok", "rating": result["rating"]})
    bus.publish(GameEvent.PLAYER_CONNECTED, {"username": username})
    return username, None


async def handle_play(ws, username: str):
    rating = auth_service.login  # נקבל את הדירוג מה-DB
    from server.db.user_repository import get_rating
    rating = get_rating(username)

    opponent = matchmaking_service.find_match(username, rating)

    if opponent:
        matchmaking_service.remove_from_queue(opponent)
        room = room_service.create_match_room(opponent, username)
        room_id = room["room_id"]
        game_service.create_game(room_id)

        await send(ws, {"type": "game_start", "room_id": room_id, "color": "black"})
        opponent_ws = _connections.get(opponent)
        if opponent_ws:
            await send(opponent_ws, {"type": "game_start", "room_id": room_id, "color": "white"})
    else:
        matchmaking_service.add_to_queue(username, rating)
        await send(ws, {"type": "waiting"})

    return room_id if opponent else None


async def handle_room(ws, username: str, data: dict):
    action = data.get("action")

    if action == "create":
        room = room_service.create_new_room(username)
        room_id = room["room_id"]
        game_service.create_game(room_id)
        await send(ws, {"type": "room_created", "room_id": room_id})
        return room_id

    elif action == "join":
        room_id = data.get("room_id")
        room = room_service.join_existing_room(room_id, username)

        if room is None:
            await send(ws, {"type": "room_error", "message": "חדר לא קיים"})
            return None

        await send(ws, {"type": "room_joined", "room_id": room_id})

        if room["black"] == username:
            white = room["white"]
            white_ws = _connections.get(white)
            if white_ws:
                await send(white_ws, {"type": "game_start", "color": "white"})
            await send(ws, {"type": "game_start", "color": "black"})

        return room_id

    return None


async def handle_move(ws, username: str, room_id: str, data: dict):
    result = game_service.handle_move(room_id, data["command"])
    await send(ws, {"type": "move_result", "result": result})

    if result["IS_ACCEPTED"]:
        bus.publish(GameEvent.MOVE_MADE, {"username": username, "room_id": room_id, "command": data["command"]})


async def handle_jump(ws, username: str, room_id: str, data: dict):
    result = game_service.handle_jump(room_id, data["command"])
    await send(ws, {"type": "jump_result", "result": result})

    if result["IS_ACCEPTED"]:
        bus.publish(GameEvent.JUMP_MADE, {"username": username, "room_id": room_id, "command": data["command"]})