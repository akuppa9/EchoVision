from buffer import Buffer
import multiprocessing as mp
import cv2
import time

def camera_process(buffer):
    print("Camera process started")
    cap = cv2.VideoCapture('http://172.20.10.10:81/stream')  # Adjust URL to your MJPEG endpoint

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
        print("frame added")

def agent_process(buffer):
    print("Agent process started")
    while False:
        # Retrieve the base64-encoded images from the buffer
        images = buffer.get_images()
        print(f"Agent sees {len(images)} frames in the buffer.")

        # You can process or send these images somewhere else here.
        # For this example, we’ll just wait a short time and loop.
        time.sleep(2)

def main():
    # Create a Buffer that holds a maximum of 5 frames.
    buffer = Buffer(capacity=5)

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


# check for trigger to start whole chain process
# get query from transcribed speech
# get images from buffer
# pass images, query, param_for_next_action (empty string) into reasoning
# get response from reasoning (next step in chain)
# pass response into action
# get action response
# put into reasoning

if __name__ == "__main__":
    main()
