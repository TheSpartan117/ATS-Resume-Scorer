"""
ATS Resume Scorer API
"""

import os
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

app = FastAPI(
    title="ATS Resume Scorer API",
    description="API for scoring and analyzing resumes for ATS compatibility",
    version="1.0.0"
)

# Environment-aware CORS configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176").split(",")

if ENVIRONMENT == "production":
    allow_methods = ["GET", "POST", "PUT", "DELETE"]
    allow_headers = ["Content-Type", "Authorization"]
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
