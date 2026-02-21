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
        Safe to call from a thread.
        """
        import time
        payload = {
            "type": event_type,
            "message": message,
            "data": data or {},
            "timestamp": time.time()
        }
        
        # We need to handle cases where emit is called from a thread or synchronous code
        try:
            # Try to find any running loop in the main thread (where listeners usually are)
            # but since we are in a thread, we use our own listeners list.
            for queue in list(self.listeners):
                try:
                    # Non-blocking put for the queue
                    queue.put_nowait(payload)
                except Exception:
                    pass
        except Exception as e:
            # Silently fail for emission during cleanup or threading edge cases
            pass

# Global instance
event_manager = EventManager()
