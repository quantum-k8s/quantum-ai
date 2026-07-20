from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import Base, engine
from routers import auth, user_profile, education, experience, certification, dashboard, notification, interview, resume, jobs
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("career-ai")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down backend app...")

app = FastAPI(
    title="Career AI API",
    description="Production-grade FastAPI Backend for Career AI Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware Setup
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8081",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred.",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )

# Include Routers with exact root prefixes for absolute compatibility with frontend
app.include_router(auth.router, prefix="/api")
app.include_router(user_profile.router, prefix="/api")
app.include_router(education.router, prefix="/api")
app.include_router(experience.router, prefix="/api")
app.include_router(certification.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(notification.router, prefix="/api")
app.include_router(interview.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")

# Health Check Endpoint
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Career AI Platform"
    }

@app.get("/")
def home():
    return {
        "message": "Career AI Backend Running Successfully"
    }
