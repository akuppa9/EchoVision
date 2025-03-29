import multiprocessing as mp
from collections import deque
import numpy as np

class Buffer:
    def __init__(self, capacity):
        self.queue = deque(maxlen=capacity)
        self.lock = mp.Lock()

    def add(self, image: np.ndarray):
        with self.lock:
            self.queue(image)

    def get_images(self):
        converted = []
        with self.lock:
            for i in range(len(self.queue)):
                # Convert to base 64
                converted.append(...)

        return converted