"""
ATS Resume Scorer API
"""

import os
import sys
import threading
from pathlib import Path
from contextlib import asynccontextmanager

# Add parent directory to Python path to allow 'backend' imports
backend_dir = Path(__file__).parent
parent_dir = backend_dir.parent
sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _warmup_models():
    """
    Pre-warm the sentence-transformers model at server startup.

    Only runs when ENABLE_SEMANTIC_MATCHING=true.  On Render free tier (512 MB)
    the model uses ~90 MB at rest + up to 200 MB per encode() call, which
    combined with the Python process and DOCX-specific operations exceeds the
    memory limit.  Keyword matching falls back to exact string comparison by
    default, which is reliable and uses negligible memory.

    LanguageTool (JVM) is also excluded: it uses ~250 MB even after a timeout.
    """
    import os
    if os.getenv("ENABLE_SEMANTIC_MATCHING", "false").lower() != "true":
        logger.info("Semantic matching disabled (ENABLE_SEMANTIC_MATCHING not set) — skipping warmup")
        return

    logger.info("Starting background model warmup (sentence-transformers)...")
    try:
        from backend.services.semantic_matcher import get_semantic_matcher
        get_semantic_matcher()._lazy_init()
        logger.info("Semantic matcher warmed up")
    except Exception as e:
        logger.warning("Semantic matcher warmup failed: %s", e)
    logger.info("Background model warmup complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Kick off model warmup in a daemon thread so it doesn't block startup
    t = threading.Thread(target=_warmup_models, daemon=True, name="model-warmup")
    t.start()
    yield


app = FastAPI(
    title="ATS Resume Scorer API",
    description="API for scoring and analyzing resumes for ATS compatibility",
    version="1.0.0",
    lifespan=lifespan,
)

# Environment-aware CORS configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176").split(",")

if ENVIRONMENT == "production":
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization", "Accept", "Origin"]
else:
    allow_methods = ["*"]
    allow_headers = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)

# Import routers
from backend.api.upload import router as upload_router
from backend.api.score import router as score_router
from backend.api.auth import router as auth_router
from backend.api.resumes import router as resumes_router
from backend.api.ads import router as ads_router
from backend.api.roles import router as roles_router
from backend.api.export import router as export_router
from backend.api.preview import router as preview_router
from backend.api.editor import router as editor_router
from backend.api.files import router as files_router
from backend.api.latex_editor import router as latex_router
from backend.api.docx_editor import router as docx_editor_router
from backend.api.onlyoffice import router as onlyoffice_router
from backend.api.phase2_features import router as phase2_router

# Include routers
app.include_router(upload_router)
app.include_router(score_router)
app.include_router(auth_router)
app.include_router(resumes_router)
app.include_router(ads_router)
app.include_router(roles_router)
app.include_router(export_router)
app.include_router(preview_router)
app.include_router(editor_router)
app.include_router(files_router)
app.include_router(latex_router)
app.include_router(docx_editor_router)
app.include_router(onlyoffice_router)
app.include_router(phase2_router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "ATS Resume Scorer API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
