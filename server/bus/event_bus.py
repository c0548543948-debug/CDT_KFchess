from collections import defaultdict
from server.bus.events import GameEvent


class EventBus:
    def __init__(self):
        self._subscribers: dict[GameEvent, list] = defaultdict(list)

    def subscribe(self, event: GameEvent, callback) -> None:
        self._subscribers[event].append(callback)

    def publish(self, event: GameEvent, data: dict = None) -> None:
        for callback in self._subscribers[event]:
            callback(data or {})


bus = EventBus()