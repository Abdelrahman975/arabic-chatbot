"""
Query handling logic for the Arabic chatbot.
"""

import os
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import ctranslate2
import torch
from config import DB_PATH, EMBEDDING_MODEL, TOP_K_RESULTS, DEFAULT_NO_ANSWER_MSG

class QueryEngine:
    def __init__(self):
        """Initialize the query engine with vector DB and LLM."""
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"}
        )
        
        # Load vector database if it exists
        if os.path.exists(DB_PATH):
            self.vector_db = FAISS.load_local(DB_PATH, self.embeddings)
            print(f"Loaded vector database from {DB_PATH}")
        else:
            raise FileNotFoundError(f"Vector database not found at {DB_PATH}. Run ingest.py first.")
        
        # Initialize the lightweight LLM (Arabic-compatible)
        # We'll use a small Arabic-compatible model with ONNX or CTranslate2 for CPU efficiency
        self.tokenizer = AutoTokenizer.from_pretrained("aubmindlab/aragpt2-base")
        
        # Using CTranslate2 for optimized CPU inference
        # Note: For production, you might want to convert your model to CT2 format first
        # This is a placeholder - in practice you should convert your preferred model
        print("Loading lightweight LLM model for CPU inference...")
        self.generator = pipeline(
            "text-generation",
            model="aubmindlab/aragpt2-base",
            tokenizer=self.tokenizer,
            device=-1,  # Use CPU
        )

    def get_relevant_context(self, query):
        """Retrieve relevant context from the vector database."""
        results = self.vector_db.similarity_search(query, k=TOP_K_RESULTS)
        context = "\n\n".join([doc.page_content for doc in results])
        
        if not context.strip():
            return None
            
        return context

    def format_prompt(self, query, context):
        """Format the prompt for the LLM with the query and context."""
        # Simple prompt template in Arabic
        template = """
        استنادًا إلى المعلومات التالية:
        
        {context}
        
        أجب على السؤال التالي باللغة العربية:
        {query}
        
        إذا كانت المعلومات المقدمة لا تحتوي على إجابة للسؤال، فقل: "عذرًا، لا أملك معلومات كافية للإجابة على هذا السؤال."
        
        الإجابة:
        """
        
        return template.format(context=context, query=query)

    def answer_question(self, query):
        """Answer a question using RAG approach."""
        # Get relevant context from vector DB
        context = self.get_relevant_context(query)
        
        # Return default message if no relevant context is found
        if not context:
            return DEFAULT_NO_ANSWER_MSG
        
        # Format prompt with context and query
        prompt = self.format_prompt(query, context)
        
        # Check if relevant context contains answer keywords
        # This helps avoid hallucination by ensuring context is actually relevant
        lower_query = query.lower()
        query_keywords = [word for word in lower_query.split() if len(word) > 3]
        
        if not any(keyword in context.lower() for keyword in query_keywords):
            return DEFAULT_NO_ANSWER_MSG
            
        try:
            # Generate answer with LLM
            responses = self.generator(
                prompt,
                max_length=300,
                num_return_sequences=1,
                temperature=0.3,
                top_p=0.85
            )
            
            # Extract the generated answer
            generated_text = responses[0]['generated_text']
            
            # Extract just the answer part after the prompt
            answer = generated_text[len(prompt):].strip()
            
            # If the answer is too short or empty, return from context directly
            if len(answer) < 10:
                # Find the most relevant paragraph in the context
                paragraphs = context.split('\n')
                most_relevant = max(paragraphs, key=lambda p: sum(kw in p.lower() for kw in query_keywords))
                return most_relevant
                
            return answer
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            
            # Fallback: Extract relevant sentence from context
            sentences = context.split('.')
            most_relevant = max(sentences, key=lambda s: sum(kw in s.lower() for kw in query_keywords))
            return most_relevant + '.'