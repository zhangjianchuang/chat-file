import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from backend.api.endpoints import router
from backend.core.exceptions import global_exception_handler, http_exception_handler
from backend.core.logging import setup_logging
from backend.services.file_service import initialize_embeddings
from backend.core.state import current_file

# 1. Setup Logging
setup_logging()
logger = logging.getLogger("app")

# 2. Define Lifespan (Startup/Shutdown logic)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("🚀 Application starting up...")
    try:
        # Initialize Embeddings
        initialize_embeddings()
        
        # Restore Session State
        current_file.load()
        
    except Exception as e:
        logger.error(f"Critical error during startup: {e}")
    
    yield
    
    # Shutdown logic
    logger.info("🛑 Application shutting down...")

app = FastAPI(title="Chat-File Agent Backend", lifespan=lifespan)

# 3. Register Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# 4. Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    
    logger.info(
        f"Path: {request.url.path} | Method: {request.method} | "
        f"Status: {response.status_code} | Duration: {formatted_process_time}ms"
    )
    
    return response

# 5. Include Routers
app.include_router(router)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"status": "ok", "service": "Chat-File Backend"}

if __name__ == "__main__":
    import uvicorn
    # Note: When running with uvicorn programmatically, logging config might be overridden by uvicorn's defaults
    # but our setup_logging() sets root logger handler, so it should be fine.
    uvicorn.run(app, host="0.0.0.0", port=8000)
