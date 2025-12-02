from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
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

    # Construct the prompt for requirements analysis
    requirements_prompt = f"""You are a Requirements Analyzer Agent. Your task is to analyze the following 
software description and extract detailed, structured requirements.

SOFTWARE DESCRIPTION:
{raw_description}

INSTRUCTIONS:
1. First, use the 'get_expense_comparator_requirements' tool to get the detailed requirements template.
2. Analyze the software description and map it to specific technical requirements.
3. Structure the requirements into categories:
   - Data Models
   - Core Functions
   - User Interface
   - Data Persistence
   - Visualization
   - Testing Requirements

4. Use the 'write_file' tool to save the structured requirements to 'requirements_spec.txt'.

5. Return a summary of the key requirements that will be used by the Code Generator Agent.

Be thorough and specific - the Code Generator will use your output to create the actual code."""

    agent_response = await agent.ainvoke({"messages": [HumanMessage(content=requirements_prompt)]})

    # Extract the final response
    final_message = agent_response["messages"][-1].content
    print(f"\nRequirements Agent Output:\n{final_message[:500]}...")

    return final_message

async def run_code_agent(requirements: str, session: ClientSession):
    tools = await load_mcp_tools(session)

    # Create and run the agent
    agent = create_react_agent(code_model, tools)

    code_prompt = """You are a Code Generator Agent. Your task is to generate complete, 
runnable Python code for the Expense Comparator application based on the following requirements.

REQUIREMENTS:
{requirements}

INSTRUCTIONS:
1. Create a complete Python application with the following structure:
   
   expense_comparator/
   ├── __init__.py
   ├── models.py          # Data models (Expense, Category, DateRange)
   ├── expense_manager.py # Core expense management functions
   ├── comparator.py      # Comparison and analysis functions  
   ├── visualizer.py      # Chart generation functions
   ├── data_store.py      # JSON persistence functions
   ├── cli.py             # Command-line interface
   └── main.py            # Main entry point

2. For each file, use the 'write_file' tool to save the code.
   - Use path like 'expense_comparator/models.py'

3. Ensure the code:
   - Has proper type hints
   - Has docstrings for all classes and functions
   - Handles errors gracefully
   - Is modular and well-organized
   - Can actually run

4. Use 'validate_python_syntax' tool to check each file before saving.

5. After creating all files, use 'write_file' to create a 'run_app.py' file in the root
   that demonstrates how to use the application.

6. Return a summary of the files created and brief instructions on how to run the app.

Generate complete, working code - not pseudocode or placeholders."""

    agent_response = await agent.ainvoke({"messages": [HumanMessage(content=code_prompt)]})

    # Extract the final response
    final_message = agent_response["messages"][-1].content
    print(f"\nCode Agent Output:\n{final_message[:500]}...")

    return final_message





async def run_test_agent(requirements: str, code_summary: str, session: ClientSession):
    tools = await load_mcp_tools(session)

    # Create and run the agent
    agent = create_react_agent(test_model, tools)

     # Construct the prompt for test generation
    prompt = f"""You are a Test Generator Agent. Your task is to create comprehensive 
test cases for the Expense Comparator application.

REQUIREMENTS REFERENCE:
{requirements}

CODE SUMMARY:
{code_summary}

INSTRUCTIONS:
1. First, read the generated code files using 'read_file' tool to understand the implementation:
   - expense_comparator/models.py
   - expense_comparator/expense_manager.py
   - expense_comparator/comparator.py
   - expense_comparator/data_store.py

2. Create a test file 'test_expense_comparator.py' with AT LEAST 10 test cases covering:
   - Test 1-2: Expense model creation and validation
   - Test 3-4: Category enumeration functionality
   - Test 5-6: Adding and retrieving expenses
   - Test 7-8: Date filtering functionality
   - Test 9-10: Comparison calculations
   - Test 11+: JSON save/load operations, edge cases

3. Use pytest framework with clear test names and assertions.

4. Each test should:
   - Have a descriptive name (test_<functionality>_<scenario>)
   - Have a docstring explaining what it tests
   - Use assert statements with clear messages
   - Be independent (not rely on other tests)

5. Use 'write_file' tool to save the tests to 'test_expense_comparator.py'.

6. Use 'run_tests' tool to execute the tests and verify they pass.

7. Return a summary of:
   - Number of tests created
   - What each test covers
   - Test execution results
   - Pass rate percentage

Target: 80%+ pass rate with minimum 10 tests."""

    agent_response = await agent.ainvoke({"messages": [HumanMessage(content=prompt)]})

    # Extract the final response
    final_message = agent_response["messages"][-1].content
    print(f"\nTest Agent Output:\n{final_message[:500]}...")

    return final_message

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

            code_summary = await run_code_agent(requirements, session)

            test_results = await run_test_agent(requirements, code_summary, session)



# Run the async function
if __name__ == "__main__":
    asyncio.run(main())