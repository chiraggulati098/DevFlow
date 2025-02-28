import google.generativeai as genai
import os
from dotenv import load_dotenv

from backend.db import store_query, retrieve_similar

# load API keys from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def generate_response(prompt):
    '''
    Send user query to Gemini API and return response
    '''
    cached_response = retrieve_similar(prompt)
    if cached_response:
        print(f"Retrieved from ChromaDB: {prompt}")  
        return f"(Retrieved from history) {cached_response}"

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        response_text = response.text if hasattr(response, "text") else "Error: Response has no text."

        store_query(prompt, response_text)
        return response_text
    except Exception as e:
        return f"Error: {str(e)}"