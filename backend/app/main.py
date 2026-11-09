"""
Main FastAPI Application Entrypoint.
Coordinates API routing, static file mounting, security middleware, and global error handling.
"""
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api.v1 import detect, history, feedback, model_info
from backend.app.ml.model import default_model_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup validation
    print(f"[{settings.APP_NAME}] Starting up. Model status: loaded={default_model_service.is_loaded}")
    yield
    # Clean shutdown
    print(f"[{settings.APP_NAME}] Shutting down gracefully.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Privacy-Conscious AI Scam and Phishing Detection Backend with Selective Two-Stage Architecture.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Security & Sanitized Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[SECURITY ALERT] Unhandled exception on {request.url.path}: {exc}")
    # Never expose internal stack traces or internal variable states to the client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Processing Error",
            "message": "An error occurred while evaluating the request. No sensitive data was exposed.",
            "request_path": str(request.url.path),
        }
    )


# Health Check Endpoints
@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "model_loaded": default_model_service.is_loaded,
        "model_version": default_model_service.model_version,
    }


# Include versioned API routers
app.include_router(detect.router, prefix=settings.API_V1_PREFIX, tags=["Detection"])
app.include_router(history.router, prefix=settings.API_V1_PREFIX, tags=["History"])
app.include_router(feedback.router, prefix=settings.API_V1_PREFIX, tags=["Feedback"])
app.include_router(model_info.router, prefix=settings.API_V1_PREFIX, tags=["Model Info"])

# Static files for the responsive Web Application
WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "web")
if os.path.exists(WEB_DIR):
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

    @app.get("/", tags=["Web App"])
    async def serve_index():
        index_file = os.path.join(WEB_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(
                index_file,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )
        return {"message": f"ScamGuard API is running. Visit /docs for OpenAPI specifications."}

    @app.get("/download-apk", tags=["Mobile App"])
    async def download_apk():
        apk_path = os.path.join(WEB_DIR, "ScamGuard.apk")
        if os.path.exists(apk_path):
            return FileResponse(
                apk_path,
                media_type="application/vnd.android.package-archive",
                filename="ScamGuard.apk"
            )
        return JSONResponse(status_code=404, content={"message": "APK file not found."})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
