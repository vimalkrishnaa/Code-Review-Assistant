from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv("config.env")

# Import routes
from routes.review import router as review_router
from routes.history import router as history_router

# Import database
from database.db import init_db

app = FastAPI(
    title="Code Review Assistant API",
    description="A web app that automatically reviews source code using an LLM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:5173",  # Alternative localhost
        "http://127.0.0.1:3000",  # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()

# Include routers
app.include_router(review_router)
app.include_router(history_router)

class PingResponse(BaseModel):
    message: str

@app.get("/ping", response_model=PingResponse)
async def ping():
    """Health check endpoint to verify server is running"""
    return PingResponse(message="Server running")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Code Review Assistant API", 
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/ping",
            "upload": "/api/upload",
            "upload_multiple": "/api/upload-multiple",
            "supported_formats": "/api/supported-formats",
            "review_health": "/api/health",
            "history": "/api/history",
            "history_stats": "/api/history/stats/summary"
        }
    }

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host=host, port=port, reload=True)
