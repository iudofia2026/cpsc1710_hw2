# 2_streaming_tts_test.py
# Stream TTS to an MP3 file, then play it on macOS (simplest + reliable)
from dotenv import load_dotenv
from openai import OpenAI
import subprocess

load_dotenv()
client = OpenAI()

# read narration text
with open("narration.txt", "r", encoding="utf-8") as f:
    text = f.read().strip()

out_path = "narration.mp3"

# STREAM to a file path (must be a string, not a BytesIO)
with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input=text,
) as resp:
    resp.stream_to_file(out_path)

# play the MP3 via macOS
subprocess.run(["open", out_path], check=False)
print("streamed narration and opened player")
# 2_streaming_tts_test.py
# Minimal + reliable: generate TTS to MP3, then open it (no streaming, no BytesIO)
from dotenv import load_dotenv
from openai import OpenAI
import subprocess

def main():
    load_dotenv()
    client = OpenAI()

    # read narration text
    with open("narration.txt", "r", encoding="utf-8") as f:
        text = f.read().strip()

    out_path = "narration.mp3"

    # simple (non-streaming) create -> write file
    resp = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
    )

    with open(out_path, "wb") as f:
        f.write(resp.content)

    # macOS: open the file in default player
    subprocess.run(["open", out_path], check=False)
    print(f"wrote and opened {out_path}")

if __name__ == "__main__":
    main()