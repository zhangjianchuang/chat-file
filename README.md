# Chat-File Agent

This project is a file analysis agent that allows users to upload documents and chat with an AI model about the content.

## Architecture

The application follows a decoupled client-server architecture:

- **Backend (FastAPI):** Handles file processing, vector storage, and LLM interaction.
- **Frontend (Streamlit):** Provides the user interface for file uploads and the chat experience.

## Tech Stack

- **Language:** Python 3.10+
- **Backend:** FastAPI, Uvicorn
- **Frontend:** Streamlit
- **LLM/Orchestration:** LangChain (suggested for RAG implementation), OpenAI API (or compatible local models)
- **Vector Store:** ChromaDB or FAISS (for local development)

## Project Structure

```
chat-file/
├── backend/            # FastAPI application
│   ├── main.py         # Entry point
│   ├── api/            # API routes (upload, chat)
│   ├── core/           # Configuration and LLM logic
│   └── services/       # File parsing and RAG pipeline
├── frontend/           # Streamlit application
│   ├── app.py          # Main UI entry point
│   └── api_client.py   # Client to communicate with FastAPI
├── data/               # Local storage for uploaded files/databases
├── requirements.txt    # Project dependencies
└── README.md
```

## Features

1.  **File Upload:** Support for PDF, TXT, MD files.
2.  **Indexing:** Parse and embed document content for retrieval.
3.  **Chat Interface:** Conversational UI to query the document.
4.  **Source Attribution:** Show which part of the document the answer is based on.

## Getting Started

*(Instructions to be added during implementation)*
