import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env')

print(dotenv_path)

load_dotenv(dotenv_path=dotenv_path)

# API keys
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
HUGGING_FACE_ACCESS_TOKENS = ""
HUGGING_FACE_API_URL = os.getenv("HUGGING_FACE_API_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")