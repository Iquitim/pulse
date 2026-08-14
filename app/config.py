import os
from dotenv import load_dotenv

# Path to the root-level .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE)

PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "127.0.0.1")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
BSKY_HANDLE = os.getenv("BSKY_HANDLE")
BSKY_APP_PASSWORD = os.getenv("BSKY_APP_PASSWORD")

# Configurações de Instância Open-Source / Self-Hosted
ALLOW_PUBLIC_REGISTRATION = os.getenv("ALLOW_PUBLIC_REGISTRATION", "True").lower() == "true"
REQUIRE_INVITE_CODE = os.getenv("REQUIRE_INVITE_CODE", "False").lower() == "true"

# Twitter / X OAuth 2.0
TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")
TWITTER_REDIRECT_URI = os.getenv("TWITTER_REDIRECT_URI")

# Meta Threads OAuth 2.0
THREADS_APP_ID = os.getenv("THREADS_APP_ID")
THREADS_APP_SECRET = os.getenv("THREADS_APP_SECRET")
THREADS_REDIRECT_URI = os.getenv("THREADS_REDIRECT_URI")

