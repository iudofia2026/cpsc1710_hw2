# 1_tts_test.py
from dotenv import load_dotenv
from openai import OpenAI

# load API key from .env into environment
load_dotenv()

client = OpenAI()

# minimal TTS request -> write to mp3
resp = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input="hello from the python version for cpsc 1710 saving an mp3"
)

with open("python_out.mp3", "wb") as f:
    f.write(resp.content)

print("wrote python_out.mp3")
