import feedparser
from sqlalchemy.orm import Session
from app.models.feed import Feed
from app.models.article import Article
from datetime import datetime
import hashlib

class RssIngestService:
    def fetch_feed(self, url: str):
        return feedparser.parse(url)

    def process_feed(self, db: Session, feed_id: int, feed_url: str):
        parsed = self.fetch_feed(feed_url)
        feed = db.query(Feed).filter(Feed.id == feed_id).first()
        
        if not feed:
            return

        # Update feed info if needed
        if not feed.title and parsed.feed.get('title'):
            feed.title = parsed.feed.title
        if not feed.description and parsed.feed.get('description'):
            feed.description = parsed.feed.description

        new_articles = []
        for entry in parsed.entries:
            # Generate hash for deduplication
            content_hash = hashlib.md5((entry.link + (entry.get('title') or '')).encode()).hexdigest()
            
            # Check if exists
            exists = db.query(Article).filter(Article.content_hash == content_hash).first()
            if exists:
                continue

            # Parse date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            else:
                published_at = datetime.utcnow()

            # Description fallback
            description = entry.get('summary') or entry.get('description') or ''
            
            # Content fallback
            content = ''
            if hasattr(entry, 'content'):
                content = entry.content[0].value
            else:
                content = description

            article = Article(
                feed_id=feed_id,
                title=entry.get('title', 'No Title'),
                url=entry.link,
                content=content,
                description=description,
                author=entry.get('author'),
                published_at=published_at,
                content_hash=content_hash,
                is_vectorized=False
            )
            db.add(article)
            new_articles.append(article)
        
        db.commit()
        return new_articles

rss_ingest_service = RssIngestService()
