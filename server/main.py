import asyncio
import websockets
from server.db.database import init_db
from server.api.websocket_handler import handler
from server.bus.event_bus import bus
from server.bus.events import GameEvent
from server.services import elo_service, game_service, room_service
from server.config import HOST, PORT


def on_game_over(data: dict):
    winner = data.get("winner")
    loser = data.get("loser")
    room_id = data.get("room_id")
    if winner and loser:
        elo_service.update_ratings(winner, loser)
    game_service.end_game(room_id)


def on_move_made(data: dict):
    print(f"[LOG] {data['username']} moved: {data['command']} in room {data['room_id']}")


def on_player_connected(data: dict):
    print(f"[LOG] {data['username']} connected")


def on_player_disconnected(data: dict):
    print(f"[LOG] {data['username']} disconnected from room {data['room_id']}")


async def main():
    init_db()

    bus.subscribe(GameEvent.GAME_OVER, on_game_over)
    bus.subscribe(GameEvent.MOVE_MADE, on_move_made)
    bus.subscribe(GameEvent.PLAYER_CONNECTED, on_player_connected)
    bus.subscribe(GameEvent.PLAYER_DISCONNECTED, on_player_disconnected)
    asyncio.create_task(game_loop())

    async with websockets.serve(handler, HOST, PORT):
        print(f"Server running on ws://{HOST}:{PORT}")
        await asyncio.Future()

async def game_loop():
    while True:
        for room_id in list(game_service._games.keys()):
            captured_kings = game_service.advance_game(room_id)
            if captured_kings:
                room = room_service.get_room_by_id(room_id)
                loser_color = captured_kings[0]
                winner_color = "black" if loser_color == "white" else "white"
                winner = room["white"] if winner_color == "white" else room["black"]
                loser = room["black"] if winner_color == "white" else room["white"]
                bus.publish(GameEvent.GAME_OVER, {
                    "winner": winner,
                    "loser": loser,
                    "room_id": room_id
                })
        await asyncio.sleep(0.016)

if __name__ == "__main__":
    asyncio.run(main())