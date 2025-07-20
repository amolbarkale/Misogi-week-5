"""
Medical Research PDF Ingestion Script
Use this script to ingest your medical research PDFs into Qdrant
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.pipeline import get_rag_pipeline

async def ingest_medical_pdfs():
    """Ingest medical research PDFs into Qdrant vector database"""
    
    print("🏥 Medical Research PDF Ingestion")
    print("=" * 40)
    
    # Define your PDF files here
    pdf_files = [
        "medical_research_1.pdf",  # Replace with your actual PDF paths
        "medical_research_2.pdf",  # Replace with your actual PDF paths
        # Add more PDFs as needed
    ]
    
    # Check for PDF files in current directory
    existing_pdfs = []
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            existing_pdfs.append(pdf_file)
            print(f"✅ Found: {pdf_file}")
        else:
            print(f"❌ Not found: {pdf_file}")
    
    # Also check for any PDF files in current directory
    current_dir_pdfs = list(Path(".").glob("*.pdf"))
    if current_dir_pdfs:
        print(f"\n📁 Found {len(current_dir_pdfs)} PDFs in current directory:")
        for pdf in current_dir_pdfs:
            print(f"   📄 {pdf.name}")
        
        use_all = input("\nUse all PDFs found? (y/n): ").strip().lower()
        if use_all == 'y':
            existing_pdfs = [str(pdf) for pdf in current_dir_pdfs]
    
    if not existing_pdfs:
        print("\n⚠️  No PDF files found!")
        print("Place your medical research PDFs in this directory and run again.")
        return
    
    try:
        # Initialize RAG pipeline
        print(f"\n🚀 Initializing pipeline...")
        pipeline = get_rag_pipeline()
        
        # Ingest PDFs asynchronously
        print(f"\n📚 Ingesting {len(existing_pdfs)} medical research PDFs...")
        result = await pipeline.ingest_multiple_pdfs_async(existing_pdfs)
        
        print(f"\n🎉 Ingestion completed successfully!")
        print(f"   📄 Files processed: {result['total_pdfs']}")
        print(f"   📖 Total pages: {result['total_pages']}")
        print(f"   🧩 Total chunks: {result['total_chunks']}")
        print(f"   📂 Files: {', '.join(result['files_processed'])}")
        
        print(f"\n✅ Your medical research documents are now ready for querying!")
        print(f"   🗄️  Collection: {pipeline.settings.collection_name}")
        print(f"   🌐 Qdrant URL: {pipeline.settings.qdrant_url}")
        
        # Test a query
        test_query = input("\nTest with a query (press Enter to skip): ").strip()
        if test_query:
            print(f"\n🔍 Testing query: {test_query}")
            result = await pipeline.query_async(test_query)
            print(f"📝 Answer: {result['answer'][:300]}...")
            print(f"📊 Sources: {', '.join(result['sources'])}")
        
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure GEMINI_API_KEY is set in .env")
        print("2. Start Qdrant: docker-compose up -d")
        print("3. Check PDF files are valid and readable")

if __name__ == "__main__":
    asyncio.run(ingest_medical_pdfs()) 