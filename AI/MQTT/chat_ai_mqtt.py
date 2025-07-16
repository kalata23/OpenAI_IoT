import io
import json
import time
import sounddevice as sd
import scipy.io.wavfile as wav
from gtts import gTTS
from playsound import playsound
from openai import OpenAI
import paho.mqtt.client as mqtt
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ==== OpenAI ==== 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# ==== MQTT ==== 
MQTT_BROKER = "192.168.0.67"
MQTT_PORT = 1883
MQTT_USER = "mqtt_agent"
MQTT_PASS = "p@p1t0_k0r1t0"
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# ==== System prompt ==== 
SYSTEM_PROMPT = """
Ти си IoT асистент. Когато получиш команда, отговаряй с JSON в MQTT формат:

"Включи лампата" → 
{
  "action": "publish",
  "topic": "devices/room1/relay/set",
  "payload": "ON"
}

"Каква е температурата" → 
{
  "action": "read",
  "topic": "sensors/room1/dht21"
}

Ако не можеш да действаш, отговори само с обяснение.
"""

# ==== Audio recording ====
def record_audio(filename="recording.wav", duration=5, samplerate=16000):
    print("🎙️ Говори сега...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, samplerate, recording)
    print("🎧 Записът е приключен.")
    return filename

# ==== Whisper ====
def transcribe_with_whisper(filepath):
    print("🧠 Транскрипция с Whisper...")
    with open(filepath, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="bg"
        )
    return transcript.text

# ==== GPT + MQTT  ====
def process_with_openai(user_text):
    print("📨 Заявка към OpenAI:", user_text)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )
    reply = response.choices[0].message.content.strip()
    print("🤖 OpenAI отговори:\n", reply)

    try:
        data = json.loads(reply)
        if data.get("action") == "publish":
            mqtt_client.publish(data["topic"], data["payload"])
            return f"Изпратих команда към {data['topic']}: {data['payload']}"
        elif data.get("action") == "read":
            return "Трябва да имплементираме четене от сензори (subscribe)."
    except json.JSONDecodeError:
        return reply  
# ==== TTS ====
def speak(text):
    print("🗣️ Изговаряне:", text)
    tts = gTTS(text, lang='bg')
    filename = "response.mp3"
    tts.save(filename)
    time.sleep(1)
    playsound(filename)

def main_loop():
    while True:
        try:
            record_audio()
            query = transcribe_with_whisper("recording.wav")
            print("📜 Чуто:", query)
            result = process_with_openai(query)
            speak(result)
        except KeyboardInterrupt:
            print("👋 Изход.")
            break
        except Exception as e:
            print("⚠️ Грешка:", e)

if __name__ == "__main__":
    main_loop()
