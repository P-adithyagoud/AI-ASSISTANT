import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VECTORIZE_API_KEY = os.getenv("VECTORIZE_API_KEY")
HINDSIGHT_URL = os.getenv("HINDSIGHT_URL")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found in environment variables. Set this in Vercel settings.")
