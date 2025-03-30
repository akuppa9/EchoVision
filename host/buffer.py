import multiprocessing as mp
from multiprocessing.managers import SyncManager
from collections import deque
import numpy as np
import cv2
import base64

# Define a subclass (it can be empty if you don't need extra functionality)
class SharedDeque(deque):
    pass

# Create a custom manager class.
class DequeManager(SyncManager):
    pass

# Register the SharedDeque with the manager,
# explicitly exposing the methods you need.
DequeManager.register('deque', SharedDeque, exposed=['append', 'clear', '__len__', '__getitem__'])

def create_manager():
    manager = DequeManager()
    manager.start()
    return manager

class Buffer:
    def __init__(self, capacity, manager):
        # Create a shared deque with a maximum length.
        self.queue = manager.deque(maxlen=capacity)
        # Use a shared lock from the manager.
        self.lock = manager.Lock()
        self.capacity = capacity

    def add(self, image: np.ndarray):
        with self.lock:
            self.queue.append(image)

    def get_images(self):
        converted = []
        with self.lock:
            n = len(self.queue)
            # Access each element by index.
            frames = [self.queue[i] for i in range(n)]
            for frame in frames:
                # Encode the frame as JPEG.
                ret, buffer_img = cv2.imencode('.jpeg', frame)
                if not ret:
                    continue
                # Convert JPEG bytes to a base64 string.
                jpg_as_text = base64.b64encode(buffer_img).decode('utf-8')
                converted.append(jpg_as_text)
        return converted