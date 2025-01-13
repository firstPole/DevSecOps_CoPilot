from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import uuid

def create_qdrant_collection_in_memory(client, collection_name, vector_size, distance):
    """Create or recreate a Qdrant collection in-memory."""
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config={
            "size": vector_size,
            "distance": distance,
        },
    )

def populate_qdrant_in_memory(client, categorized_text, collection_name, model):
    """Populate in-memory Qdrant with categorized text."""
    points = []
    for category, sentences in categorized_text.items():
        for sentence in sentences:
            vector = model.encode(sentence).tolist()
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={"category": category, "content": sentence},
                )
            )

    if points:
        client.upsert(collection_name=collection_name, points=points)
    print(f"In-memory collection '{collection_name}' populated successfully.")
