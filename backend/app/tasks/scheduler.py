from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.feed import Feed
from app.models.article import Article
from app.services.rss_ingest import rss_ingest_service
from app.services.embedder import embedder_service

from app.vector.milvus import milvus_service
from app.services.rag import rag_service
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_and_process_feeds():
    logger.info("Starting feed fetch...")
    db: Session = SessionLocal()
    try:
        feeds = db.query(Feed).all()
        for feed in feeds:
            try:
                rss_ingest_service.process_feed(db, feed.id, feed.url)
            except Exception as e:
                logger.error(f"Error processing feed {feed.url}: {e}")
                
        # After fetching, process vectorization for new articles
        process_vectorization(db)
        
    finally:
        db.close()
    logger.info("Feed fetch completed.")

def _vectorize_articles(db: Session, articles: list[Article]) -> int:
    processed_count = 0
    for article in articles:
        try:
            # Split text
            text_to_embed = f"{article.title}\n\n{article.description}\n\n{article.content}"
            chunks = rag_service.split_text(text_to_embed)

            vectors = []
            attributes = []

            for chunk in chunks:
                vec = embedder_service.embed_text(chunk)
                if vec:
                    vectors.append(vec)
                    attributes.append({
                        "article_id": article.id,
                        "chunk_content": chunk
                    })

            if vectors:
                milvus_service.insert_vectors(vectors, attributes)

            article.is_vectorized = True
            db.commit() # Commit per article to save progress
            processed_count += 1

        except Exception as e:
            logger.error(f"Error vectorizing article {article.id}: {e}")
            db.rollback()
    return processed_count

def process_vectorization(db: Session) -> int:
    logger.info("Starting vectorization...")
    # Batch size 10 to avoid overload
    articles = db.query(Article).filter(Article.is_vectorized == False).limit(50).all()
    return _vectorize_articles(db, articles)

def vectorize_articles_by_ids(article_ids: list[int]) -> int:
    if not article_ids:
        return 0
    db: Session = SessionLocal()
    try:
        articles = db.query(Article).filter(
            Article.id.in_(article_ids),
            Article.is_vectorized == False
        ).all()
        return _vectorize_articles(db, articles)
    finally:
        db.close()

scheduler = BackgroundScheduler()
# Run every 30 minutes
scheduler.add_job(fetch_and_process_feeds, 'interval', minutes=30)

def start_scheduler():
    scheduler.start()
    # Run immediately on startup to vectorize any pending articles
    import threading
    threading.Thread(target=fetch_and_process_feeds, daemon=True).start()

