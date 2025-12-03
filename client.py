# client.py
# Name: Junxi Chen, Mark Qiu, Sung Jin Kim
# Student ID: 70714925, , 10906553
#
# Description: Multi-Agent System Client using Model Context Protocol (MCP)
# This module implements the multi-agent architecture for the AI Coder system.
# It defines three specialized agents that collaborate to generate code and tests.

"""
AI Coder Multi-Agent System Client

This module implements a multi-agent system that uses the Model Context Protocol (MCP)
for communication between agents. The system consists of three specialized agents:

1. Requirements Analyzer Agent:
   - Role: Parse and structure raw software descriptions into detailed requirements
   - Tools: get_expense_comparator_requirements, write_file
   - Output: Structured requirements specification

2. Code Generator Agent:
   - Role: Generate complete, runnable Python code based on requirements
   - Tools: write_file, validate_python_syntax, create_directory
   - Output: Full application codebase with proper structure

3. Test Generator Agent:
   - Role: Create comprehensive test cases and run them
   - Tools: read_file, write_file, run_tests
   - Output: Test file with 10+ test cases, execution results

The agents communicate via MCP and share context through the session.
"""

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import asyncio
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Import our usage tracker for model statistics
from usage_tracker import get_callbacks, global_tracker


# =============================================================================
# MODEL CONFIGURATION
# =============================================================================
# Each agent uses a separate model instance for clear usage tracking.
# All models are configured with temperature=0 for deterministic outputs.
# The callbacks parameter enables usage tracking for API calls and tokens.
# =============================================================================

# Agent 1: Requirements Analyzer
# Role: Analyzes raw software descriptions and extracts structured requirements
# This agent is the first in the pipeline and sets the foundation for code generation
requirements_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    callbacks=get_callbacks(),  # Enable usage tracking
)

# Agent 2: Code Generator
# Role: Generates complete, runnable Python code based on analyzed requirements
# This agent creates the entire application structure with proper modularity
code_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    callbacks=get_callbacks(),  # Enable usage tracking
)

# Agent 3: Test Generator and Runner
# Role: Creates comprehensive test cases and executes them to verify code quality
# This agent ensures the generated code meets the 80% pass rate requirement
test_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    callbacks=get_callbacks(),  # Enable usage tracking
)


# =============================================================================
# DEFAULT SOFTWARE DESCRIPTION
# =============================================================================
# The Expense Comparator application description from the project requirements.
# This is the software that our multi-agent system will generate code for.
# =============================================================================

EXPENSE_COMPARATOR_DESCRIPTION = """
Expense Comparator is a finance software application that helps users compare their 
expenses across different time periods. Users can input their expenses and categorize 
them into different categories such as groceries, transportation, entertainment, etc. 
The application will provide a visual representation of their expenses through charts 
and graphs, allowing users to easily compare their spending habits between different 
timeframes. Users can also set custom date ranges for comparison. The main function 
of the software is to provide users with a clear understanding of their spending 
patterns and identify areas where they can make adjustments to improve their 
financial well-being.
"""


# =============================================================================
# AGENT FUNCTIONS
# =============================================================================
# Each function implements one agent's behavior. Agents are designed to be
# independent but collaborate through shared context and MCP tools.
# =============================================================================

async def run_requirements_agent(raw_description: str, session: ClientSession) -> str:
    """
    Run the Requirements Analyzer Agent.
    
    This agent is responsible for:
    1. Analyzing the raw software description
    2. Extracting detailed technical requirements
    3. Structuring requirements into categories
    4. Saving the requirements specification to a file
    
    Args:
        raw_description: The raw software description from user input
        session: Active MCP client session for tool access
        
    Returns:
        Structured requirements that will be used by the Code Generator Agent
    """
    # Load MCP tools available from the server
    tools = await load_mcp_tools(session)

    # Create a ReAct agent with the requirements model
    # ReAct (Reasoning + Acting) allows the agent to think and use tools
    agent = create_react_agent(requirements_model, tools)

    # Construct the detailed prompt for requirements analysis
    # This prompt guides the agent through the analysis process
    requirements_prompt = f"""You are a Requirements Analyzer Agent.
    Your task is to analyze the following software description and turn it into a detailed, 
    structured requirements document.

    SOFTWARE DESCRIPTION:
    {raw_description}

    INSTRUCTIONS:
    1. Generate a thorough, structured requirements document using ONLY the information in 
        the software description plus reasonable, clearly-labeled assumptions.
        - Do NOT invent major features that are not implied by the description.
        - If you need to assume something, mark it with a prefix like 'ASSUMPTION:'.

    2. Organize the requirements into clear sections, for example:
        - High-level goal
        - Data models
        - Core functions and APIs
        - User interactions / UI
        - Persistence / storage
        - Error handling and edge cases
        - Testing requirements 

    3. Write the document in a clean, Markdown-style format with headings and numbered lists
       where appropriate, so another agent can read it easily.

    4. Use the 'write_file' MCP tool to save the full document as 'requirements_spec.txt'
       in the project output directory.

    5. In your final message, return the full requirements text EXACTLY as written to the file.
       This text will be passed directly to the Code Generator Agent, which must be able to 
       implement the entire application from this document alone.
    """

    # Execute the agent with the prompt
    # Increase recursion_limit to allow more tool calls
    agent_response = await agent.ainvoke(
        {"messages": [HumanMessage(content=requirements_prompt)]},
        config={"recursion_limit": 50}
    )

    # Extract and return the final response from the agent
    final_message = agent_response["messages"][-1].content
    print(f"\n{'='*60}")
    print("REQUIREMENTS AGENT OUTPUT")
    print('='*60)
    print(f"{final_message[:1000]}...")
    print('='*60)

    return final_message


