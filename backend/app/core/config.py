import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
