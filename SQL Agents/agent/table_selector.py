from langchain_google_genai import GoogleGenerativeEmbeddings
from langchain_community.vectorstores import FAISS
from sqlalchemy import create_engine, inspect
from config import GEMINI_API_KEY, DB_PATH

#  Identify tables in my database
def get_table_selector():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    docs = [{"content": table, "metadata": {"table_name": table}} for table in tables]

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY
    )
    vectorstore = FAISS.from_texts(
        [doc["content"] for doc in docs],
        embedding=embeddings
    )
    return vectorstore

def select_relevant_tables(user_query, vectorstore, k=5):
    docs = vectorstore.similarity_search(user_query, k=k)
    return [doc.page_content for doc in docs]
