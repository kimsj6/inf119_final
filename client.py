from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio

#Agent 1: Requirements analyzer
requirements_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)

#Agent 2: Code generator
code_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)

#Agent 3: Tester / debugger
test_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)

async def run_requirements_agent(raw_description: str, session: ClientSession) -> str:
    tools = await load_mcp_tools(session)

    # Create and run the agent
    agent = create_react_agent(requirements_model, tools)
    agent_response = await agent.ainvoke({"messages": "#Add message here"})
    return agent_response

async def run_code_agent(requirements: str, session: ClientSession):
    tools = await load_mcp_tools(session)

    # Create and run the agent
    agent = create_react_agent(code_model, tools)
    agent_response = await agent.ainvoke({"messages": "#Add message here"})
    return agent_response

async def run_test_agent(requirements: str, session: ClientSession):
    tools = await load_mcp_tools(session)

    # Create and run the agent
    agent = create_react_agent(test_model, tools)
    agent_response = await agent.ainvoke({"messages": "#Add message here"})
    return agent_response

async def main() -> None:
    raw_description = """
    """

    server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            requirements = await run_requirements_agent(raw_description, session)

            await run_code_agent(requirements, session)

            await run_test_agent(requirements, session)



# Run the async function
if __name__ == "__main__":
    asyncio.run(main())