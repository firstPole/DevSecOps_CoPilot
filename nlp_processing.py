import os
import spacy
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline, AutoTokenizer
from qdrant_populate import create_qdrant_collection
from extract_text import extract_text_from_docx
import uuid

# Load pre-trained models
nlp = spacy.load("en_core_web_sm")
sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
summarizer = pipeline("summarization", model="t5-small")
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Function to process and store documents efficiently
from qdrant_client.http.models import PointStruct
import os
import uuid

def process_and_store_documents(directory_path, qdrant_client):
    """Extract, process, and store documents in Qdrant."""
    for filename in os.listdir(directory_path):
        if filename.endswith(".docx") and not filename.startswith("~$"):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file: {file_path}")

            # Extract and process text
            text = extract_text_from_docx(file_path)
            doc = nlp(text)
            
            points = []
            for sentence in doc.sents:
                vector = sentence_model.encode(sentence.text).tolist()
                points.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector,
                        payload={"content": sentence.text}
                    )
                )
            
            # Store in Qdrant
            collection_name = os.path.splitext(filename)[0]
            create_qdrant_collection(
                qdrant_client, 
                collection_name, 
                sentence_model.get_sentence_embedding_dimension(), 
                "Cosine"
            )
            if points:
                response = qdrant_client.upsert(collection_name=collection_name, points=points)
            print(type(response))
            print(f"File {filename} processed and stored in Qdrant.")


# Function to generate dynamic prompt based on user input and document content
def create_dynamic_prompt(user_prompt, qdrant_client, directory_path):
    """Generate a prompt dynamically based on user input and document content."""
    user_prompt_embedding = sentence_model.encode(user_prompt).tolist()
    if user_prompt_embedding is None:
        raise ValueError("Failed to generate embedding for user prompt.")

    all_points = []

    for filename in os.listdir(directory_path):
        if filename.endswith(".docx") and not filename.startswith("~$"):
            collection_name = os.path.splitext(filename)[0]
            response = qdrant_client.scroll(collection_name=collection_name, scroll_filter=None, limit=100)
            points = response[0] if response and isinstance(response, tuple) else []

            for point in points:
                if point.vector is None:
                    #print(f"Point {point.id} has no vector. Skipping...")
                    continue

                point_vector = point.vector
                similarity = util.cos_sim(user_prompt_embedding, point_vector).item()
                if similarity > 0.5:  # Similarity threshold
                    all_points.append(point)

    # Create a dynamic prompt from relevant content
    selected_sentences = [point.payload["content"] for point in all_points if point.payload and "content" in point.payload]
    final_prompt = "\n".join(selected_sentences) + f"\nUser Prompt: {user_prompt}"
    

    return final_prompt
