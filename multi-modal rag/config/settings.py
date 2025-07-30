import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Configuration settings for the multi-modal RAG application."""
    
    def __init__(self):
        self.setup_environment()
    
    def setup_environment(self):
        """Set up environment variables for API keys and configurations."""
        # API Keys - Load from environment variables or use defaults
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.groq_api_key: str = os.getenv("GROQ_API_KEY", "")
        self.langchain_api_key: str = os.getenv("LANGCHAIN_API_KEY", "")
        
        # Validate required API keys
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        # Set environment variables for libraries
        os.environ["OPENAI_API_KEY"] = self.openai_api_key
        os.environ["GROQ_API_KEY"] = self.groq_api_key
        if self.langchain_api_key:
            os.environ["LANGCHAIN_API_KEY"] = self.langchain_api_key
            os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
    
    # File paths
    content_path: str = os.getenv("CONTENT_PATH", "./content/")
    pdf_filename: str = os.getenv("PDF_FILENAME", "attention.pdf")
    
    @property
    def pdf_path(self) -> str:
        return os.path.join(self.content_path, self.pdf_filename)
    
    # PDF processing settings
    max_characters: int = int(os.getenv("MAX_CHARACTERS", "10000"))
    combine_text_under_n_chars: int = int(os.getenv("COMBINE_TEXT_UNDER_N_CHARS", "2000"))
    new_after_n_chars: int = int(os.getenv("NEW_AFTER_N_CHARS", "6000"))
    
    # Model settings
    text_model: str = os.getenv("TEXT_MODEL", "llama-3.1-8b-instant")
    image_model: str = os.getenv("IMAGE_MODEL", "gpt-4o-mini")
    temperature: float = float(os.getenv("TEMPERATURE", "0.5"))
    max_concurrency: int = int(os.getenv("MAX_CONCURRENCY", "3"))
    
    # Vectorstore settings
    collection_name: str = os.getenv("COLLECTION_NAME", "multi_modal_rag")


# Global settings instance
settings = Settings()