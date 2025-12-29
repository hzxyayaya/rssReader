import logging
from google import genai
from app.core.config import settings
from app.services.embedder import embedder_service
from app.vector.milvus import milvus_service
from app.db.session import SessionLocal
from app.models.article import Article

logger = logging.getLogger(__name__)

class RagService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = 'gemini-2.0-flash-exp' # Using newer flash model

    def split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200):
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += (chunk_size - overlap)
        return chunks

    def retrieve_context(self, question: str, article_ids: list[int] = None):
        """
        Retrieve relevant context chunks from Milvus.
        
        Args:
            question: The user's question
            article_ids: List of article IDs to filter by (None = search all)
        """
        # 1. Embed query
        query_vector = embedder_service.embed_query(question)
        if not query_vector:
            logger.warning("Failed to embed query")
            return []

        # 2. Build filter expression
        expr = None
        if article_ids and len(article_ids) > 0:
            if len(article_ids) == 1:
                expr = f"article_id == {article_ids[0]}"
            else:
                ids_str = ", ".join(str(id) for id in article_ids)
                expr = f"article_id in [{ids_str}]"
        
        logger.info(f"RAG search: article_ids={len(article_ids) if article_ids else 'all'}, expr={expr}")
        
        # 3. Search Milvus with higher top_k for better coverage
        # Single article: 5 chunks, Multi-article: 30 chunks
        top_k = 30 if (article_ids and len(article_ids) > 1) else 10
        
        results = milvus_service.search_vectors(
            query_vectors=[query_vector], 
            top_k=top_k,
            expr=expr
        )
        
        # 4. Format results with deduplication
        contexts = []
        seen = set()
        fallback_ids = set()
        if results:
            for hit in results[0]:
                entity = getattr(hit, "entity", None)
                content = entity.get("chunk_content") if entity else None
                article_id = entity.get("article_id") if entity else None
                if content and content not in seen:
                    contexts.append(content)
                    seen.add(content)
                    logger.debug(f"Found chunk from article {article_id}")
                elif article_id is not None:
                    fallback_ids.add(article_id)

        if fallback_ids and len(contexts) < top_k:
            remaining = top_k - len(contexts)
            contexts.extend(self._fallback_contexts_from_articles(list(fallback_ids), remaining))
        
        logger.info(f"RAG retrieved {len(contexts)} context chunks")
        return contexts

    def answer_question(self, question: str, context: list[str], history: list = []):
        context_str = "\n\n".join(context)
        
        prompt = f"""
        基于以下上下文回答问题。如果上下文不包含答案，请简单说明无法回答。
        
        上下文:
        {context_str}
        
        问题: {question}
        
        回答:
        """
        
        try:
             response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
             )
             return response.text
        except Exception as e:
            logger.error(f"Generate content failed: {e}")
            return "抱歉，AI 服务暂时不可用。"

    def _fallback_contexts_from_articles(self, article_ids: list[int], max_chunks: int) -> list[str]:
        if not article_ids or max_chunks <= 0:
            return []
        db = SessionLocal()
        try:
            articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
            contexts = []
            for article in articles:
                text_to_embed = f"{article.title}\n\n{article.description or ''}\n\n{article.content or ''}"
                chunks = self.split_text(text_to_embed)
                for chunk in chunks:
                    contexts.append(chunk)
                    if len(contexts) >= max_chunks:
                        return contexts
            return contexts
        finally:
            db.close()

rag_service = RagService()
