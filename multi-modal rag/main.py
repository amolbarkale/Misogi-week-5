#!/usr/bin/env python3
"""
Multi-Modal RAG Application
Main entry point for the multi-modal retrieval-augmented generation system.
"""

from config import settings
from src.pdf_processing import extract_pdf_elements, separate_elements
from src.summarization import summarize_texts_and_tables, summarize_images
from src.vectorstore import create_vectorstore_and_retriever, add_documents_to_retriever, test_retrieval
from src.rag_pipeline import create_rag_chain, create_rag_chain_with_sources
from utils import display_base64_image, print_retrieval_results, print_response_with_context


def main():
    """Main function to run the multi-modal RAG pipeline."""
    
    print("Starting Multi-Modal RAG Pipeline...")
    
    # Step 1: Extract PDF elements
    print("\n1. Extracting PDF elements...")
    chunks = extract_pdf_elements(settings.pdf_path, settings.content_path)
    tables, texts, images = separate_elements(chunks)
    
    print(f"Extracted {len(texts)} text chunks, {len(tables)} tables, and {len(images)} images")
    
    # Step 2: Generate summaries
    print("\n2. Generating summaries...")
    text_summaries, table_summaries = summarize_texts_and_tables(texts, tables)
    image_summaries = summarize_images(images)
    
    print(f"Generated {len(text_summaries)} text summaries, {len(table_summaries)} table summaries, and {len(image_summaries)} image summaries")
    
    # Step 3: Create vectorstore and retriever
    print("\n3. Setting up vectorstore and retriever...")
    retriever = create_vectorstore_and_retriever()
    add_documents_to_retriever(
        retriever, texts, text_summaries, tables, table_summaries, images, image_summaries
    )
    
    # Step 4: Test retrieval
    print("\n4. Testing retrieval...")
    test_docs = test_retrieval(retriever, "who are the authors of the paper?")
    print(f"Retrieved {len(test_docs)} documents for test query")
    
    # Step 5: Create RAG chains
    print("\n5. Creating RAG chains...")
    rag_chain = create_rag_chain(retriever)
    rag_chain_with_sources = create_rag_chain_with_sources(retriever)
    
    # Step 6: Interactive query interface
    print("\n6. Multi-Modal RAG Pipeline ready!")
    print("=" * 60)
    print("You can now ask questions about your PDF document.")
    print("Type 'quit', 'exit', or 'q' to stop.")
    print("Type 'sources' before your question to see source context.")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nEnter your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                print("Please enter a question.")
                continue
            
            # Check if user wants sources
            show_sources = user_input.lower().startswith('sources ')
            if show_sources:
                question = user_input[8:]  # Remove 'sources ' prefix
                print(f"\nQuery with sources: {question}")
                response = rag_chain_with_sources.invoke(question)
                print_response_with_context(response)
            else:
                print(f"\nQuery: {user_input}")
                response = rag_chain.invoke(user_input)
                print("Response:", response)
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error processing question: {str(e)}")
            print("Please try again.")
    
    return rag_chain, rag_chain_with_sources


if __name__ == "__main__":
    # Create content directory if it doesn't exist
    import os
    os.makedirs(settings.content_path, exist_ok=True)
    
    # Check if PDF exists
    if not os.path.exists(settings.pdf_path):
        print(f"PDF file not found at {settings.pdf_path}")
        print("Please add your PDF file to the content/ directory and update the filename in config/settings.py")
        exit(1)
    
    main()