#!/usr/bin/env python3
"""
Multi-Modal RAG Streamlit Application
Interactive web interface for the multi-modal retrieval-augmented generation system.
"""

import streamlit as st
import base64
import io
import pandas as pd
from PIL import Image
import os
import sys

# Add the current directory to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from src.pdf_processing import extract_pdf_elements, separate_elements
from src.summarization import summarize_texts_and_tables, summarize_images
from src.vectorstore import create_vectorstore_and_retriever, add_documents_to_retriever
from src.rag_pipeline import create_rag_chain_with_sources


def initialize_rag_system():
    """Initialize the RAG system and cache it in session state."""
    if 'rag_initialized' not in st.session_state:
        with st.spinner("Initializing Multi-Modal RAG system..."):
            try:
                # Step 1: Extract PDF elements
                st.write("📄 Extracting PDF elements...")
                chunks = extract_pdf_elements(settings.pdf_path, settings.content_path)
                tables, texts, images = separate_elements(chunks)
                
                # Step 2: Generate summaries
                st.write("🤖 Generating summaries...")
                text_summaries, table_summaries = summarize_texts_and_tables(texts, tables)
                image_summaries = summarize_images(images)
                
                # Step 3: Create vectorstore and retriever
                st.write("🔍 Setting up search system...")
                retriever = create_vectorstore_and_retriever()
                add_documents_to_retriever(
                    retriever, texts, text_summaries, tables, table_summaries, images, image_summaries
                )
                
                # Step 4: Create RAG chain
                st.write("⚡ Creating RAG pipeline...")
                rag_chain = create_rag_chain_with_sources(retriever)
                
                # Cache in session state
                st.session_state.rag_chain = rag_chain
                st.session_state.rag_initialized = True
                st.session_state.extraction_stats = {
                    'texts': len(texts),
                    'tables': len(tables), 
                    'images': len(images)
                }
                
                st.success("✅ RAG system initialized successfully!")
                
            except Exception as e:
                st.error(f"❌ Error initializing RAG system: {str(e)}")
                st.stop()


def display_base64_image_streamlit(base64_code, caption="Retrieved Image"):
    """Display a base64 encoded image in Streamlit."""
    try:
        # Decode base64 to bytes
        image_data = base64.b64decode(base64_code)
        # Create PIL Image
        image = Image.open(io.BytesIO(image_data))
        # Display in Streamlit
        st.image(image, caption=caption, use_column_width=True)
    except Exception as e:
        st.error(f"Error displaying image: {str(e)}")


def display_table_from_html(table_html, caption="Retrieved Table"):
    """Display HTML table in Streamlit."""
    try:
        # Try to parse HTML table with pandas
        tables = pd.read_html(table_html)
        if tables:
            st.subheader(caption)
            st.dataframe(tables[0], use_container_width=True)
        else:
            st.subheader(caption)
            st.markdown(table_html, unsafe_allow_html=True)
    except Exception as e:
        st.subheader(caption)
        st.markdown(table_html, unsafe_allow_html=True)


