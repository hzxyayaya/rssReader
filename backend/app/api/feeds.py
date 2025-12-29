from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.feed import Feed as FeedModel
from app.models.user import User
from app.schemas.feed import Feed as FeedSchema, FeedCreate
from app.core.security import get_current_user
from app.services.rss_ingest import rss_ingest_service
import threading
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

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
    try:
        rss_ingest_service.process_feed(db, db_feed.id, db_feed.url)
        
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
    
    db.delete(feed)
    db.commit()
    return None
