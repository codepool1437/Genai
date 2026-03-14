import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

# Import our settings from config
from config import settings

# This script lives in backend/, so data/ is one level up
DATA_DIR = Path(__file__).parent.parent / "data"

def initialize_pinecone():
    """Initialize Pinecone client and ensure the index exists."""
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index_name = settings.PINECONE_INDEX_NAME
    
    # Check if index exists, if not create it serverless
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"Creating Pinecone index '{index_name}' for the first time...")
        pc.create_index(
            name=index_name,
            dimension=768, # Vector dimension for BGE-base-en-v1.5
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1" # Can be adjusted based on your Pinecone dashboard
            )
        )
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists.")
        
    return index_name

def ingest_data():
    """Load PDFs, chunk text, embed, and upsert to Pinecone."""
    # 1. Validate keys
    settings.validate_keys()
    
    # 2. Check for data directory
    if not DATA_DIR.exists() or not any(DATA_DIR.iterdir()):
        print(f"❌ No PDFs found in {DATA_DIR}.")
        print("Please add some career guide PDFs to the 'data' folder before running this script.")
        return

    # 3. Load Documents
    print("📥 Loading PDFs from 'data/' directory...")
    loader = PyPDFDirectoryLoader(str(DATA_DIR))
    documents = loader.load()
    
    if not documents:
        print("❌ No text could be extracted from the PDFs.")
        return

    # 4. Inject Metadata (Industry, Role, Skill Level)
    # We use simple heuristics based on the filename to tag the documents.
    # You can customize these rules based on your actual PDF file names!
    for doc in documents:
        source = doc.metadata.get('source', '')
        filename = os.path.basename(source).lower()
        
        # Default metadata
        doc.metadata["industry"] = "Technology"
        doc.metadata["skill_level"] = "All Levels"
        
        # Guess role based on filename keywords
        if 'data' in filename or 'machine' in filename or 'ai' in filename:
            doc.metadata["role"] = "Data Scientist / AI Engineer"
        elif 'software' in filename or 'develop' in filename:
            doc.metadata["role"] = "Software Engineer"
        elif 'product' in filename or 'manager' in filename:
            doc.metadata["role"] = "Product Manager"
        else:
            doc.metadata["role"] = "General Tech"

    # 5. Split Documents into Chunks
    print("✂️ Splitting documents into manageable chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} document pages.")

    # 6. Initialize Embedding Model
    print(f"🧠 Initializing Embedding Model ({settings.EMBEDDING_MODEL_NAME})...")
    # Setting device to CPU by default to prevent PyTorch/CUDA issues on local machines
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=settings.EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'}, 
        encode_kwargs={'normalize_embeddings': True}
    )

    # 7. Initialize Pinecone Environment
    index_name = initialize_pinecone()

    # 8. Upsert to Pinecone Vector DB
    print(f"🚀 Upserting vector embeddings to Pinecone index '{index_name}'...")
    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=index_name
    )
    
    print("✨ Ingestion complete! Knowledge base is ready.")

if __name__ == "__main__":
    ingest_data()
