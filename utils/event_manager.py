import asyncio
import json
from typing import List

class EventManager:
    def __init__(self):
        self.listeners: List[asyncio.Queue] = []

    async def subscribe(self):
        queue = asyncio.Queue()
        self.listeners.append(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self.listeners.remove(queue)

    def emit(self, event_type: str, message: str, data: dict = None):
        """
        Emits an event to all connected SSE listeners.
        """
        payload = {
            "type": event_type,
            "message": message,
            "data": data or {},
            "timestamp": asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
        }
        
        # We need to handle cases where emit is called from a thread or synchronous code
        try:
            loop = asyncio.get_running_loop()
            for queue in self.listeners:
                loop.call_soon_threadsafe(queue.put_nowait, payload)
        except RuntimeError:
            # No running loop (e.g. initial setup)
            pass

# Global instance
event_manager = EventManager()
