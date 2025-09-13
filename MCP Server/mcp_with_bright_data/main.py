import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model

from langgraph.prebuilt import create_react_agent

load_dotenv()

async def run_agent():
    
    openai_key = os.getenv("OPENAI_API_KEY")
    bright_data_key = os.getenv("BRIGHT_DATA_API_KEY_2")
        
    client = MultiServerMCPClient(
        {
            "bright_data": {
                "command": "npx",
                "args": ["@brightdata/mcp"],
                "env": {
                    "API_TOKEN": bright_data_key,
                },
                "transport": "stdio"
            }
        }
    )
    
    print("Getting tools from MCP client...")
    tools = await asyncio.wait_for(client.get_tools(), timeout=30.0)
    print(f"Found {len(tools)} tools: {[tool.name for tool in tools]}")

    model = init_chat_model(model="openai:gpt-4o", api_key=openai_key)

    agent = create_react_agent(model, tools, prompt="You are a web search agent with access to brightdata tool to get latest data")

    agent_response = await asyncio.wait_for(
        agent.ainvoke({"messages": "Who won IPL in 2025"}), 
        timeout=60.0
    )

    print("Agent response:")
    print(agent_response["messages"][-1].content)
    

if __name__ == "__main__":
    asyncio.run(run_agent())