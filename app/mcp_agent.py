import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

async def main():
    load_dotenv()
    
    # Create MCPClient from config file
    client = MCPClient.from_config_file(
        os.path.join(os.path.dirname(__file__), "../config/browser_mcp.json")
    )
    
    # Create LLM (Groq as primary, GPT-4o as fallback)
    try:
        llm = ChatOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            model="llama3-70b-8192"
        )
    except:
        llm = ChatOpenAI(model="gpt-4o")

    # Create agent
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    # Run query
    result = await agent.run(
        "Analyze my GitHub activity and suggest areas for improvement",
        max_steps=30,
    )
    print(f"\nResult: {result}")

if __name__ == "__main__":
    asyncio.run(main())
