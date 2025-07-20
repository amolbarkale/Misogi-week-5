# Medical AI Assistant RAG Pipeline

A simple, focused RAG (Retrieval-Augmented Generation) system for medical document querying using Gemini Flash 2 and Qdrant.

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=medical_documents
```

### 3. Start Qdrant Database
Using Docker Compose (recommended):
```bash
docker compose -f docker-compose.db.yml up -d
```

Or using Docker directly:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Verify Qdrant is Running:**
```bash
# Check container status
docker ps

# Test API connection (should return JSON with version info)
curl http://localhost:6333/

# Access Qdrant Dashboard in browser
http://localhost:6333/dashboard
```

### 4. Access Qdrant Dashboard (Optional)
Open your browser and go to: **http://localhost:6333/dashboard**

You can use the dashboard to:
- View collections and vectors
- Monitor database status
- Explore your ingested documents

### 5. Launch Web UI (Recommended)
```bash
streamlit run streamlit_app.py
```
**Features:**
- 🔍 Interactive question asking
- 📚 Source tracking and display  
- 💬 Conversation history
- 🧪 **RAGAS evaluation testing**
- ⚙️ Configurable retrieval settings

### 6. Run Command Line Demo
```bash
python demo.py
```

### 7. Run RAGAS Evaluation
```bash
# Comprehensive evaluation
python run_ragas_evaluation.py

# Quick evaluation  
python run_ragas_evaluation.py --quick
```

## Usage

### Ingest Multiple Medical Research PDFs
```bash
# Place your PDF files in the project directory
python ingest_pdfs.py
```

Or programmatically:
```python
import asyncio
from src.rag.pipeline import get_rag_pipeline

async def ingest_research():
    pipeline = get_rag_pipeline()
    pdf_files = ["research1.pdf", "research2.pdf"]
    result = await pipeline.ingest_multiple_pdfs_async(pdf_files)
    print(f"Ingested {result['total_chunks']} chunks")

asyncio.run(ingest_research())
```

### Query Documents (Async)
```python
result = await pipeline.query_async("What are the main findings?")
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

## Core Features

- ✅ **Multi-PDF Ingestion**: Load and chunk multiple medical research PDFs
- ✅ **Async Processing**: Efficient embedding calls with asyncio
- ✅ **Vector Search**: Semantic search using Gemini embeddings  
- ✅ **RAG Query**: Context-aware responses with Gemini Flash 2
- ✅ **Source Tracking**: Track which documents provide answers
- ✅ **Web UI**: Beautiful Streamlit interface for interactive querying
- ✅ **RAGAS Evaluation**: Automated testing for faithfulness, relevancy, precision, recall
- ✅ **Docker Compose**: Easy Qdrant database setup

## Architecture

```
PDF → Chunks → Embeddings → Qdrant → Retrieval → Gemini → Answer
```

- **Documents**: PyPDFLoader for PDF processing
- **Chunking**: RecursiveCharacterTextSplitter
- **Embeddings**: GoogleGenerativeAIEmbeddings
- **Vector DB**: Qdrant for similarity search
- **LLM**: Gemini Flash 2 for response generation

## Project Structure

```
src/
├── core/
│   ├── config.py          # Configuration management
│   └── gemini_client.py   # Gemini API client
└── rag/
    └── pipeline.py        # RAG pipeline implementation
```

## Next Steps

This is a foundation for building more advanced features like:
- RAGAS evaluation
- API endpoints  
- Multi-document support
- Advanced query processing 