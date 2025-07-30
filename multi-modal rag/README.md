# Multi-Modal RAG Application

## Folder Structure

```
multiModalRag/
├── main.py                          # Main entry point
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── content/                        # Directory for PDF files
│   └── name.pdf              # Place your PDF here
├── config/                         # Configuration files
│   ├── __init__.py
│   └── settings.py                # API keys and settings
├── src/                           # Source code modules
│   ├── pdf_processing/           # PDF extraction functionality
│   │   ├── __init__.py
│   │   └── extractor.py          # PDF parsing and element extraction
│   ├── summarization/           # Text and image summarization
│   │   ├── __init__.py
│   │   └── chains.py            # LangChain summarization chains
│   ├── vectorstore/             # Vector database setup
│   │   ├── __init__.py
│   │   └── store.py             # ChromaDB and retriever configuration
│   └── rag_pipeline/            # RAG chain implementation
│       ├── __init__.py
│       └── pipeline.py          # Multi-modal RAG pipeline
└── utils/                       # Utility functions
    ├── __init__.py
    └── display.py               # Display and formatting utilities
```

## Installation & Setup

### 1. Install System Dependencies

**For macOS:**
```bash
brew install poppler tesseract libmagic
```

**For Linux:**
```bash
apt-get install poppler-utils tesseract-ocr libmagic-dev
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Copy the example environment file and add your API keys:
```bash
cp .env.example .env
```

Edit `.env` file and add your actual API keys:
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
GROQ_API_KEY=gsk_your-groq-api-key-here
LANGCHAIN_API_KEY=lsv2_pt_your-langchain-api-key-here
```

Alternatively, set environment variables directly:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export GROQ_API_KEY="your-groq-api-key"
export LANGCHAIN_API_KEY="your-langchain-api-key"
```

### 4. Add Your PDF

Place your PDF file in the `content/` directory and update the filename in your `.env` file:
```bash
PDF_FILENAME=your-document.pdf
```

## How to Run

### Option 1: Streamlit Web Interface (Recommended)

```bash
streamlit run app.py
```

This will open a web interface in your browser where you can:
- Ask questions in a user-friendly interface
- View retrieved images and tables
- See metadata from source documents
- Get visual feedback during processing

### Option 2: Command Line Interface

```bash
python main.py
```

This will run the CLI version where you can:
1. Extract text, tables, and images from the PDF
2. Generate summaries using AI models
3. Create a vector database for retrieval
4. Set up the RAG pipeline
5. Ask questions interactively in the terminal

## Usage

After running `main.py`, you can use the RAG chains in your own code:

```python
from main import main

# Initialize the system
rag_chain, rag_chain_with_sources = main()

# Ask questions
response = rag_chain.invoke("Your question here")
print(response)

# Get response with sources
response_with_sources = rag_chain_with_sources.invoke("Your question here")
print(response_with_sources['response'])
```