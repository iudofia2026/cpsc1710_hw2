# CPSC 1710 — Homework 2
- Initialized repo on macOS
- Added .gitignore for env/ and .env
---
## Repo Setup Summary (Part 1.1)
I ran `git init` inside my project folder `CPSC1710_HW2` to turn it into a Git repository then manually created two files:
- `README.md` with a project title and environment setup log
- `.gitignore` to exclude unnecessary files (e.g., `.env`, `env/`, cache files)

### .gitignore (current required entries)
env/
pycache/
.DS_Store
.vscode/
.env

- 2.2: added `0_tts_test.sh`, generated `out.mp3`, committed + pushed
- 3.1: created venv (`python -m venv env`), installed deps, selected interpreter in VS Code, tested `load_dotenv()` and confirmed API key loaded
- 3.2: wrote `1_tts_test.py` that saves `python_out.mp3` from OpenAI TTS and ran it successfully

---

## Activity Log
- 2025-09-11
  - Added `0_tts_test.sh` and tested OpenAI TTS output (`out.mp3`).
- 2025-09-13
  - Made local Python venv, installed packages, verified `.env` loading worked (`dotenv_loaded: True`, `OPENAI_API_KEY set: True`).
  - Created `1_tts_test.py`, ran it, and got `python_out.mp3` saying “hello from python version of the folder.”