def display_retrieved_context(context):
    """Display the retrieved context including texts, images, and tables."""
    st.subheader("📚 Retrieved Context")
    
    # Display text sources
    if context.get('texts'):
        st.write("**📝 Text Sources:**")
        for i, text_doc in enumerate(context['texts']):
            with st.expander(f"Text Source {i+1}"):
                # Handle both Document objects and CompositeElement objects
                if hasattr(text_doc, 'page_content'):
                    content = text_doc.page_content
                    metadata = getattr(text_doc, 'metadata', {})
                elif hasattr(text_doc, 'text'):
                    content = text_doc.text
                    metadata = getattr(text_doc, 'metadata', {})
                else:
                    content = str(text_doc)
                    metadata = {}
                
                st.write(content)
                if metadata:
                    st.write("**Metadata:**")
                    # Convert metadata to dict if it's not already
                    if hasattr(metadata, '__dict__'):
                        metadata_dict = metadata.__dict__
                    else:
                        metadata_dict = metadata
                    st.json(metadata_dict)
    
    # Display image sources  
    if context.get('images'):
        st.write("**🖼️ Image Sources:**")
        for i, image_b64 in enumerate(context['images']):
            with st.expander(f"Image Source {i+1}", expanded=True):
                display_base64_image_streamlit(image_b64, f"Image {i+1}")
    
    # Check for tables in the original documents
    # Handle both Document and CompositeElement objects
    texts_with_tables = []
    for doc in context.get('texts', []):
        content = ""
        if hasattr(doc, 'page_content'):
            content = doc.page_content
        elif hasattr(doc, 'text'):
            content = doc.text
        else:
            content = str(doc)
        
        if 'table' in content.lower():
            texts_with_tables.append((doc, content))
    
    if texts_with_tables:
        st.write("**📊 Table Sources:**")
        for i, (table_doc, content) in enumerate(texts_with_tables):
            with st.expander(f"Table Source {i+1}"):
                # Try to display as HTML if it contains table tags
                if '<table' in content.lower():
                    display_table_from_html(content, f"Table {i+1}")
                else:
                    st.write(content)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Multi-Modal RAG",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📚 Multi-Modal RAG System")
    st.markdown("Ask questions about your PDF document and get answers with visual context!")
    
    # Sidebar with information
    with st.sidebar:
        st.header("📋 System Info")
        
        # Check if PDF exists
        if os.path.exists(settings.pdf_path):
            st.success(f"✅ PDF loaded: {settings.pdf_filename}")
        else:
            st.error(f"❌ PDF not found: {settings.pdf_filename}")
            st.info("Please add your PDF to the content/ directory")
            st.stop()
        
        # Show extraction stats if available
        if 'extraction_stats' in st.session_state:
            stats = st.session_state.extraction_stats
            st.write("**Extracted Elements:**")
            st.write(f"📝 Texts: {stats['texts']}")
            st.write(f"📊 Tables: {stats['tables']}")
            st.write(f"🖼️ Images: {stats['images']}")
        
        st.markdown("---")
        st.markdown("**💡 Tips:**")
        st.markdown("- Ask specific questions about the document")
        st.markdown("- Images and tables will be shown when relevant")
        st.markdown("- Check the retrieved context for sources")
    
    # Initialize the RAG system
    initialize_rag_system()
    
    # Main query interface
    st.header("🔍 Ask a Question")
    
    # Create a form for the query
    with st.form("query_form", clear_on_submit=False):
        user_question = st.text_area(
            "Enter your question about the document:",
            placeholder="e.g., What is the main topic of this document?",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.form_submit_button("🚀 Ask Question")
        with col2:
            show_context = st.checkbox("Show retrieved context", value=True)
    
    # Process the query
    if submit_button and user_question.strip():
        with st.spinner("🤔 Thinking..."):
            try:
                # Get response with sources
                response = st.session_state.rag_chain.invoke(user_question.strip())
                
                # Display the answer
                st.header("💡 Answer")
                st.write(response['response'])
                
                # Display retrieved context if requested
                if show_context and 'context' in response:
                    st.markdown("---")
                    display_retrieved_context(response['context'])
                    
            except Exception as e:
                st.error(f"❌ Error processing question: {str(e)}")
                st.error("Please try again or check your API keys.")
    
    elif submit_button and not user_question.strip():
        st.warning("⚠️ Please enter a question.")
    
    # Example questions
    if 'rag_initialized' in st.session_state:
        st.markdown("---")
        st.subheader("💭 Example Questions")
        
        example_questions = [
            "What are the main topics discussed in this document?",
            "Can you summarize the key findings?",
            "What figures or charts are shown in the document?",
            "Are there any tables with data?",
            "Who are the authors of this document?"
        ]
        
        cols = st.columns(len(example_questions))
        for i, question in enumerate(example_questions):
            if cols[i % len(cols)].button(f"📝 {question[:30]}...", key=f"example_{i}"):
                st.session_state.example_question = question
                st.rerun()
        
        # Handle example question clicks
        if 'example_question' in st.session_state:
            user_question = st.session_state.example_question
            del st.session_state.example_question
            st.rerun()


if __name__ == "__main__":
    main()