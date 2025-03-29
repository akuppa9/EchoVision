import multiprocessing as mp
from collections import deque

class Buffer:
    def __init__(self, capacity):
        self.queue = deque(maxlen=capacity)
        self.lock = mp.Lock()

    def add(self):
        with self.lock:
            # Add image to queue

    def get_images(self):
        converted = []
        with self.lock:
            for i in range(len(self.queue)):
                # Convert to base 64
                converted.append(...)

        return converted