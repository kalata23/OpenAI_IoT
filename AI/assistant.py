import os
import yaml
import requests
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

valid_rooms = [r['name'] for r in config['rooms']]

def query_openai(prompt, system=None):
    system_prompt = system or f"""
Ти си домашен асистент. Върни JSON във формат:
{{"action": "...", "room": "..."}}
Позволени действия: get_temperature, get_humidity, get_all, turn_on, turn_off, exit
Позволени стаи: {", ".join(valid_rooms)}
Ако няма подходяща стая, върни стаята все пак.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def explain_result_to_user(context):
    prompt = f"На база на следната информация: {context}, кажи на потребителя на български с човешки език какво се случва."
    return query_openai(prompt, system="Ти си приятелски асистент и обясняваш разбираемо какво се случи.")

def find_sensor(room, data_type):
    for r in config['rooms']:
        if r['name'] == room:
            for s in r.get('sensors', []):
                if s['type'] == "temperature_humidity":
                    return s['ip'], s['endpoints'].get(data_type)
    return None, None

def find_device(room, device_type):
    for r in config['rooms']:
        if r['name'] == room:
            for d in r.get('devices', []):
                if d['type'] == device_type:
                    return d['ip'], d['endpoints']
    return None, None

def handle_command(json_command):
    try:
        command = json.loads(json_command)
        action = command.get("action")
        room = command.get("room", "").strip()

        if not room:
            print("Не е посочена стая.")
            return

        if room not in valid_rooms:
            print(f"Стаята '{room}' не съществува в конфигурацията.")
            return

        if action == "exit":
            print("Излизане...")
            exit()

        if action in ["get_temperature", "get_humidity", "get_all"]:
            data_type = action.replace("get_", "")
            ip, endpoint = find_sensor(room, data_type if action != "get_all" else "all")
            if not ip or not endpoint:
                print(f"В {room} няма конфигуриран сензор за {data_type}.")
                return
            try:
                response = requests.get(f"http://{ip}{endpoint}", timeout=5)
                data = response.json()
                context = f"{action} от стая {room}: {data}"
                explanation = explain_result_to_user(context)
                print(explanation)
            except:
                print(f"Съжалявам, не можах да получа данни от сензора в {room}.")
        elif action in ["turn_on", "turn_off"]:
            ip, endpoints = find_device(room, "relay")
            if not ip or not endpoints:
                print(f"В {room} няма конфигурирана лампа.")
                return
            payload = "on" if action == "turn_on" else "off"
            try:
                requests.post(f"http://{ip}{endpoints['control']}", data=payload, timeout=5)
                state_resp = requests.get(f"http://{ip}{endpoints['state']}", timeout=5)
                new_state = state_resp.json().get("state", "unknown")
                context = f"Лампата в {room} е зададена да бъде '{payload}'. Ново състояние: {new_state}."
                explanation = explain_result_to_user(context)
                print(explanation)
            except:
                print(f"Съжалявам, не успях да управлявам лампата в {room}.")
        else:
            print("Неразпознато действие.")
    except Exception as e:
        print("Грешка при обработка на отговора:", e)

def main():
    print("Асистентът е активен. Напиши 'изход' за край.")
    while True:
        user_input = input("Ти: ")
        ai_reply = query_openai(user_input)
        handle_command(ai_reply)

if __name__ == "__main__":
    main()
