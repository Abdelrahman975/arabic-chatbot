"""
Script to extract text from PDF, chunk it, and create a vector database.
"""

import os
import re
from pypdf import PdfReader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from config import PDF_PATH, DB_PATH, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    print(f"Extracting text from {pdf_path}...")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")
    
    pdf_reader = PdfReader(pdf_path)
    text = ""
    for page in pdf_reader.pages:
        # Ensure proper encoding of Arabic text
        page_text = page.extract_text()
        # Remove any BOM or special characters that might corrupt Arabic text
        page_text = page_text.encode('utf-8', errors='ignore').decode('utf-8')
        text += page_text
    
    print(f"Extracted {len(text)} characters from PDF.")
    return text

def clean_text(text):
    """Clean extracted text by removing extra whitespace and ensuring proper Arabic text encoding."""
    # First ensure proper UTF-8 encoding
    text = text.encode('utf-8', errors='ignore').decode('utf-8')
    
    # Remove any non-Arabic characters that might be causing corruption
    # Keep Arabic characters, numbers, and basic punctuation
    arabic_pattern = re.compile(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\u0020-\u002F\u0030-\u0039\u0660-\u0669\u06F0-\u06F9]')
    text = arabic_pattern.sub(' ', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def chunk_text(text):
    """Split text into chunks for processing."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    print(f"Split text into {len(chunks)} chunks.")
    return chunks

def create_vector_db(chunks):
    """Create a vector database from text chunks."""
    print("Creating vector database...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL, 
        model_kwargs={"device": "cpu"}
    )
    
    db = FAISS.from_texts(chunks, embeddings)
    
    # Save the vector database
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db.save_local(DB_PATH)
    
    print(f"Vector database created and saved to {DB_PATH}")
    return db

def extract_qa_pairs(text):
    """
    Extract question-answer pairs from the text.
    This is an advanced function that tries to identify and separate
    question-answer pairs in the Arabic text based on patterns.
    """
    # Simple pattern: questions often start with "س" followed by a number
    qa_pattern = r'س\d+:(.+?)(?=جواب:)جواب:(.+?)(?=س\d+:|$)'
    pairs = re.findall(qa_pattern, text, re.DOTALL)
    
    clean_pairs = []
    for question, answer in pairs:
        # Clean up the extracted text
        question = clean_text(question)
        answer = clean_text(answer)
        clean_pairs.append((question, answer))
    
    print(f"Extracted {len(clean_pairs)} question-answer pairs.")
    return clean_pairs

def main():
    """Main function to run the ingestion process."""
    text = extract_text_from_pdf(PDF_PATH)
    clean_content = clean_text(text)
    
    # Option 1: Simply chunk the text
    chunks = chunk_text(clean_content)
    
    # Option 2: Extract QA pairs (may be more effective for structured FAQ)
    # qa_pairs = extract_qa_pairs(clean_content)
    # chunks = [f"سؤال: {q}\nجواب: {a}" for q, a in qa_pairs]
    
    # Create vector database
    create_vector_db(chunks)
    
    print("Ingestion process completed successfully!")

if __name__ == "__main__":
    main()