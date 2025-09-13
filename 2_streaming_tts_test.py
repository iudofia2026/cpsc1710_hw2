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
# 2_streaming_tts_test.py
# Goal: Use AsyncOpenAI and LocalAudioPlayer to play narration from a text file.
# If the SDK doesn't expose LocalAudioPlayer, we provide a minimal compatible shim
# that streams to an MP3 file and begins playback as data arrives.

import asyncio
import os
import threading
import time
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

# Try to import LocalAudioPlayer from known locations; otherwise define a shim.
LocalAudioPlayer = None
try:
    # Older helper path (some SDK builds)
    from openai.audio import LocalAudioPlayer as _LAP  # type: ignore
    LocalAudioPlayer = _LAP
except Exception:
    try:
        # Alternative helper path
        from openai.resources.audio.speech import LocalAudioPlayer as _LAP2  # type: ignore
        LocalAudioPlayer = _LAP2
    except Exception:
        LocalAudioPlayer = None


class ShimLocalAudioPlayer:
    """
    Minimal stand-in for LocalAudioPlayer:
    - Accepts a streaming response context and a target file path.
    - Starts a watcher thread that waits until the file has some data, then plays it with macOS 'afplay'.
    - This gives near-real-time playback while the file is still being written.
    """
    def __init__(self, min_start_bytes: int = 40_000):
        self.min_start_bytes = min_start_bytes

    async def stream_playback(self, response_ctx, out_path: str = "narration.mp3"):
        # Ensure parent dir exists
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)

        # Watcher to start afplay when enough bytes are present
        def _watch_and_play():
            # wait for file to appear and grow
            for _ in range(600):  # ~60s max (600 * 0.1)
                try:
                    if os.path.exists(out_path) and os.path.getsize(out_path) >= self.min_start_bytes:
                        # Use afplay for immediate playback (works well with partially-written MP3s)
                        try:
                            subprocess.Popen(["afplay", out_path])
                        except FileNotFoundError:
                            # fallback to 'open' which will launch default player
                            subprocess.Popen(["open", out_path])
                        return
                except Exception:
                    pass
                time.sleep(0.1)
            # if we never started, try to open whatever got written
            try:
                subprocess.Popen(["open", out_path])
            except Exception:
                pass

        watcher = threading.Thread(target=_watch_and_play, daemon=True)
        watcher.start()

        # The streaming response object writes bytes as they arrive:
        # NOTE: stream_to_file is synchronous; that's fine because the watcher
        # will kick off playback once the file has enough data.
        response_ctx.stream_to_file(out_path)

        # Give the watcher a moment if it hasn't fired yet
        await asyncio.sleep(0.2)


async def main():
    load_dotenv()
    client = AsyncOpenAI()

    # read the narration text
    with open("narration.txt", "r", encoding="utf-8") as f:
        text = f.read().strip()

    # choose a voice and output file
    voice = "alloy"
    out_path = "narration.mp3"

    # Decide on player: real LocalAudioPlayer if present, otherwise shim
    if LocalAudioPlayer is None:
        player = ShimLocalAudioPlayer()
    else:
        player = LocalAudioPlayer()

    # Create a streaming TTS response and play it
    # (Do not pass unsupported args like 'format')
    async with await client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
    ) as response:
        # If the official LocalAudioPlayer is available and supports stream_playback(response),
        # call it; otherwise use the shim which streams to a file and plays it as it grows.
        if hasattr(player, "stream_playback"):
            # Some helper implementations expect just the response, others need an out_path.
            try:
                await player.stream_playback(response)  # type: ignore
            except TypeError:
                await player.stream_playback(response, out_path=out_path)  # type: ignore
        else:
            # Fallback: ensure we produce audio even if helpers are missing
            shim = ShimLocalAudioPlayer()
            await shim.stream_playback(response, out_path=out_path)

    print("streamed narration to speakers")

if __name__ == "__main__":
    asyncio.run(main())