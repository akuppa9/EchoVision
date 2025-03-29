from buffer import Buffer
import multiprocessing as mp

def camera_process(buffer):
    print("Camera process started")

    # Add in the camera capture while look

def agent_process(buffer):
    print("Agent Process start")
    
    # Add while look for agent process

def main():
    buffer = Buffer(capacity=5)

    camera = mp.Process(target=camera_process)
    agent = mp.Process(target=agent_process)

    camera.start()
    agent.start()

    try:
        camera.join()
        agent.join()
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        camera.terminate()
        agent.terminate()
        camera.join()
        agent.join()

if __name__ == "__main__":
    main()