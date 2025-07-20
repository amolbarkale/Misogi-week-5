"""
Medical AI Assistant RAG Demo
Demonstration of multi-PDF ingestion with async processing
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.pipeline import get_rag_pipeline

async def demo_multi_pdf_ingestion():
    """Demo multiple PDF ingestion with async processing"""
    print("🏥 Medical Research AI Assistant - Multi-PDF Demo")
    print("=" * 50)
    
    try:
        # Initialize RAG pipeline
        pipeline = get_rag_pipeline()
        
        # Example: Ingest multiple medical research PDFs
        pdf_files = [
            "Attention.pdf",  # Replace with your PDF paths
            "fewshot.pdf"   # Replace with your PDF paths
        ]
        
        # Check if PDF files exist (for demo purposes, we'll simulate)
        existing_pdfs = []
        for pdf_path in pdf_files:
            if os.path.exists(pdf_path):
                existing_pdfs.append(pdf_path)
            else:
                print(f"⚠️  PDF not found: {pdf_path} (skipping for demo)")
        
        if existing_pdfs:
            print(f"\n📚 Ingesting {len(existing_pdfs)} medical research PDFs...")
            result = await pipeline.ingest_multiple_pdfs_async(existing_pdfs)
            
            print(f"✅ Ingestion complete!")
            print(f"   📄 Files: {result['files_processed']}")
            print(f"   📖 Pages: {result['total_pages']}")
            print(f"   🧩 Chunks: {result['total_chunks']}")
        
        # Setup retriever for querying
        pipeline.setup_retriever()
        
        # Medical research queries
        queries = [
            "What are the main findings about diabetes treatment?",
            "What methodologies were used in the cardiovascular studies?", 
            "What are the key limitations mentioned in the research?"
        ]
        
        print(f"\n🔍 Running {len(queries)} async queries...")
        
        # Run queries asynchronously
        tasks = [pipeline.query_async(query) for query in queries]
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results, 1):
            print(f"\n📋 Query {i}: {result['question']}")
            print(f"📝 Answer: {result['answer'][:200]}...")
            print(f"📊 Sources: {', '.join(result['sources'])}")
            print(f"🧩 Chunks found: {result['chunks_found']}")
        
        print("\n🎉 Multi-PDF async demo complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Setup checklist:")
        print("1. Set GEMINI_API_KEY in your .env file")
        print("2. Start Qdrant: docker-compose up -d")
        print("3. Place your medical research PDFs in the project root")
        print("4. Update pdf_files list with your actual PDF paths")

def demo_basic():
    """Basic demo without PDFs for testing"""
    print("🏥 Basic Medical Research AI Assistant Demo")
    print("=" * 45)
    
    try:
        # Initialize RAG pipeline
        pipeline = get_rag_pipeline()
        
        # Setup retriever (assumes existing collection)
        pipeline.setup_retriever()
        
        # Sample queries
        queries = [
            "What is the mechanism of action for ACE inhibitors?",
            "What are the side effects of statins?", 
            "How does diabetes affect cardiovascular health?"
        ]
        
        for query in queries:
            print(f"\n🔍 Query: {query}")
            try:
                result = pipeline.query(query)
                print(f"📝 Answer: {result['answer'][:200]}...")
                print(f"📊 Sources: {', '.join(result['sources'])}")
                print(f"🧩 Found {result['chunks_found']} relevant chunks")
            except Exception as e:
                print(f"❌ Query error: {e}")
        
        print("\n🎉 Basic demo complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nℹ️  This demo requires existing documents in Qdrant")

if __name__ == "__main__":
    # Choose demo type
    demo_type = input("Choose demo:\n1. Multi-PDF async (requires PDFs)\n2. Basic (uses existing collection)\nEnter 1 or 2: ").strip()
    
    if demo_type == "1":
        asyncio.run(demo_multi_pdf_ingestion())
    else:
        demo_basic() 