async def run_code_agent(requirements: str, session: ClientSession) -> str:
    """
    Run the Code Generator Agent.
    
    This agent is responsible for:
    1. Reading the structured requirements
    2. Creating the application file structure
    3. Generating complete, runnable Python code
    4. Validating syntax before saving files
    5. Creating a main entry point
    
    Args:
        requirements: Structured requirements from the Requirements Agent
        session: Active MCP client session for tool access
        
    Returns:
        Summary of generated files and instructions for running the application
    """
    # Load MCP tools available from the server
    tools = await load_mcp_tools(session)

    # Create a ReAct agent with the code generator model
    agent = create_react_agent(code_model, tools)

    # Construct the detailed prompt for code generation
    # This prompt provides clear structure and quality requirements
    code_prompt = f"""You are a Code Generator Agent. Your job is to generate complete, runnable Python code for the Expense Comparator application. 
    
    You have access to these MCP tools:
        - create_directory(path: str)
        - write_file(filename: str, content: str)
        - validate_python_syntax(code: str) - read_file(filename: str)
        - append_to_file(filename: str, content: str)
    Do NOT invent tools that do not exist. Always use these tools to create files.
    
    REQUIREMENTS DOCUMENT:
    {requirements}

    INSTRUCTIONS:
    1. Carefully read the requirements document and plan the simple user interactive application structure.
    2. Use 'create_directory' to create this directory: - 'expense_comparator'
    3. Under 'expense_comparator', create these Python modules using 'write_file':
        - 'expense_comparator/__init__.py'
        - 'expense_comparator/models.py'
        - 'expense_comparator/expense_manager.py'
        - 'expense_comparator/comparator.py'
        - 'expense_comparator/data_store.py'
        - 'expense_comparator/visualizer.py'
        - 'expense_comparator/cli.py'
        - 'expense_comparator/main.py'
    4. For each module:
        - First generate the code in your reasoning.
        - Call 'validate_python_syntax' on the code string.
        - Only if syntax is valid, call 'write_file' to save it.
        - If syntax is invalid, fix it and re-validate.
    5. The code MUST:
        - Implement the behavior described in the requirements (data models, core functions, etc.).
        - Include type hints and docstrings for functions/classes.
        - Use clean imports and avoid circular dependencies.
        - Be runnable and give have simple and interactive CLI menu.
    6. At the end, create a small `run_app.py` in the root (not inside the package) that works as a simple entry point to the application, using `write_file("run_app.py", ...)`.
    7. In your final message back to the user:
        - Summarize the created files and their purpose.

    Remember: do not print code in the chat. Use 'create_directory' and 'write_file' to actually create the files in the output directory."""

    # Execute the agent with the prompt
    # Increase recursion_limit to allow more tool calls (each file = ~2 calls)
    agent_response = await agent.ainvoke(
        {"messages": [HumanMessage(content=code_prompt)]},
        config={"recursion_limit": 100}
    )

    # Extract and return the final response from the agent
    final_message = agent_response["messages"][-1].content
    print(f"\n{'='*60}")
    print("CODE GENERATOR AGENT OUTPUT")
    print('='*60)
    print(f"{final_message[:1000]}...")
    print('='*60)

    return final_message


