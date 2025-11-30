import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def test_rag():
    pdf_path = "flight_policy.pdf"
    
    # Check 1: File Exists
    if not os.path.exists(pdf_path):
        print("❌ ERROR: flight_policy.pdf not found in this folder!")
        return

    print("✅ Step 1: Found PDF.")

    # Check 2: Load PDF
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        print(f"✅ Step 2: Loaded {len(docs)} pages.")
    except Exception as e:
        print(f"❌ ERROR Loading PDF: {e}")
        return

    # Check 3: Embeddings (The likely culprit)
    print("⏳ Step 3: Initializing Embeddings (This downloads a model)...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print("✅ Step 3: Embeddings Model Ready.")
    except Exception as e:
        print(f"❌ ERROR Downloading Model: {e}")
        print("💡 Solution: Run 'pip install sentence-transformers' again.")
        return

    # Check 4: Vector Store
    print("⏳ Step 4: Creating Vector Store...")
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        vectorstore = FAISS.from_documents(splits, embeddings)
        print("✅ Step 4: Brain Created Successfully!")
        
        # Test Search
        retriever = vectorstore.as_retriever()
        result = retriever.invoke("price discovery flight")
        print(f"\n🎉 SUCCESS! Retrieved Answer snippet: {result[0].page_content[:100]}...")
        
    except Exception as e:
        print(f"❌ ERROR Creating Brain: {e}")

if __name__ == "__main__":
    test_rag()