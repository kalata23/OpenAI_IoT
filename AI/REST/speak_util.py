from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile

def speak(text):
    print(f"🗣️ Изговаряне: {text}")
    tts = gTTS(text=text, lang="bg")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    sound = AudioSegment.from_mp3(temp_file.name)
    play(sound)
