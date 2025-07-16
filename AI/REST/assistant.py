import os
import json
import yaml
import openai
import requests
from whisper_util import record_audio, transcribe_audio
from speak_util import speak
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

with open("iot_config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

def build_system_prompt(config):
    devices_desc = []
    for room, data in config["rooms"].items():
        for dev, details in data["devices"].items():
            dev_type = details["type"]
            devices_desc.append(f"{dev} в {room} ({dev_type})")
    devices_text = "\n".join(devices_desc)
    return f"""Ти си IoT асистент. Имаш достъп до следните устройства:
{devices_text}
Отговаряй с JSON във формат:
{{"action": "get/post", "room": "...", "device": "...", "param": "...", "value": "..."}} ако е POST.
Ако питането е за стойност, param трябва да е temperature, humidity или all.
Ако е за включване/изключване, param е state и value е on/off."""

def send_request(config, cmd):
    room = cmd["room"]
    device = cmd["device"]
    action = cmd["action"]
    param = cmd.get("param", "")
    value = cmd.get("value", "")

    dev_info = config["rooms"][room]["devices"][device]
    url = dev_info["url"]
    if action == "get":
        endpoint = dev_info["methods"]["GET"].get(param, "/")
        response = requests.get(url + endpoint)
        return response.text
    elif action == "post":
        payload = {param: value}
        response = requests.post(url, json=payload)
        return response.text
    return "Невалидна заявка."

def main():
    system_prompt = build_system_prompt(CONFIG)
    while True:
        path = record_audio()
        user_text = transcribe_audio(path)
        print("📜 Чуто:", user_text)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
        response = openai.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
        reply = response.choices[0].message.content.strip()
        print("🤖 OpenAI отговори:\n", reply)

        try:
            cmd = json.loads(reply)
            result = send_request(CONFIG, cmd)
            speak(f"Резултат: {result}")
        except Exception as e:
            print("⚠️ Грешка:", e)
            speak("Не можах да изпълня командата.")

if __name__ == "__main__":
    main()
