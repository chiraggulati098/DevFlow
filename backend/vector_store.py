import chromadb
from sentence_transformers import SentenceTransformer
import os

chroma_client = chromadb.PersistentClient(path="./chromadb_store")
collection = chroma_client.get_or_create_collection(name="docs")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def add_pdf_to_chromadb(pdf_path):
    '''
    Extracts text from PDF, generates embeddings, and stores it in chromaDB with metadata
    '''
    from backend.pdf_processor import process_and_store_pdf

    paragraphs = process_and_store_pdf(pdf_path)
    embeddings = embedding_model.encode(paragraphs).tolist()
    doc_name = os.path.basename(pdf_path)

    for i, paragraph in enumerate(paragraphs):
        collection.add(
            ids = [f"{doc_name}_{i}"],
            documents = [paragraph],
            embeddings = [embeddings[i]],
            metadatas = [{"source": doc_name}]
        )
    
    print(f"{doc_name} added to ChromaDB")

def query_chromadb(query, top_k = 3):
    '''
    Retrieves most relevant paragraphs for a given query
    '''
    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(
        query_texts=[query], n_results=top_k, include=["documents", "metadatas", "distances"]
    )

    documents = results["documents"][0] 
    metadatas = results["metadatas"][0]

    return list(zip(documents, metadatas))