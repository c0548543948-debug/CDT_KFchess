import threading
import asyncio
import websockets
import json


class WSClient:
    def __init__(self, on_message):
        """
        on_message - פונקציה שתיקרא כל פעם שמגיע מסר מהשרת.
        """
        self._on_message = on_message
        self._websocket = None
        self._loop = None

    def connect(self, url: str):
        """
        פותח חיבור לשרת ומריץ את ההאזנה ב-thread נפרד.
        """
        self._loop = asyncio.new_event_loop()
        thread = threading.Thread(
            target=self._run,
            args=(url,),
            daemon=True
        )
        thread.start()

    def _run(self, url: str):
        """
        רצה בתוך ה-thread — מתחבר ומאזין.
        """
        self._loop.run_until_complete(self._listen(url))

    async def _listen(self, url: str):
        """
        מתחבר לשרת ומאזין למסרים.
        """
        async with websockets.connect(url) as ws:
            self._websocket = ws
            async for message in ws:
                data = json.loads(message)
                self._on_message(data)

    def send(self, data: dict):
        """
        שולח מסר לשרת. נקרא מלולאת הציור.
        """
        if self._websocket is None:
            return
        asyncio.run_coroutine_threadsafe(
            self._websocket.send(json.dumps(data)),
            self._loop
        )