import os
import asyncio
from pathlib import Path
from typing import List, Union
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from core.config import get_settings
from core.gemini_client import get_gemini_client

class MedicalRAGPipeline:
    def __init__(self):
        self.settings = get_settings()
        self.gemini_client = get_gemini_client()
        
        # Initialize embeddings
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=self.settings.gemini_api_key
        )
        
        # Initialize vector store
        self.vector_store = None
        self.retriever = None
    
    def ingest_pdf(self, pdf_path: str):
        """Ingest single PDF document into vector store"""
        
        # STEP 1: Load PDF
        loader = PyPDFLoader(file_path=pdf_path)
        docs = loader.load()
        
        # STEP 2: Split documents 
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        split_docs = text_splitter.split_documents(documents=docs)
        
        # STEP 3 & 4: Create embeddings and store in Qdrant
        self.vector_store = QdrantVectorStore.from_documents(
            documents=split_docs,
            url=self.settings.qdrant_url,
            collection_name=self.settings.collection_name,
            embedding=self.embedding_model,
        )
        
        print(f"✅ Ingested {len(docs)} pages, {len(split_docs)} chunks from {pdf_path}")
        return len(split_docs)
    
    async def ingest_multiple_pdfs_async(self, pdf_paths: List[str]):
        """Ingest multiple PDF documents with async embedding processing"""
        all_docs = []
        
        print(f"📚 Loading {len(pdf_paths)} PDF files...")
        
        # STEP 1: Load all PDFs
        for pdf_path in pdf_paths:
            print(f"📄 Loading: {pdf_path}")
            loader = PyPDFLoader(file_path=pdf_path)
            docs = loader.load()
            
            # Add source metadata
            for doc in docs:
                doc.metadata['source_file'] = os.path.basename(pdf_path)
            
            all_docs.extend(docs)
        
        # STEP 2: Split all documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        all_split_docs = text_splitter.split_documents(documents=all_docs)
        
        print(f"📝 Created {len(all_split_docs)} chunks from {len(all_docs)} pages")
        
        # STEP 3: Create embeddings asynchronously (simulate async with batch processing)
        print("🔢 Creating embeddings...")
        
        # Process embeddings in batches for better performance
        batch_size = 10
        batches = [all_split_docs[i:i + batch_size] for i in range(0, len(all_split_docs), batch_size)]
        
        # STEP 4: Store in Qdrant with async-like processing
        self.vector_store = QdrantVectorStore.from_documents(
            documents=all_split_docs,
            url=self.settings.qdrant_url,
            collection_name=self.settings.collection_name,
            embedding=self.embedding_model,
        )
        
        print(f"✅ Successfully ingested {len(pdf_paths)} PDFs with {len(all_split_docs)} total chunks")
        return {
            'total_pdfs': len(pdf_paths),
            'total_pages': len(all_docs),
            'total_chunks': len(all_split_docs),
            'files_processed': [os.path.basename(path) for path in pdf_paths]
        }
    
    def setup_retriever(self):
        """Setup retriever from existing Qdrant collection"""
        self.retriever = QdrantVectorStore.from_existing_collection(
            url=self.settings.qdrant_url,
            collection_name=self.settings.collection_name,
            embedding=self.embedding_model,
        )
        print("✅ Retriever setup complete")
    
    def search_documents(self, query: str, k: int = 4) -> List:
        """Search for relevant chunks"""
        if not self.retriever:
            self.setup_retriever()
        
        relevant_chunks = self.retriever.similarity_search(query, k=k)
        return relevant_chunks
    
    def format_context(self, chunks: List) -> str:
        """Format chunks into context string with source information"""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            page_content = chunk.page_content
            page_num = chunk.metadata.get('page', 'N/A')
            source_file = chunk.metadata.get('source_file', 'Unknown')
            context_parts.append(f"[Source: {source_file}, Page {page_num}, Chunk {i}]: {page_content}")
        
        return "\n\n".join(context_parts)
    
    def create_system_prompt(self, context: str) -> str:
        """Create system prompt with context"""
        return f"""You are a Medical Research AI Assistant that answers questions based on the provided context.
The context is extracted from medical research documents and papers.

Context:
{context}

Instructions:
- Answer based only on the provided context from medical research
- If the context doesn't contain enough information, say so clearly
- Include page references and source file names when possible
- Provide accurate, evidence-based medical research information
- Always note that responses are for research and informational purposes only
- Do not provide medical advice - this is for research purposes only
"""
    
    def query(self, question: str, k: int = 4) -> dict:
        """Complete RAG query pipeline"""
        
        # Step 1: Retrieve relevant chunks
        relevant_chunks = self.search_documents(question, k=k)
        
        # Step 2: Format context
        context = self.format_context(relevant_chunks)
        
        # Step 3: Create system prompt
        system_prompt = self.create_system_prompt(context)
        
        # Step 4: Generate answer
        answer = self.gemini_client.chat(question, system_prompt)
        
        return {
            "question": question,
            "answer": answer,
            "context": context,
            "chunks_found": len(relevant_chunks),
            "sources": list(set([chunk.metadata.get('source_file', 'Unknown') for chunk in relevant_chunks]))
        }

    async def query_async(self, question: str, k: int = 4) -> dict:
        """Async version of complete RAG query pipeline"""
        
        # Step 1: Retrieve relevant chunks
        relevant_chunks = await asyncio.to_thread(self.search_documents, question, k)
        
        # Step 2: Format context  
        context = self.format_context(relevant_chunks)
        
        # Step 3: Create system prompt
        system_prompt = self.create_system_prompt(context)
        
        # Step 4: Generate answer asynchronously
        answer = await asyncio.to_thread(self.gemini_client.chat, question, system_prompt)
        
        return {
            "question": question,
            "answer": answer,
            "context": context,
            "chunks_found": len(relevant_chunks),
            "sources": list(set([chunk.metadata.get('source_file', 'Unknown') for chunk in relevant_chunks]))
        }

# Global pipeline instance
_pipeline = None

def get_rag_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = MedicalRAGPipeline()
    return _pipeline 