import google.generativeai as genai
from .config import get_settings

class GeminiClient:
    def __init__(self):
        self.settings = get_settings()
        genai.configure(api_key=self.settings.gemini_api_key)
        self.model = genai.GenerativeModel(self.settings.gemini_model)
    
    def chat(self, query: str, system_prompt: str = None) -> str:
        if system_prompt:
            prompt = f"{system_prompt}\n\nUser: {query}\nAssistant:"
        else:
            prompt = query
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def get_medical_prompt(self) -> str:
        return """You are a AI Assistant for healthcare professionals. 
Provide accurate, evidence-based information based on the provided context. 
Always note that responses are for informational purposes only."""

_client = None

def get_gemini_client():
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client 