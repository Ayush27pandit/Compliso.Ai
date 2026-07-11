import os 
from dotenv import load_dotenv
 
load_dotenv()
class Settings:
    #---------------------------------Reasoning Engine---------------------------------#
        GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
        GROQ_MODEL: str= os.getenv("GROQ_MODEL")
        GROQ_FALLBACK_API_KEY: str = os.getenv("GROQ_FALLBACK_API_KEY")

    #---------------------------------Vector Database---------------------------------#
        QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
        QDRANT_CLUSTER_ENDPOINT: str = os.getenv("QDRANT_CLUSTER_ENDPOINT")
        QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION_NAME")

    #-------------------------------Gemini Embeddings API---------------------------------#
        GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

 