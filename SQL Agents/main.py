import streamlit as st
from agent.sql_toolkit import get_sql_agent
from agent.table_selector import get_table_selector, select_relevant_tables
from agent.planner import generate_plan
from utils.security import is_rate_limited

st.set_page_config(page_title="SQL Agent Demo", layout="wide")
st.title("🥞 SQL Agent – Natural Language to SQL")

## Rate Limiting
# Check if the request is rate-limited based on the user's IP address
try:
    ip = st.context.headers.get("X-Forwarded-For", st.context.headers.get("X-Real-IP", "127.0.0.1"))
    # Handle multiple IPs in X-Forwarded-For (take first one)
    if "," in ip:
        ip = ip.split(", ")[0].strip()
except:
    ip = "127.0.0.1"

if is_rate_limited(ip):
    st.error("Too many requests. Please try again later.")
    st.stop()

user_query = st.text_input("Ask a data question:")

if user_query:
    st.subheader("🕵️ Query Planning")
    plan = generate_plan(user_query)
    for step in plan:
        st.markdown(f"- {step}")

    st.subheader("📑 Table Selection")
    vectorstore = get_table_selector()
    print("vectorstore", vectorstore)
    relevant_tables = select_relevant_tables(user_query, vectorstore)
    st.write("Likely Tables Used:", relevant_tables)

    st.subheader("🤖 Agent Response")
    agent = get_sql_agent(relevant_tables)
    with st.spinner("Generating SQL and fetching results..."):
        response = agent.run(user_query)
        st.Success(response)
