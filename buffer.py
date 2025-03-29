import multiprocessing as mp
from collections import deque
import numpy as np
import cv2
import base64

class Buffer:
    def __init__(self, capacity):
        # Holds up to 'capacity' most recent frames
        self.queue = deque(maxlen=capacity)
        self.lock = mp.Lock()

    def add(self, image: np.ndarray):
        with self.lock:
            self.queue.append(image)

    def get_images(self):
        converted = []
        with self.lock:
            for frame in self.queue:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue

                # Convert JPEG bytes to base64 string
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                converted.append(jpg_as_text)
        return converted
