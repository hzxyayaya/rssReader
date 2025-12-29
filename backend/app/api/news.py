from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.models.article import Article as ArticleModel
from app.models.user_article import UserArticle
from app.schemas.article import Article, ArticleList
from app.core.security import get_current_user

router = APIRouter()

# Manual vectorization trigger - place BEFORE dynamic route
@router.post("/vectorize", status_code=status.HTTP_202_ACCEPTED)
def trigger_vectorization(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Manually trigger vectorization of pending articles"""
    from app.tasks.scheduler import fetch_and_process_feeds
    background_tasks.add_task(fetch_and_process_feeds)
    return {"message": "Vectorization started in background"}


@router.get("/", response_model=List[ArticleList])
def get_news(
    skip: int = 0, 
    limit: Optional[int] = None, 
    feed_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(ArticleModel)
    if feed_id:
        query = query.filter(ArticleModel.feed_id == feed_id)
    
    query = query.order_by(ArticleModel.published_at.desc()).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    articles = query.all()
    return articles

# IMPORTANT: This must come BEFORE /{article_id} to avoid route conflict
@router.get("/read-status", response_model=list[int])
def get_read_article_ids(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of article IDs that user has read"""
    read_articles = db.query(UserArticle.article_id).filter(
        UserArticle.user_id == current_user.id,
        UserArticle.is_read == True
    ).all()
    return [r[0] for r in read_articles]

@router.get("/{article_id}", response_model=Article)
def get_article(
    article_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.post("/{article_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_as_read(
    article_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_article = db.query(UserArticle).filter(
        UserArticle.user_id == current_user.id,
        UserArticle.article_id == article_id
    ).first()
    
    if user_article:
        if not user_article.is_read:
            user_article.is_read = True
            user_article.read_at = datetime.utcnow()
    else:
        user_article = UserArticle(
            user_id=current_user.id,
            article_id=article_id,
            is_read=True,
            read_at=datetime.utcnow()
        )
        db.add(user_article)
    
    db.commit()
    return None
