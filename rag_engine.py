import os
import PyPDF2
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import re

class RAGEngine:
    def __init__(self):
        print("Initializing RAG Engine...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunks = []
        self.index = None
        self.chunk_metadata = []
        self.load_pdfs()
        print(f"Loaded {len(self.chunks)} chunks from PDFs")
    
    def extract_pdf_text(self, pdf_path):
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                print(f"Processing {pdf_path} - {len(reader.pages)} pages")
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n[Page {page_num + 1}]\n{page_text}\n"
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
        return text
    
    def clean_text(self, text):
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n+', '\n', text)  # Multiple newlines to single
        return text.strip()
    
    def chunk_text(self, text, chunk_size=800, overlap=200):
        chunks = []
        text = self.clean_text(text)
        
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk + sentence) < chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if len(chunk) > 100]
    
    def load_pdfs(self):
        all_chunks = []
        all_metadata = []
        
        for file in os.listdir('.'):
            if file.endswith('.pdf'):
                print(f"Processing {file}...")
                text = self.extract_pdf_text(file)
                if text:
                    chunks = self.chunk_text(text)
                    print(f"Created {len(chunks)} chunks from {file}")
                    
                    for i, chunk in enumerate(chunks):
                        all_chunks.append(chunk)
                        all_metadata.append({
                            'source': file,
                            'chunk_id': i,
                            'text': chunk
                        })
        
        if all_chunks:
            print("Creating embeddings...")
            self.chunks = all_chunks
            self.chunk_metadata = all_metadata
            
            # Create embeddings
            embeddings = self.embedding_model.encode(all_chunks, show_progress_bar=True)
            
            # Create FAISS index
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            faiss.normalize_L2(embeddings)  # Normalize for cosine similarity
            self.index.add(embeddings.astype('float32'))
            
            print(f"FAISS index created with {self.index.ntotal} vectors")
        else:
            print("No text extracted from PDFs!")
    
    def search_context(self, query, top_k=5):
        if not self.chunks or self.index is None:
            return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunk_metadata) and scores[0][i] > 0.3:  # Threshold
                results.append({
                    'text': self.chunk_metadata[idx]['text'],
                    'source': self.chunk_metadata[idx]['source'],
                    'score': float(scores[0][i]),
                    'chunk_id': self.chunk_metadata[idx]['chunk_id']
                })
        
        return results
    
    def generate_response(self, query):
        print(f"Query: {query}")
        
        # Get relevant context
        context_chunks = self.search_context(query, top_k=3)
        print(f"Found {len(context_chunks)} relevant chunks")
        
        if not context_chunks:
            return "I couldn't find relevant information in the available documents. Please try rephrasing your question or ask about topics covered in the PDFs."
        
        # Show what was found
        for i, chunk in enumerate(context_chunks):
            print(f"Chunk {i+1} (score: {chunk['score']:.3f}): {chunk['text'][:100]}...")
        
        # Combine context
        context = "\n\n".join([chunk['text'] for chunk in context_chunks])
        sources = list(set([chunk['source'] for chunk in context_chunks]))
        
        # Generate response based on context
        response = self.create_answer(query, context, sources)
        
        return response
    
    def create_answer(self, query, context, sources):
        # Extract key information from context
        query_lower = query.lower()
        
        # Look for specific patterns in the query
        if "how to" in query_lower or "how do" in query_lower:
            # Extract step-by-step instructions
            steps = re.findall(r'\d+\.\s*[^.]+\.', context)
            if steps:
                answer = "Here's how to do it:\n\n"
                for step in steps[:5]:  # Limit to 5 steps
                    answer += f"• {step.strip()}\n"
                answer += f"\n(Source: {', '.join(sources)})"
                return answer
        
        # For other queries, provide contextual answer
        # Find the most relevant sentences
        sentences = re.split(r'(?<=[.!?])\s+', context)
        relevant_sentences = []
        
        query_words = set(query_lower.split())
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            if len(query_words.intersection(sentence_words)) >= 2:
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            answer = "Based on the documentation:\n\n"
            answer += "\n\n".join(relevant_sentences[:3])  # Top 3 relevant sentences
            answer += f"\n\n(Source: {', '.join(sources)})"
            return answer
        
        # Fallback - return first part of context
        answer = f"According to the available information:\n\n{context[:500]}..."
        if len(context) > 500:
            answer += "\n\n[Content truncated]"
        answer += f"\n\n(Source: {', '.join(sources)})"
        
        return answer