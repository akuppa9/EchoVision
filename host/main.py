from buffer import Buffer, create_manager
import multiprocessing as mp
import cv2
import time
import numpy as np
from test_chain import test_chain
from transcription import transcribe_with_elevenlabs

def camera_process(buffer):
    print("Camera process started")
    cap = cv2.VideoCapture('http://172.20.10.3:81/stream')  # Adjust URL to your MJPEG endpoint

    if not cap.isOpened():
        print("Error: Unable to open MJPEG stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            # If reading a frame failed, skip
            continue
        
        # Add the new frame to the buffer
        buffer.add(frame)

def agent_process(buffer):
    print("Agent process started")
    while True:
        
        # Retrieve the base64-encoded images from the buffer
        images = buffer.get_images()
        query = [transcribe_with_elevenlabs("../Park.wav")]
       
        print(f"Agent sees {images} frames in the buffer.")
        # print(f"Agent sees {images} frames in the buffer.")
        test_chain(images, query)
        
        # You can process or send these images somewhere else here.
        # For this example, we’ll just wait a short time and loop.
        time.sleep(2)

def main():
    manager = create_manager()
    # Create a Buffer that holds a maximum of 5 frames.
    buffer = Buffer(capacity=5, manager=manager)

    # Pass the same buffer instance to both processes.
    camera = mp.Process(target=camera_process, args=(buffer,))
    agent = mp.Process(target=agent_process, args=(buffer,))

    camera.start()
    agent.start()

    try:
        camera.join()
        agent.join()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Stopping processes...")
        camera.terminate()
        agent.terminate()
        camera.join()
        agent.join()

if __name__ == "__main__":
    main()
