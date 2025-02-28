import chromadb
import google.generativeai as genai
import hashlib
import json
import os
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder

from backend.pdf_processor import process_pdf

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
persist_directory = os.path.join(os.getcwd(), "chroma_db")  # Store in a local directory

cross_encoder_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def generate_embeddings(text):
    '''
    Generate embedding using Gemini
    '''
    if not text.strip():
        print('Skipping empty chunk.')
        return None
    
    response = genai.embed_content(model="models/text-embedding-004", content=text)
    return response['embedding']

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path = persist_directory)
        self.collection = self.client.get_or_create_collection("devflow_docs")

    def add_document(self, pdf_path):
        '''
        Extract text fromm PDF, generate embeddings, and store in ChromaDB
        '''
        text_chunks = process_pdf(pdf_path)
        metadata = {"source": pdf_path}

        for idx, chunk in enumerate(text_chunks):
            chunk = chunk.strip()

            if not chunk:
                print(f"Skipping empty chunk {idx} from {pdf_path}")
                continue

            chunk_id = hashlib.md5((pdf_path + str(idx)).encode()).hexdigest()  # Unique ID per chunk
            embedding = generate_embeddings(chunk)

            print(f"Adding chunk {idx} out of {len(text_chunks)} from {pdf_path} with ID {chunk_id}")

            existing = self.collection.get(ids=[chunk_id])
            if existing and existing['ids']:
                print(f"Skipping existing chunk {idx} from {pdf_path}")
                continue 

            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[metadata]
            )
    
    def query(self, query_text, top_k = 10):
        '''
        Retrieve the most relevant chunks from ChromaDB based on query
        '''
        query_embedding = generate_embeddings(query_text)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)

        if not results or "documents" not in results or not results["documents"][0]:
            return []

        retrieved_chunks = results["documents"][0]

        # rerank using CrossEncoder
        rerank_scores = cross_encoder_model.predict([[query_text, chunk] for chunk in retrieved_chunks])
        reranked_results = sorted(zip(retrieved_chunks, rerank_scores), key=lambda x: x[1], reverse=True)
        
        return [chunk for chunk, _ in reranked_results]