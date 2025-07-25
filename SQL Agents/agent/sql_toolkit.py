from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.sql_database import SQLDatabase
from config import GEMINI_API_KEY, DB_PATH

def get_sql_agent(relevant_tables):
    print('relevant_tables:', relevant_tables)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True)
    
    return agent

db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}", include_tables=relevant_tables, sample_rows_in_table_info=5)