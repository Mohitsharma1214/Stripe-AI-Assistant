import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-2-9b-it:free")
    DB_PATH = os.path.join(os.getcwd(), "chroma_db")
    COLLECTION_NAME = "stripe_docs_v2"
    
    # RAG Settings
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 150
    
    # Security Settings
    DOMAIN_THRESHOLD = 0.5  # Cosine similarity threshold for domain relevance
    REJECTION_MESSAGE = "This query is outside the supported Stripe domain. I can only answer questions related to Stripe APIs and the provided documentation."
    INJECTION_MESSAGE = "Security Alert: A potential prompt injection attempt was detected. Your request has been blocked."

config = Config()
