import os
# import speech_recognition as sr
import requests
from dotenv import load_dotenv

load_dotenv()

def transcribe_with_elevenlabs(audio_file_path):
    api_key = os.getenv("ELEVEL_LABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable is not set.")
        return None

    # Endpoint and required parameters based on Eleven Labs API docs.
    url = "https://api.us.elevenlabs.io/v1/speech-to-text"
    headers = {
        "xi-api-key": api_key,
    }
    data = {
        "model_id": "scribe_v1",  # required model identifier
        # Optionally, include language_code if known, e.g. "en"
        "language_code": "en"
    }
    # Send the file as a multipart form.
    with open(audio_file_path, "rb") as audio_file:
        files = {"file": audio_file}
        response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code != 200:
        print("Error in transcription:", response.text)
        return None

    result = response.json()
    return result.get("text", None)

def main():
    pass
#     recognizer = sr.Recognizer()
#     microphone = sr.Microphone()

#     # Calibrate microphone to ambient noise.
#     print("Calibrating microphone for ambient noise. Please wait...")
#     with microphone as source:
#         recognizer.adjust_for_ambient_noise(source, duration=2)
#     print("Calibration complete. Start speaking now.")

#     while True:
#         with microphone as source:
#             print("Listening...")
#             audio = recognizer.listen(source)

#         # Save the recorded audio to a temporary WAV file.
#         audio_file_path = "temp_audio.wav"
#         with open(audio_file_path, "wb") as f:
#             f.write(audio.get_wav_data())

#         # Transcribe the audio using Eleven Labs' transcription endpoint.
#         transcription = transcribe_with_elevenlabs(audio_file_path)
#         if transcription:
#             print("Transcribed Text:", transcription)
#         else:
#             print("Could not transcribe the audio.")

if __name__ == "__main__":
    main()
