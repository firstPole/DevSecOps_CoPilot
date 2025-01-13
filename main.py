import requests
import aiohttp
from qdrant_client import QdrantClient
from extract_text import extract_text_from_docx
from nlp_processing import process_document_with_nlp, create_category_prompts, truncate_prompt
from qdrant_populate import create_qdrant_collection_in_memory, populate_qdrant_in_memory
from config import qdrant_config, embedding_model
from ai_code_generator import generate_code_from_azure_async,generate_code_from_azure
from sentence_transformers import SentenceTransformer

# Azure OpenAI configuration
AZURE_OPENAI_API_KEY = ""
AZURE_OPENAI_ENDPOINT = ""
AZURE_OPENAI_API_VERSION = ""
AZURE_OPENAI_DEPLOYMENT = "" 

async def generate_pipeline(user_prompt, docx_file):
    try:
        if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
            raise ValueError("Azure OpenAI API Key or Endpoint is not set.")
        
        # Step 1: Extract text from the document
        print("Extracting text from the document...")
        text = extract_text_from_docx(docx_file)

        # Step 2: Process the text using NLP to categorize it
        print("Categorizing text with NLP...")
        categorized_sections = process_document_with_nlp(text)

        # Step 3: Initialize Qdrant client in-memory
        print("Initializing in-memory Qdrant client...")
        qdrant_client = QdrantClient(path=":memory:")

        # Step 4: Create Qdrant collection in-memory
        print("Creating in-memory Qdrant collection...")
        create_qdrant_collection_in_memory(
            qdrant_client,
            qdrant_config["collection_name"],
            qdrant_config["vector_size"],
            qdrant_config["distance"],
        )

        # Step 5: Populate Qdrant with categorized data
        print("Populating Qdrant collection in-memory...")
        populate_qdrant_in_memory(qdrant_client, categorized_sections, qdrant_config["collection_name"], embedding_model)

        # Step 6: Create category-specific prompts
        print("Creating category-specific prompts...")
        comprehensive_prompt = create_category_prompts(categorized_sections, user_prompt)

        # Step 7: Truncate prompt to minimize token usage
        truncated_prompt = truncate_prompt(comprehensive_prompt, max_length=4000)  # Adjust max length as needed
        print(f"Final truncated prompt:\n{truncated_prompt}")

        # Step 8: Send the comprehensive prompt to Azure OpenAI for code generation
        print(f"Sending prompt to Azure OpenAI...\n")
        generate_code_from_azure
        #await generate_code_from_azure_async(
        generated_code = generate_code_from_azure(
            AZURE_OPENAI_ENDPOINT,
            AZURE_OPENAI_API_KEY,
            truncated_prompt,
            AZURE_OPENAI_API_VERSION,
            AZURE_OPENAI_DEPLOYMENT
        )
        print(f"Generated Code:\n{generated_code}")

        return generated_code

    except Exception as e:
        print(f"Error generating code: {e}")
        return f"Error: {e}"
