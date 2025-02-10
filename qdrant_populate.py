from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from extract_text import extract_text_from_docx
import uuid
import os
from config import embedding_model
from sentence_transformers import util


def create_qdrant_collection(client, collection_name, vector_size, distance):
    """Create or recreate a Qdrant collection."""
    try:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config={
                "size": vector_size,
                "distance": distance,
            },
        )
        print(f"Collection '{collection_name}' created successfully.")
    except Exception as e:
        print(f"Error creating Qdrant collection: {e}")










