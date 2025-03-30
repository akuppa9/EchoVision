from buffer import Buffer, create_manager
import multiprocessing as mp
import cv2
import time
import numpy as np
from test_chain import test_chain
from transcription import transcribe_with_elevenlabs
import os
import time
import sounddevice as sd
import soundfile as sf

def record_audio(filename, duration=3, fs=44100):
    print("Recording for", duration, "seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    try:
        os.remove(filename)  # Remove the file if it exists
    except FileNotFoundError:
        pass
    # Save the recording as a WAV file
    sf.write(filename, recording, fs)

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
    # Polling algorithm to check for file named "mic.txt" acts as button
    while True:
        if os.path.exists("mic.txt"):
            print(f"Mic input detected, Starting Agent Process")
            # Remove the file to avoid re-triggering
            os.remove("mic.txt")
            # Retrieve the base64-encoded images from the buffer
            images = buffer.get_images()
            record_audio("output.wav")
            query = [transcribe_with_elevenlabs("output.wav")]
        
            #print(f"Agent sees {images} frames in the buffer.")
            # print(f"Agent sees {images} frames in the buffer.")
            test_chain(images, query )
            # You can process or send these images somewhere else here.
            # For this example, we’ll just wait a short time and loop.
            time.sleep(2)
            break
        # change polling rate right now is polling once every second
        time.sleep(1)

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
