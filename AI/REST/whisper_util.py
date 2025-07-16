import sounddevice as sd
import numpy as np
import wave
import tempfile
import openai
import os

def record_audio(duration=4, samplerate=16000):
    print("🎙️ Говори сега...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    print("🎧 Записът е приключен.")

    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with wave.open(temp_wav.name, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(recording.tobytes())

    return temp_wav.name

def transcribe_audio(file_path):
    print("🧠 Транскрипция с Whisper...")
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    with open(file_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="bg"
        )
    return transcript.text