# 3_multi_voice_effects.py
# Multi-voice TTS runner with simple "effects" via style/speed prompts.
# Modes:
#   --save  : write MP3 files
#   --stream: write MP3 then auto-open (macOS)
#
# Effects are prompt-based (style, speed) so no extra DSP libs are needed.

import argparse
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

DEFAULT_VOICES = ["alloy", "verse", "aria"]

def build_effective_text(raw_text: str, style: str, speed: str) -> str:
    style_map = {
        "neutral": "Read in a clear, neutral studio voice.",
        "news": "Read like a concise news anchor, confident and authoritative.",
        "whisper": "Read softly, with a hushed, intimate tone.",
        "dramatic": "Read with dramatic pacing and emphasis, cinematic style.",
    }
    speed_map = {
        "slow": "Keep a measured, slower pace with clear pauses.",
        "normal": "Use a natural, conversational pace.",
        "fast": "Use a quicker pace while staying intelligible.",
    }
    parts = [style_map.get(style, ""), speed_map.get(speed, "")]
    prefix = " ".join([p for p in parts if p]).strip()
    if prefix:
        return f"{prefix}\n\n{raw_text}"
    return raw_text

def save_mp3(client: OpenAI, voice: str, text: str, out_path: Path) -> None:
    resp = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(resp.content)

def stream_to_mp3_and_open(client: OpenAI, voice: str, text: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
    ) as resp:
        resp.stream_to_file(str(out_path))
    subprocess.Popen(["open", str(out_path)])

def main():
    load_dotenv()
    client = OpenAI()

    parser = argparse.ArgumentParser(description="Multi-voice OpenAI TTS with simple effects.")
    parser.add_argument("--text", type=str, help="Inline text to speak.")
    parser.add_argument("--text-file", type=str, help="Path to a .txt file to read.")
    parser.add_argument("--voices", type=str, default=",".join(DEFAULT_VOICES),
                        help="Comma-separated voices (default: alloy,verse,aria)")
    parser.add_argument("--mode", choices=["save", "stream"], default="save",
                        help="save = write files only; stream = write and auto-open")
    parser.add_argument("--style", choices=["neutral", "news", "whisper", "dramatic"], default="neutral",
                        help="delivery style effect")
    parser.add_argument("--speed", choices=["slow", "normal", "fast"], default="normal",
                        help="pace effect")
    parser.add_argument("--outdir", type=str, default="voices_out", help="output directory")
    parser.add_argument("--basename", type=str, default="take", help="base filename")
    args = parser.parse_args()

    if not args.text and not args.text_file:
        raise SystemExit("Provide --text or --text-file")

    raw_text = args.text
    if args.text_file:
        raw_text = Path(args.text_file).read_text(encoding="utf-8").strip()

    effective_text = build_effective_text(raw_text, args.style, args.speed)
    voices = [v.strip() for v in args.voices.split(",") if v.strip()]
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Voices: {voices}")
    print(f"Mode: {args.mode} | Style: {args.style} | Speed: {args.speed}")
    for i, voice in enumerate(voices, start=1):
        out_path = outdir / f"{args.basename}_{i:02d}_{voice}.mp3"
        print(f"- {voice} -> {out_path.name}")
        try:
            if args.mode == "save":
                save_mp3(client, voice, effective_text, out_path)
            else:
                stream_to_mp3_and_open(client, voice, effective_text, out_path)
        except Exception as e:
            print(f"  ! Skipped {voice} due to error: {e}")
    print("Done.")

if __name__ == "__main__":
    main()
