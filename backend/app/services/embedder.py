from google import genai
from app.core.config import settings

class EmbedderService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = 'models/text-embedding-004' # Updated model name for better performance

    def embed_text(self, text: str) -> list[float]:
        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config={'output_dimensionality': 768}
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"Embedding failed: {e}")
            return []

    def embed_query(self, text: str) -> list[float]:
        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config={'output_dimensionality': 768}
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"Query embedding failed: {e}")
            return []

embedder_service = EmbedderService()
