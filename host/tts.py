from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os
import serial
import time
import io
from pydub import AudioSegment

load_dotenv()

def stream_audio_to_esp32(audio_data, port="/dev/ttyUSB0", baud_rate=115200):
    """
    Stream audio data to ESP32 via serial connection.
    
    Args:
        audio_data: Binary audio data from ElevenLabs
        port: Serial port (adjust based on your system)
        baud_rate: Communication speed
    """
    try:
        # Convert MP3 to raw PCM format that ESP32 can process
        audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
        # Convert to mono, 16kHz, 16-bit PCM for ESP32
        audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        raw_audio = audio.raw_data
        
        # Open serial connection
        ser = serial.Serial(port, baud_rate)
        time.sleep(2)  # Wait for ESP32 to reset
        
        # Send header (audio length)
        audio_length = len(raw_audio)
        ser.write(f"START:{audio_length}\n".encode())
        time.sleep(0.1)
        
        # Send audio in chunks
        chunk_size = 1024  # Adjust based on ESP32 buffer size
        for i in range(0, audio_length, chunk_size):
            chunk = raw_audio[i:i+chunk_size]
            ser.write(chunk)
            # Wait for acknowledgment if implementing handshaking
            # ack = ser.readline().strip()
            time.sleep(0.01)  # Small delay between chunks
        
        # End transmission
        ser.write(b"END\n")
        ser.close()
        print("Audio streaming complete")
        
    except Exception as e:
        print(f"Error streaming audio: {e}")

# Get audio from ElevenLabs
client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

audio = client.text_to_speech.convert(
    text="The first move is what sets everything in motion.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
)

# Instead of playing locally, stream to ESP32
stream_audio_to_esp32(audio)