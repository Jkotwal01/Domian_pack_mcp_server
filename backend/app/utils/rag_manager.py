"""RAG Management utility for PDF indexing and retrieval."""
import os
import tempfile
import requests
from typing import Dict, Any, Optional, List
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain.tools import tool
from app.config import settings
from app.utils.llm_factory import get_llm

# -------------------
# 1. LLM + embeddings
# -------------------
# Using settings from app.config
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", 
    api_key=settings.OPENAI_API_KEY
)

# -------------------
# 2. PDF retriever store (per thread/session)
# -------------------
# Map to store retrievers and metadata in memory
_THREAD_RETRIEVERS: Dict[str, Any] = {}
_THREAD_METADATA: Dict[str, dict] = {}


def _get_retriever(thread_id: Optional[str]):
    """Fetch the retriever for a thread if available."""
    if thread_id and thread_id in _THREAD_RETRIEVERS:
        return _THREAD_RETRIEVERS[thread_id]
    return None


def ingest_pdf(file_bytes: bytes, thread_id: str, filename: Optional[str] = None) -> dict:
    """
    Build a FAISS retriever for the uploaded PDF and store it for the thread.
    Returns a summary dict.
    """
    if not file_bytes:
        raise ValueError("No bytes received for ingestion.")

    # Create a temporary file to save the PDF bytes for PyPDFLoader
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200, 
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(docs)

        # Create FAISS vector store from chunks
        vector_store = FAISS.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 4}
        )

        # Store for the session
        thread_id_str = str(thread_id)
        _THREAD_RETRIEVERS[thread_id_str] = retriever
        _THREAD_METADATA[thread_id_str] = {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }

        return _THREAD_METADATA[thread_id_str]
    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except OSError:
            pass


# -------------------
# 3. Tools
# -------------------
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def rag_tool(query: str, thread_id: Optional[str] = None) -> dict:
    """
    Retrieve relevant information from the uploaded PDF for this chat thread.
    Always include the thread_id when calling this tool.
    """
    retriever = _get_retriever(thread_id)
    if retriever is None:
        return {
            "error": "No document indexed for this chat. Upload a PDF first.",
            "query": query,
        }

    result = retriever.invoke(query)
    context = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        "query": query,
        "context": context,
        "metadata": metadata,
        "source_file": _THREAD_METADATA.get(str(thread_id), {}).get("filename"),
    }


def get_rag_tools(thread_id: str):
    """Get a list of tools including the thread-specific rag_tool."""
    # We create a partial tool or a wrapper that injects thread_id implicitly for nodes
    return [rag_tool]
