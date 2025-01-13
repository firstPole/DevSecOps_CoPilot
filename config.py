from sentence_transformers import SentenceTransformer

# NLP model for sentence embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Qdrant collection configuration for in-memory setup
qdrant_config = {
    "collection_name": "devsecops_best_practices",
    "vector_size": 384,
    "distance": "Cosine",
}
