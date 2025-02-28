import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma_db")   # stores data persistently
collection = chroma_client.get_or_create_collection("devflow_ai_queries")

def store_query(query, response):
    '''
    Store user queries and AI responses in chroma DB
    '''
    collection.add(
        documents = [response],
        metadatas = [{"query": query}],
        ids = [query]                       # using query as unique ID
    )

def retrieve_similar(query):
    '''
    Retrieve the most similar stored response
    '''
    results = collection.query(query_texts = [query], n_results = 1)
    if results["documents"]:
        return results["documents"][0]
    return None