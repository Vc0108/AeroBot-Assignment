import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def configure_rag(uploaded_file):
    # --- WINDOWS SAFE FILE HANDLING ---
    # Create a temporary file to save the uploaded content
    # delete=False is crucial for Windows
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    # ----------------------------------

    try:
        print(f"DEBUG: Processing temp file at {tmp_path}")
        
        # 1. Load PDF
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        print(f"DEBUG: Found {len(docs)} pages.")
        
        # 2. Split Text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # 3. Create Embeddings
        print("DEBUG: Loading Embeddings Model...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 4. Create Vector Store
        print("DEBUG: Building Vector Store...")
        vectorstore = FAISS.from_documents(splits, embeddings)
        print("DEBUG: Success! Brain created.")
        
        return vectorstore

    except Exception as e:
        print(f"CRITICAL ERROR in RAG: {e}")
        return None
        
    finally:
        # Cleanup: Delete the temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)