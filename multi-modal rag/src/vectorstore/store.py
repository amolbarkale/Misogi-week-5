import uuid
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain.storage import InMemoryStore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers.multi_vector import MultiVectorRetriever


def create_vectorstore_and_retriever():
    """
    Create and configure the vectorstore and multi-vector retriever.
    
    Returns:
        MultiVectorRetriever: Configured retriever instance
    """
    # The vectorstore to use to index the child chunks
    vectorstore = Chroma(
        collection_name="multi_modal_rag", 
        embedding_function=OpenAIEmbeddings()
    )
    
    # The storage layer for the parent documents
    store = InMemoryStore()
    id_key = "doc_id"
    
    # The retriever (empty to start)
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key=id_key,
    )
    
    return retriever


def add_documents_to_retriever(retriever, texts, text_summaries, tables, table_summaries, images, image_summaries):
    """
    Add documents and their summaries to the retriever.
    
    Args:
        retriever: MultiVectorRetriever instance
        texts (list): List of text elements
        text_summaries (list): List of text summaries
        tables (list): List of table elements
        table_summaries (list): List of table summaries
        images (list): List of base64 encoded images
        image_summaries (list): List of image summaries
    """
    id_key = "doc_id"
    
    # Add texts if they exist
    if texts and text_summaries:
        doc_ids = [str(uuid.uuid4()) for _ in texts]
        summary_texts = [
            Document(page_content=summary, metadata={id_key: doc_ids[i]}) 
            for i, summary in enumerate(text_summaries)
        ]
        retriever.vectorstore.add_documents(summary_texts)
        retriever.docstore.mset(list(zip(doc_ids, texts)))
    
    # Add tables if they exist
    if tables and table_summaries:
        table_ids = [str(uuid.uuid4()) for _ in tables]
        summary_tables = [
            Document(page_content=summary, metadata={id_key: table_ids[i]}) 
            for i, summary in enumerate(table_summaries)
        ]
        retriever.vectorstore.add_documents(summary_tables)
        retriever.docstore.mset(list(zip(table_ids, tables)))
    
    # Add image summaries if they exist
    if images and image_summaries:
        img_ids = [str(uuid.uuid4()) for _ in images]
        summary_img = [
            Document(page_content=summary, metadata={id_key: img_ids[i]}) 
            for i, summary in enumerate(image_summaries)
        ]
        retriever.vectorstore.add_documents(summary_img)
        retriever.docstore.mset(list(zip(img_ids, images)))


def test_retrieval(retriever, query="who are the authors of the paper?"):
    """
    Test the retrieval functionality.
    
    Args:
        retriever: MultiVectorRetriever instance
        query (str): Query to test with
        
    Returns:
        list: Retrieved documents
    """
    docs = retriever.invoke(query)
    return docs

