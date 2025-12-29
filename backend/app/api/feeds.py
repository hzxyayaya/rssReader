from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.feed import Feed as FeedModel
from app.models.user import User
from app.schemas.feed import Feed as FeedSchema, FeedCreate
from app.core.security import get_current_user
from app.services.rss_ingest import rss_ingest_service
from app.tasks.scheduler import vectorize_articles_by_ids

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
    except Exception as e:
        print(f"Error fetching feed: {e}")
    
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
    
    db.delete(feed)
    db.commit()
    return None
