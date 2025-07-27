import streamlit as st
from agents.langchain_tools import get_sheet_names
from agents.langchain_agent import langchain_sheets_agent

st.set_page_config(page_title="🤖 LangChain Google Sheets Agent", layout="wide")

# Header
st.title("🤖 LangChain Google Sheets Agent")
st.markdown("*Powered by LangChain & Google Gemini*")

# Sidebar with agent information
with st.sidebar:
    st.header("📋 Agent Information")
    
    if st.button("🔄 Clear Memory"):
        try:
            langchain_sheets_agent.clear_memory()
            st.success("Agent memory cleared successfully.")
        except Exception as e:
            st.error(f"Error clearing memory: {str(e)}")
    
    if st.button("📖 Show Capabilities"):
        try:
            tools = langchain_sheets_agent.get_available_tools()
            
            info = """
🤖 **LangChain Google Sheets Agent**

**Available Operations:**
"""
            for tool in tools:
                info += f"• **{tool['name']}**: {tool['description']}\n"
            
            info += """
**Natural Language Examples:**
• "Filter employees with salary > 50000"
• "Group by department and sum salaries"
• "Create pivot table with regions as rows and products as columns"
• "Sort by date descending"
• "Add a bonus column that's 10% of salary"
• "Add a new employee: John Doe, age 30, salary 75000"

**Enhanced Features:**
• Conversation memory - remembers context
• Better error handling and recovery
• Structured tool calling with validation
• Automatic sheet context awareness
"""
            st.markdown(info)
        except Exception as e:
            st.error(f"Error getting agent info: {str(e)}")
    
    if st.button("💬 Show History"):
        try:
            history = langchain_sheets_agent.get_conversation_history()
            if isinstance(history, list) and len(history) > 0:
                st.write("**Conversation History:**")
                for i, msg in enumerate(history[-5:]):  # Show last 5 messages
                    if hasattr(msg, 'content'):
                        st.write(f"{i+1}. {msg.content[:100]}...")
            else:
                st.write("No conversation history yet.")
        except Exception as e:
            st.error(f"Error getting history: {str(e)}")

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Sheet Operations")
    
    # Sheet selection
    try:
        sheet_names = get_sheet_names()
        sheet = st.selectbox("📋 Select Worksheet", sheet_names)
    except Exception as e:
        st.error(f"Error loading sheets: {e}")
        st.stop()
    
    # Query input with examples
    st.markdown("### 💬 Ask me anything about your sheet:")
    
    # Example queries
    example_queries = [
        "Filter employees with salary > 50000",
        "Group by department and sum salaries", 
        "Create pivot table with regions as rows",
        "Sort by date descending",
        "Add a bonus column that's 10% of salary",
        "Show me sheet information"
    ]
    
    selected_example = st.selectbox("📝 Or choose an example query:", [""] + example_queries)
    
    if selected_example:
        user_query = st.text_area("✨ Your Query:", value=selected_example, height=100)
    else:
        user_query = st.text_area("✨ Your Query:", height=100, placeholder="Type your natural language request here...")

with col2:
    st.header("💡 Quick Tips")
    st.markdown("""
    **Natural Language Examples:**
    
    🔍 **Filtering:**
    - "Show employees with salary > 60000"
    - "Filter products where category is 'Electronics'"
    
    📊 **Aggregation:**
    - "Sum sales by region"
    - "Average salary by department"
    
    🔄 **Pivot Tables:**
    - "Pivot by category and month showing sales"
    
    📈 **Sorting:**
    - "Sort by date newest first"
    - "Order by name alphabetically"
    
    ➕ **Adding Data:**
    - "Add column for 15% tax calculation"
    - "Add new employee John, age 25, salary 50000"
    """)

# Process query
if st.button("🚀 Execute Query", type="primary"):
    if user_query.strip():
        with st.spinner("🔄 Processing your request with LangChain..."):
            try:
                # Process query using LangChain agent directly
                result = langchain_sheets_agent.process_query(user_query, sheet)
                
                if result["success"]:
                    response = result["response"]
                    # Display response
                    st.success("✅ Task Completed!")
                    
                    # Format response for better display
                    if isinstance(response, str):
                        if "Successfully" in response or "Created" in response:
                            st.success(response)
                        elif "Error" in response:
                            st.error(response)
                        else:
                            st.info(response)
                    else:
                        st.write(response)
                else:
                    st.error(f"❌ Error: {result['response']}")
                    
            except Exception as e:
                st.error(f"❌ System Error: {str(e)}")
                st.info("💡 Try rephrasing your query or check your sheet configuration.")
    else:
        st.warning("⚠️ Please enter a query or select an example.")

# Footer
st.markdown("---")
st.markdown("*Built with LangChain, Streamlit, and Google Sheets API*")
