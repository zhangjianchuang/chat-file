import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from backend.services.file_service import save_upload_file, index_document
from backend.services.chat_service import ChatService
from backend.core.state import current_file

logger = logging.getLogger("app")
router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    logger.info(f"Received file upload request: {file.filename}")
    
    # 1. Save file locally
    try:
        file_path = save_upload_file(file)
        logger.info(f"File saved to: {file_path}")
        
        # 2. Determine type & Update State
        if file.filename.endswith((".xlsx", ".xls", ".csv")):
            current_file.file_type = "pandas"
            num_chunks = 0
            msg = "Uploaded for Data Analysis (Excel/CSV mode)."
            logger.info("Mode set to: Pandas/Data Analysis")
        else:
            current_file.file_type = "rag"
            # 3. Process and Index for RAG
            num_chunks = index_document(file_path)
            msg = f"Successfully indexed into {num_chunks} chunks."
            logger.info(f"Mode set to: RAG. Indexed {num_chunks} chunks.")
            
        current_file.path = file_path
        current_file.save() # Persist state
        
    
    return {
        "filename": file.filename, 
        "status": "success", 
        "chunks": num_chunks,
        "message": msg
    }

@router.get("/status")
def get_status():
    """Get the current file session state."""
    if current_file.path:
        filename = current_file.path.split("/")[-1] # Extract filename from path
        return {
            "active": True,
            "filename": filename,
            "type": current_file.file_type
        }
    return {"active": False}

@router.post("/chat")
def chat(request: ChatRequest):
    logger.info(f"Received chat request: {request.message[:50]}...") # Log first 50 chars only
    
    if not current_file.path:
        logger.warning("Chat attempted without uploaded file.")
        return {"response": "No file uploaded yet. Please upload a file first."}

    try:
        # --- MODE 1: PANDAS AGENT (Excel/CSV) ---
        if current_file.file_type == "pandas":
            logger.info("Routing to Pandas Agent")
            answer, steps = ChatService.run_pandas_agent(current_file.path, request.message)
            return {
                "response": answer,
                "steps": steps
            }

        # --- MODE 2: RAG (PDF/TXT) ---
        else:
            logger.info("Routing to RAG Chain")
            answer = ChatService.run_rag_chain(request.message)
            return {"response": answer}
            
    except Exception as e:
        logger.error(f"Error during chat generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
