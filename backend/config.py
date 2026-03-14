import os
from dotenv import load_dotenv

# Load environment variables from the .env file located in the root directory
load_dotenv()

class Settings:
    """Centralized configuration management."""
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "career-guidance")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-base-en-v1.5")
    
    @classmethod
    def validate_keys(cls):
        """Validate that all required API keys are present."""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in the environment variables.")
        if not cls.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is not set in the environment variables.")
            
settings = Settings()
