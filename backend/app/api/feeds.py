from typing import List
import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.feed import Feed as FeedModel
from app.models.article import Article as ArticleModel
from app.models.user_article import UserArticle
from app.models.message import ChatSession, Message
from app.vector.milvus import milvus_service
from app.models.user import User
from app.schemas.feed import Feed as FeedSchema, FeedCreate
from app.core.security import get_current_user
from app.services.rss_ingest import rss_ingest_service
import threading
import logging

logger = logging.getLogger(__name__)
from app.tasks.scheduler import vectorize_articles_by_ids

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[FeedSchema])
def read_feeds(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    feeds = db.query(FeedModel).filter(FeedModel.user_id == current_user.id).offset(skip).limit(limit).all()
    return feeds

@router.post("/", response_model=FeedSchema)
def create_feed(
    feed: FeedCreate, 
    db: Session = Depends(get_db), 
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user)
):
    # Check if exists for user
    existing = db.query(FeedModel).filter(FeedModel.user_id == current_user.id, FeedModel.url == feed.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Feed already subscribed")
    
    db_feed = FeedModel(
        title=feed.title,
        url=feed.url,
        description=feed.description,
        icon=feed.icon,
        user_id=current_user.id
    )
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    
    # Trigger initial fetch (sync for now, better async)
    new_articles = []
    try:
        new_articles = rss_ingest_service.process_feed(db, db_feed.id, db_feed.url)
        
        # Trigger vectorization in background thread
        def vectorize_new_articles():
            from app.db.session import SessionLocal
            from app.tasks.scheduler import process_vectorization
            db_session = SessionLocal()
            try:
                logger.info(f"Starting vectorization for feed {db_feed.id}...")
                process_vectorization(db_session)
                logger.info(f"Vectorization completed for feed {db_feed.id}")
            except Exception as e:
                logger.error(f"Error vectorizing articles: {e}")
            finally:
                db_session.close()
        
        threading.Thread(target=vectorize_new_articles, daemon=True).start()
        
    except Exception as e:
        logger.error(f"Error fetching feed: {e}")
    
    if new_articles:
        article_ids = [article.id for article in new_articles if article.id is not None]
        if article_ids:
            if background_tasks:
                background_tasks.add_task(vectorize_articles_by_ids, article_ids)
            else:
                vectorize_articles_by_ids(article_ids)
        
    return db_feed

@router.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feed(
    feed_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    feed = db.query(FeedModel).filter(FeedModel.id == feed_id, FeedModel.user_id == current_user.id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    try:
        article_ids = [
            row[0] for row in db.query(ArticleModel.id)
            .filter(ArticleModel.feed_id == feed_id)
            .all()
        ]

        if article_ids:
            session_ids = [
                row[0] for row in db.query(ChatSession.id)
                .filter(ChatSession.article_id.in_(article_ids))
                .all()
            ]

            if session_ids:
                db.query(Message).filter(Message.session_id.in_(session_ids)).delete(synchronize_session=False)
                db.query(ChatSession).filter(ChatSession.id.in_(session_ids)).delete(synchronize_session=False)

            db.query(UserArticle).filter(UserArticle.article_id.in_(article_ids)).delete(synchronize_session=False)
            deleted_vectors = milvus_service.delete_by_article_ids(article_ids)
            if deleted_vectors == 0:
                logger.warning("No vectors deleted for feed_id=%s", feed_id)
            db.query(ArticleModel).filter(ArticleModel.id.in_(article_ids)).delete(synchronize_session=False)

        db.delete(feed)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete feed")
    return None
