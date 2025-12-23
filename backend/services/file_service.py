import os
import shutil
import logging
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

logger = logging.getLogger("app")

CHROMA_PATH = "data/chroma_db"
DATA_PATH = "data/uploads"

# Global variable to hold the initialized embedding model
_embeddings_instance = None

def initialize_embeddings():
    """Initialize the embedding model. Should be called at app startup."""
    global _embeddings_instance
    if _embeddings_instance is not None:
        logger.info("Embedding model is already initialized.")
        return

    logger.info("⏳ Initializing Embedding Model (all-MiniLM-L6-v2)... This may take a moment.")
    try:
        # Initialize the model (downloads if not present)
        _embeddings_instance = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        logger.info("✅ Embedding Model initialized successfully.")
    except Exception as e:
        logger.critical(f"❌ Failed to initialize Embedding Model: {e}")
        raise e

def get_embeddings():
    """Get the initialized embedding model instance."""
    if _embeddings_instance is None:
        raise RuntimeError("Embedding model is not initialized. Call initialize_embeddings() during startup.")
    return _embeddings_instance

def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file to disk and return the path."""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    
    file_path = os.path.join(DATA_PATH, upload_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path

def load_and_split_document(file_path: str):
    """Load document based on extension and split into chunks."""
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        # Default to text loader for .txt, .md, etc.
        loader = TextLoader(file_path, encoding="utf-8")
    
    docs = loader.load()
    
    # Split text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(docs)
    return chunks

def index_document(file_path: str):
    """Full pipeline: Load -> Split -> Embed -> Store in Chroma."""
    
    # Skip vector indexing for Excel/CSV (Structured Data)
    if file_path.endswith((".xlsx", ".xls", ".csv")):
        return 0

    chunks = load_and_split_document(file_path)
    
    # Store in ChromaDB
    Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=CHROMA_PATH
    )
    return len(chunks)

def get_retriever():
    """Return a retriever connected to the vector store."""
    if not os.path.exists(CHROMA_PATH):
        return None
        
    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embeddings()
    )
    # Search for top 5 most relevant chunks
    return vector_store.as_retriever(search_kwargs={"k": 5})