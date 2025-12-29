from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.session import get_db
from app.schemas.qa import AskRequest, AnswerResponse
from app.services.rag import rag_service
from app.models.message import ChatSession, Message
from app.models.article import Article
from app.models.feed import Feed
from app.core.security import get_current_user
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def resolve_article_ids(db: Session, user_id: int, request: AskRequest) -> list[int]:
    """
    Resolve filter parameters to a list of article IDs.
    Returns empty list if no filters (search all), or list of specific IDs.
    """
    article_ids = []
    
    # 1. Add explicit article_id (legacy single article)
    if request.article_id:
        article_ids.append(request.article_id)
    
    # 2. Add explicit article_ids
    if request.article_ids:
        article_ids.extend(request.article_ids)
    
    # 3. Resolve feed_ids to article IDs
    if request.feed_ids:
        feed_articles = db.query(Article.id).filter(
            Article.feed_id.in_(request.feed_ids),
            Article.is_vectorized == True
        ).all()
        article_ids.extend([a[0] for a in feed_articles])
    
    # 4. Resolve date_filter to article IDs
    if request.date_filter:
        now = datetime.utcnow()
        cutoff = None
        
        if request.date_filter == "today":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif request.date_filter == "yesterday":
            cutoff = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif request.date_filter == "week":
            cutoff = now - timedelta(days=7)
        
        if cutoff:
            date_articles = db.query(Article.id).filter(
                Article.published_at >= cutoff,
                Article.is_vectorized == True
            ).all()
            logger.info(f"Date filter '{request.date_filter}': cutoff={cutoff}, found {len(date_articles)} articles")
            article_ids.extend([a[0] for a in date_articles])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_ids = []
    for id in article_ids:
        if id not in seen:
            seen.add(id)
            unique_ids.append(id)
    
    logger.info(f"Resolved {len(unique_ids)} article IDs: {unique_ids[:10]}{'...' if len(unique_ids) > 10 else ''}")
    return unique_ids

@router.post("/ask", response_model=AnswerResponse)
def ask_question(
    request: AskRequest, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 1. Get or Create Session
    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        new_session = ChatSession(
            id=session_id, 
            user_id=current_user.id,
            article_id=request.article_id,
            title=request.question[:50]
        )
        db.add(new_session)
        db.commit()
    else:
        # Verify session ownership
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id, 
            ChatSession.user_id == current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

    # 2. Save User Message
    user_msg = Message(session_id=session_id, role="user", content=request.question)
    db.add(user_msg)
    db.commit()
    
    # 3. Resolve filters to article IDs
    article_ids = resolve_article_ids(db, current_user.id, request)
    
    # 4. Retrieve Context and Generate Answer
    contexts = rag_service.retrieve_context(request.question, article_ids if article_ids else None)
    answer_text = rag_service.answer_question(request.question, contexts)
    
    # 5. Save AI Message with citations
    citation_data = [{"text": c[:100] + "..." if len(c) > 100 else c} for c in contexts]
    
    ai_msg = Message(
        session_id=session_id, 
        role="ai", 
        content=answer_text,
        citations=citation_data
    )
    db.add(ai_msg)
    db.commit()
    
    return AnswerResponse(
        answer=answer_text,
        session_id=session_id,
        citations=citation_data
    )

