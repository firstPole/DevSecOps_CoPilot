import requests
import aiohttp
from qdrant_client import QdrantClient
from extract_text import extract_text_from_docx
from nlp_processing import process_and_store_documents, create_dynamic_prompt
from qdrant_populate import create_qdrant_collection
from config import qdrant_config, embedding_model
from azure_code_generator import generate_code_from_azure_async,generate_code_from_azure
from sentence_transformers import SentenceTransformer
from aws_code_generator import generate_code_from_aws
# from code_generators import generate_code
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_qdrant_client():
    """Initialize and return Qdrant client."""
    return QdrantClient(path=":memory:")

async def generate_pipeline(user_prompt, directory_path, provider_flag):
    try:
        # Step 1: Process and store documents in Qdrant
        print(f"Processing and storing documents from directory: {directory_path}")
        qdrant_client = QdrantClient(path=":memory:")
        process_and_store_documents(directory_path, qdrant_client)

        # Step 2: Process user query and get top matches
        print("Processing user query...")
        #top_sentences, keywords = get_top_matches(user_prompt, qdrant_client, directory_path)


        # Step 3: Generate dynamic prompt based on the user input and document content
        print("Generating dynamic prompt...")
        final_prompt = create_dynamic_prompt(user_prompt, qdrant_client, directory_path)

        # Step 4: Send the prompt to Azure or AWS for code generation
        print("Sending to the provider...")
        if provider_flag == "Azure":
            print("Sending to Azure OpenAI...")
            generated_code = generate_code_from_azure(
                os.getenv("AZURE_OPENAI_ENDPOINT"),
                os.getenv("AZURE_OPENAI_API_KEY"),
                final_prompt,  # No need for truncation
                os.getenv("AZURE_OPENAI_API_VERSION"),
                os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            )
        elif provider_flag == "AWS":
            print("Sending to AWS Bedrock...")
            generated_code = generate_code_from_aws(final_prompt)  # Implement AWS-specific code generator here
        else:
            raise ValueError("Invalid provider flag")

        print(f"Generated Code:\n{generated_code}")
        return generated_code

    except Exception as e:
        print(f"Error generating code: {e}")
        return f"Error: {e}"
