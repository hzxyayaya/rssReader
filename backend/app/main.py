from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, Base
from contextlib import asynccontextmanager
# 导入所有 models 以便 create_all 能找到
from app.models import user, feed, article, message

# NOTE: avoid creating DB tables at import time (prevents failures when importing
# the module in environments where DB is unreachable or env vars are malformed).
# Create tables during FastAPI startup so we can handle and log errors safely.

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Logic
    import logging, re
    from app.core.config import settings
    logger = logging.getLogger("app.startup")

    def _mask_dsn(dsn: str) -> str:
        # mask credentials (basic) for safer logging
        try:
            return re.sub(r'://([^:/@]+):([^@]+)@', r'://\1:***@', dsn)
        except Exception:
            return repr(dsn)

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created or already exist.")
    except UnicodeDecodeError as e:
        logger.exception("UnicodeDecodeError while connecting to DB. Masked DSN: %s",
                         _mask_dsn(getattr(settings, 'SQLALCHEMY_DATABASE_URL', '')))
        raise
    except Exception:
        logger.exception("Failed to create DB tables. Masked DSN: %s",
                         _mask_dsn(getattr(settings, 'SQLALCHEMY_DATABASE_URL', '')))
        raise

    from app.tasks.scheduler import start_scheduler
    start_scheduler()
    
    yield
    # Shutdown Logic (if needed)

app = FastAPI(title="Intelligent RSS Reader API", version="1.0.0", lifespan=lifespan)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有，生产环境需指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Intelligent RSS Reader API"}

# 路由注册将在后续步骤添加
from app.api import auth, feeds, news, qa

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(feeds.router, prefix="/api/feeds", tags=["feeds"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(qa.router, prefix="/api/qa", tags=["qa"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8021, log_level="info", reload=True)
