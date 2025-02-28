import chromadb
import google.generativeai as genai
import hashlib
import json
import os
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder

from backend.pdf_processor import process_pdf
from backend.ai_model import summarize_query

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
    
    try:
        response = genai.embed_content(model="models/text-embedding-004", content=text)
        return response['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
    return None

def get_file_hash(file_path):
    '''
    Generate a hash of the file content to detect modifications.
    '''
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path = persist_directory)
        self.collection = self.client.get_or_create_collection("devflow_docs")

    def add_document(self, pdf_path):
        '''
        Extract text fromm PDF, generate embeddings, and store in ChromaDB
        '''
        file_hash = get_file_hash(pdf_path)
        text_chunks = process_pdf(pdf_path)
        metadata = {"source": pdf_path, "file_hash": file_hash}

        for idx, chunk in enumerate(text_chunks):
            chunk = chunk.strip()
            if not chunk:
                print(f"Skipping empty chunk {idx} from {pdf_path}")
                continue

            chunk_id = hashlib.md5((pdf_path + str(idx)).encode()).hexdigest()  # Unique ID per chunk
            embedding = generate_embeddings(chunk)

            if embedding is None:
                print(f"Failed to generate embedding for chunk {idx} from {pdf_path}")
                continue

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
        summarized_query = summarize_query(query_text)
        print(f"Original query: {query_text}")
        print(f"Summarized query: {summarized_query}")

        query_embedding = generate_embeddings(summarized_query)
        if query_embedding is None:
            return []
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)

        if not results or "documents" not in results or not results["documents"][0]:
            return []

        retrieved_chunks = results["documents"][0]
        rerank_scores = cross_encoder_model.predict([[query_text, chunk] for chunk in retrieved_chunks])
        reranked_results = sorted(zip(retrieved_chunks, rerank_scores), key=lambda x: x[1], reverse=True)
        
        return [chunk for chunk, _ in reranked_results]
    
    def remove_document(self, pdf_path):
        '''
        Remove all chunks associated with a PDF from ChromaDB
        '''
        all_entries = self.collection.get(include=["metadatas"])
        ids_to_remove = [entry[0] for entry in zip(all_entries["ids"], all_entries["metadatas"]) if entry[1] and entry[1].get("source") == pdf_path]

        if ids_to_remove:
            self.collection.delete(ids=ids_to_remove)
            print(f"Removed {len(ids_to_remove)} chunks for {pdf_path}")

    def sync_with_docs_directory(self, docs_dir = "./docs/"):
        '''
        Syncs ChromaDB with the docs directory: add new/modified files, remove deleted ones
        '''
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            print(f"Created {docs_dir} directory.")
            return

        # get all PDFs in docs directory
        current_files = {os.path.abspath(os.path.join(docs_dir, f)) for f in os.listdir(docs_dir) if f.endswith(".pdf")}

        # get all files currently in ChromaDB
        all_entries = self.collection.get(include = ["metadatas"])
        stored_files = {}
        for metadata in all_entries["metadatas"]:
            if metadata and "source" in metadata and "file_hash" in metadata:
                source = os.path.abspath(metadata["source"])
                stored_files[source] = metadata["file_hash"]
        
        # add or update files
        for pdf_path in current_files:
            current_hash = get_file_hash(pdf_path)
            if pdf_path not in stored_files or stored_files[pdf_path] != current_hash:
                print(f"Processing new or modified file: {pdf_path}")
                if pdf_path in stored_files:
                    self.remove_document(pdf_path)
                self.add_document(pdf_path)
        
        # remove files no longer in docs directory
        for stored_path in stored_files.keys():
            if stored_path not in current_files:
                print(f"Removing deleted file from DB: {stored_path}")
                self.remove_document(stored_path)