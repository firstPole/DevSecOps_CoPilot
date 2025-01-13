from sentence_transformers import SentenceTransformer, util
import spacy
from spacy.matcher import Matcher
from transformers import pipeline, AutoTokenizer

# Load pre-trained models
nlp = spacy.load("en_core_web_sm")
sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
summarizer = pipeline("summarization", model="t5-small")  # Using a smaller summarization model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def categorize_text(text, model=sentence_model):
    """Categorize text using embeddings and semantic similarity."""
    try:
        text_embedding = model.encode(text)
        potential_categories = ["security", "monitoring", "deployment", "CI/CD", "vulnerability", "scalability", "performance", "maintainability"]
        category_embeddings = model.encode(potential_categories)
        similarities = util.cos_sim(text_embedding, category_embeddings).numpy()[0]
        return potential_categories[similarities.argmax()]
    except Exception as e:
        print(f"Error categorizing text: {e}")
        return "uncategorized"

def process_document_with_nlp(text):
    """Process document text and categorize sentences dynamically."""
    doc = nlp(text)
    categorized_text = {}
    for sentence in doc.sents:
        category = categorize_text(sentence.text)
        categorized_text.setdefault(category, []).append(sentence.text)
    return categorized_text

def summarize_category(sentences, max_length=20):
    """Summarizes the key aspects of a list of sentences."""
    try:
        if len(sentences) <= 2:
            return " ".join(sentences)
        text = " ".join(sentences)
        summary = summarizer(text, max_length=max_length, min_length=10)[0]['summary_text']
        return summary
    except Exception as e:
        print(f"Error summarizing category: {e}")
        return "Summary not available"

def truncate_prompt(prompt, max_length=1024):
    """Truncates the prompt to the specified maximum length while preserving meaning."""
    input_ids = tokenizer.encode(prompt)
    if len(input_ids) <= max_length:
        return prompt
    truncated_ids = input_ids[:max_length]
    return tokenizer.decode(truncated_ids, skip_special_tokens=True)

def create_category_prompts(categorized_sections, user_prompt):
    """Creates concise and informative prompts for Azure OpenAI."""
    user_prompt_embedding = sentence_model.encode(user_prompt)
    prompt_parts = [f"**User Prompt:** {user_prompt}"]
    for category, sentences in categorized_sections.items():
        sentence_embeddings = sentence_model.encode(sentences)
        relevance_scores = util.cos_sim(user_prompt_embedding, sentence_embeddings).numpy()[0]
        top_indices = relevance_scores.argsort()[-2:][::-1]
        selected_sentences = [sentences[i] for i in top_indices]
        summary = summarize_category(selected_sentences)
        prompt_parts.append(f"**{category}:** {summary}")
    return "\n".join(prompt_parts)
