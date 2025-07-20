# Medical AI Assistant Setup Guide

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Docker** installed for Qdrant database
3. **Gemini API Key** from Google AI Studio

## 🚀 Quick Setup

### 1. Environment Configuration

Create a `.env` file in the project root:

```bash
# Medical AI Assistant Configuration

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Qdrant Database Configuration  
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=medical_research
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Qdrant Database

**Option A: Docker Compose (Recommended)**
```bash
docker compose -f docker-compose.db.yml up -d
```

**Option B: Direct Docker**
```bash
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 4. Prepare Your Medical Research PDFs

- Place your medical research PDF files in the project directory
- Ensure they are readable and valid PDF files
- Recommended: Use research papers, medical studies, clinical trial reports

### 5. Ingest Your PDFs

```bash
python ingest_pdfs.py
```

This will:
- Scan for PDF files in your directory
- Ask which PDFs to process
- Use async processing for efficient ingestion
- Store everything in Qdrant with source tracking

### 6. Test Your Setup

```bash
python demo.py
```

Choose option 1 for multi-PDF demo or option 2 for basic testing.

## 📚 Usage Examples

### Single PDF Ingestion
```python
from src.rag.pipeline import get_rag_pipeline

pipeline = get_rag_pipeline()
chunks = pipeline.ingest_pdf("medical_study.pdf")
```

### Multiple PDFs with Async
```python
import asyncio
from src.rag.pipeline import get_rag_pipeline

async def ingest_research():
    pipeline = get_rag_pipeline()
    pdf_files = ["study1.pdf", "study2.pdf", "clinical_trial.pdf"]
    result = await pipeline.ingest_multiple_pdfs_async(pdf_files)
    print(f"Processed: {result['files_processed']}")
    print(f"Total chunks: {result['total_chunks']}")

asyncio.run(ingest_research())
```

### Querying with Source Tracking
```python
# Synchronous query
result = pipeline.query("What are the side effects of ACE inhibitors?")
print(f"Answer: {result['answer']}")
print(f"Sources: {', '.join(result['sources'])}")

# Async query (recommended for better performance)
result = await pipeline.query_async("What treatment protocols were used?")
print(f"Answer: {result['answer']}")
print(f"Found in: {', '.join(result['sources'])}")
```

## 🔧 Troubleshooting

### Common Issues

**1. Gemini API Errors**
- Verify your API key is correct
- Check if you have credits/quota available
- Ensure the API key has necessary permissions

**2. Qdrant Connection Issues**
```bash
# Check if Qdrant is running
curl http://localhost:6333/

# Check container status
docker ps

# View Qdrant logs
docker compose -f docker-compose.db.yml logs qdrant

# Access Qdrant Dashboard
# Open in browser: http://localhost:6333/dashboard
```

**3. PDF Processing Errors**
- Ensure PDFs are not password-protected
- Check file permissions are readable
- Try with a smaller PDF first

**4. Memory Issues with Large PDFs**
- Reduce chunk size in config
- Process PDFs one at a time
- Increase system memory if possible

### Verification Commands

```bash
# Check Qdrant is running (should return version info)
curl http://localhost:6333/

# Check Qdrant collections
curl http://localhost:6333/collections

# Check collection info (after ingesting PDFs)
curl http://localhost:6333/collections/medical_research

# Access Qdrant Web Dashboard
# Open in browser: http://localhost:6333/dashboard

# Test Gemini API
python -c "from src.core.gemini_client import get_gemini_client; print(get_gemini_client().chat('Test'))"
```

## 📁 Project Structure

```
medical-ai-assistant/
├── src/
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   └── gemini_client.py    # Gemini API client
│   └── rag/
│       └── pipeline.py         # RAG pipeline with async support
├── docker-compose.yml          # Qdrant database setup
├── demo.py                     # Interactive demo
├── ingest_pdfs.py             # PDF ingestion script
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```

## 🎯 Next Steps

After setup, you can:
1. **Add more PDFs**: Just place them in the directory and run `ingest_pdfs.py` again
2. **Build an API**: Use FastAPI to create REST endpoints
3. **Add evaluation**: Integrate RAGAS for quality assessment
4. **Scale up**: Deploy to cloud with container orchestration

## 💡 Tips for Medical Research

1. **Organize by specialty**: Create different collections for different medical areas
2. **Include metadata**: Ensure PDFs have clear titles and author information  
3. **Quality sources**: Use peer-reviewed journals and clinical studies
4. **Regular updates**: Re-ingest when new research becomes available
5. **Compliance**: Ensure all research materials comply with your institution's guidelines 