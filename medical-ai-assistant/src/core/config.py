import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.collection_name = os.getenv("COLLECTION_NAME", "medical_documents")
        
        if not self.gemini_api_key:
            raise ValueError("Please set GEMINI_API_KEY in your .env file")

settings = Settings()

def get_settings():
    return settings 