from dotenv import load_dotenv
import os

loaded = load_dotenv()
print("dotenv_loaded:", loaded)
print("OPENAI_API_KEY set:", bool(os.getenv("OPENAI_API_KEY")))