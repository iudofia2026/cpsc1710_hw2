#!/usr/bin/env bash
set -euo pipefail

# Load API key from .env
set -a
source .env
set +a

# Call OpenAI TTS and save MP3
curl -sS -X POST "https://api.openai.com/v1/audio/speech" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{
    "model": "gpt-4o-mini-tts",
    "voice": "alloy",
    "input": "Hello from CPSC 1710—testing text to speech!"
  }' --output out.mp3

echo "Wrote out.mp3"