async def run_test_agent(requirements: str, session: ClientSession) -> str:
    """
    Run the Test Generator Agent.
    
    This agent is responsible for:
    1. Reading the generated code files to understand implementation
    2. Creating comprehensive test cases (minimum 10) that tests all major functionality
    
    Args:
        requirements: Original requirements for reference
        code_summary: Summary from the Code Generator Agent
        session: Active MCP client session for tool access
        
    Returns:
        Test execution results including pass/fail counts and coverage summary
    """
    # Load MCP tools available from the server
    tools = await load_mcp_tools(session)

    # Create a ReAct agent with the test model
    agent = create_react_agent(test_model, tools)

    # Construct the detailed prompt for test generation
    # This prompt ensures comprehensive test coverage
    prompt = f"""You are a Test Generator Agent. Create test cases for the Expense Comparator application.

    REQUIREMENTS DOCUMENT:
    {requirements}

    TOOLS YOU CAN USE:
    - read_file(filename: str)
    - write_file(filename: str, content: str)
    - append_to_file(filename: str, content: str)

    STEPS:
    1. Read ONLY the high-level code files using 'read_file':
    - expense_comparator/models.py
    - expense_comparator/expense_manager.py
    - expense_comparator/comparator.py
    - expense_comparator/data_store.py

    2. Create 'test_expense_comparator.py' with **between 12 and 15 tests total**.
    - Each test should:
        - Be small and focused on a single behavior
        - Use clear, descriptive names like test_add_expense_valid, test_add_expense_invalid_amount, etc.
        - Use simple inputs and assertions
    - Prefer a few well-chosen tests over many exhaustive ones.

    3. IMPORTANT CONSTRAINTS:
    - Do NOT import external libraries
    - Tests may only import:
        - pytest
        - Python standard library modules if truly needed (e.g., datetime)
        - The project modules: expense_comparator.models, expense_comparator.expense_manager,
        expense_comparator.comparator, expense_comparator.data_store
    - Treat the database / storage layer as a black box:
        - Call the public APIs (e.g., ExpenseManager methods) instead of touching DB connections directly.
        - Do NOT open connections manually or execute raw SQL in tests.

    4. Write all tests into a single file 'test_expense_comparator.py' using 'write_file'.
    - No need to over-optimize fixtures; use fixtures only if they make the code clearer.
    - Aim for readability and simplicity.

    5. In your final message, summarize:
    - How many tests you created
    - What main behaviors are covered

    Remember: do not print code in the chat. Use 'write_file' to actually create the files in the output directory.
    """

    # Execute the agent with the prompt
    # Increase recursion_limit to allow reading files + writing + running tests
    agent_response = await agent.ainvoke(
        {"messages": [HumanMessage(content=prompt)]},
        config={"recursion_limit": 80}
    )

    # Extract and return the final response from the agent
    final_message = agent_response["messages"][-1].content
    print(f"\n{'='*60}")
    print("TEST GENERATOR AGENT OUTPUT")
    print('='*60)
    print(f"{final_message[:1000]}...")
    print('='*60)

    return final_message


# =============================================================================
# MCP SESSION MANAGEMENT
# =============================================================================
# Context manager for establishing and managing MCP sessions.
# This allows clean session handling in both CLI and GUI modes.
# =============================================================================

@asynccontextmanager
async def get_mcp_session() -> AsyncGenerator[ClientSession, None]:
    """
    Create an MCP session context manager.
    
    This context manager handles:
    1. Starting the MCP server process
    2. Establishing the client connection
    3. Initializing the session
    4. Cleaning up on exit
    
    Yields:
        Initialized ClientSession for MCP communication
        
    Example:
        async with get_mcp_session() as session:
            tools = await load_mcp_tools(session)
            # Use tools...
    """
    # Configure server parameters to start the MCP server
    # Use sys.executable to ensure we use the same Python interpreter
    # This works across different systems (macOS, Linux, Windows)
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
    )

    # Create stdio client connection to the server
    async with stdio_client(server_params) as (read, write):
        # Create and initialize the client session
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
# The main function orchestrates the entire multi-agent workflow.
# It can be run directly for CLI usage or imported for GUI usage.
# =============================================================================

async def main() -> None:
    """
    Main entry point for the AI Coder multi-agent system.
    
    This function orchestrates the complete workflow:
    1. Initializes the MCP session
    2. Runs the Requirements Analyzer Agent
    3. Runs the Code Generator Agent
    4. Runs the Test Generator Agent
    5. Displays the model usage report
    
    The agents run sequentially, with each agent's output feeding into the next.
    """
    # Use the default Expense Comparator description
    raw_description = EXPENSE_COMPARATOR_DESCRIPTION

    print("="*60)
    print("AI CODER - MULTI-AGENT SYSTEM")
    print("="*60)
    print("\nStarting multi-agent code generation pipeline...")
    print(f"\nSoftware Description:\n{raw_description[:200]}...")
    print("\n" + "="*60)

    # Reset the usage tracker for a fresh run
    global_tracker.reset()

    # Establish MCP session and run all agents
    async with get_mcp_session() as session:
        # Phase 1: Requirements Analysis
        print("\n📋 PHASE 1: Requirements Analysis")
        print("-"*40)
        requirements = await run_requirements_agent(raw_description, session)

        # Phase 2: Code Generation
        print("\n💻 PHASE 2: Code Generation")
        print("-"*40)
        await run_code_agent(requirements, session)

        # Phase 3: Test Generation and Execution
        print("\n🧪 PHASE 3: Test Generation & Execution")
        print("-"*40)
        test_results = await run_test_agent(requirements, session)

    # Display and save the model usage report
    print("\n" + "="*60)
    print("📊 MODEL USAGE REPORT")
    print("="*60)
    print(global_tracker.get_summary())
    
    # Save the usage report to JSON file
    report_path = global_tracker.save_report("output/model_usage_report.json")
    print(f"\nUsage report saved to: {report_path}")
    
    # Print JSON format for easy verification
    print("\nJSON Format:")
    print(global_tracker.get_usage_report_json())

    print("\n" + "="*60)
    print("✅ CODE GENERATION COMPLETE!")
    print("="*60)
    print("\nGenerated files are in the 'output/' directory.")
    print("Run tests with: cd output && python -m pytest test_expense_comparator.py -v")


# Run the async function when script is executed directly
if __name__ == "__main__":
    asyncio.run(main())
