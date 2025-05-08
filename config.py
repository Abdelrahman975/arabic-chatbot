"""
Configuration settings for the Arabic chatbot application.
"""

# Data paths
PDF_PATH = "data/FAQ-Arabic.pdf"
DB_PATH = "data/vector_db"

# Model parameters
EMBEDDING_MODEL = "CAMeL-Lab/bert-base-arabic-camelbert-mix"  # Better Arabic embedding model
LLM_MODEL = "aubmindlab/aragpt2-base"  # Arabic-specific model
DEFAULT_NO_ANSWER_MSG = "عذرًا، لا أملك معلومات كافية للإجابة على هذا السؤال."

# Retrieval parameters
TOP_K_RESULTS = 3
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Server settings
HOST = "127.0.0.1"
PORT = 8000