                      AI Coder - Multi-Agent System
                        IN4MATX 119 Final Project

Team Members:
- Junxi Chen (70714925)
- Tiancheng Qiu （36732598）
- Sung Jin Kim (10906553)

--------------------------------------------------------------------------------
                            PROJECT OVERVIEW
--------------------------------------------------------------------------------

AI Coder is a multi-agent system that uses the Model Context Protocol (MCP) to 
coordinate multiple AI agents for automated code generation. The system takes 
software requirements as input and generates:

- Structured requirements specification
- Complete, runnable Python application code
- Comprehensive test cases (10+ tests with 80%+ pass rate)
- Model usage tracking report

The system is designed to generate an Expense Comparator application - a finance 
software that helps users compare expenses across different time periods with 
visualization capabilities.

--------------------------------------------------------------------------------
                           SYSTEM ARCHITECTURE
--------------------------------------------------------------------------------


Multi-Agent Design

The system consists of three specialized agents that collaborate via MCP:

	Agent 
		Requirements Analyzer
		Code Generator
		Test Generator

	Role
		Parses raw software descriptions into structured requirements
		Creates runnable Python code modules
		Generates comprehensive test cases 
	
	MCP Tools Used
		write_file 
		create_directory, write_file, validate_python_syntax, read_file
		read_file, write_file
	                                

--------------------------------------------------------------------------------
                              INSTALLATION
--------------------------------------------------------------------------------

Prerequisites
- Python 3.9 or higher
- Google API Key for Gemini models

Step 1: Clone the Repository
    git clone <repository-url>
    cd inf119_final

Step 2: Create Virtual Environment (Recommended)
    python -m venv venv
    source venv/bin/activate    # On macOS/Linux
    # OR
    venv\Scripts\activate       # On Windows

Step 3: Install Dependencies
    pip install -r requirements.txt

Step 4: Set Up Google API Key
    Set your Google Generative AI API key as an environment variable:

    export GOOGLE_API_KEY="your-api-key-here"    # On macOS/Linux
    # OR
    set GOOGLE_API_KEY=your-api-key-here         # On Windows CMD

--------------------------------------------------------------------------------
                               HOW TO RUN
--------------------------------------------------------------------------------

Option 1: GUI Mode (Recommended)
Launch the Gradio web interface:

    python main.py

Then open your browser to: http://127.0.0.1:7860

The GUI provides:
- Input box for software description
- Tabs for viewing requirements, generated code, test cases, and usage report
- One-click code generation

Option 2: CLI Mode
Run directly in the terminal:

    python main.py --cli

Option 3: Run GUI Directly
    python gui.py

--------------------------------------------------------------------------------
                         RUNNING GENERATED TESTS
--------------------------------------------------------------------------------

After code generation, run the automated tests:

Method 1: Using the Test Runner Script
    python run_tests.py

Method 2: Using pytest Directly
    cd output
    python -m pytest test_expense_comparator.py -v

Expected output: At least 10 test cases with 8+ passing (80%+ pass rate).

--------------------------------------------------------------------------------
                          MODEL USAGE REPORT
--------------------------------------------------------------------------------

The system tracks and reports API usage for each model:

- Number of API calls to each model
- Total tokens consumed by each model

The report is saved to output/model_usage_report.json in the following format:

{
  "gemini-2.5-flash": {
    "numApiCalls": 15,
    "totalTokens": 45000
  }
}

--------------------------------------------------------------------------------
                    RUNNING THE GENERATED APPLICATION
--------------------------------------------------------------------------------

After generation, run the Expense Comparator application:

    cd output
    python run_app.py

This launches an interactive CLI menu where you can:
- Add expenses with categories
- View expenses by date range
- Compare expenses between periods
- Generate visualization charts

--------------------------------------------------------------------------------
                        GENERATED CODE STRUCTURE
--------------------------------------------------------------------------------

The generated Expense Comparator application includes:

+------------------------+----------------------------------------------------+
| Module                 | Purpose                                            |
+------------------------+----------------------------------------------------+
| models.py              | Data models for Expense, Category, DateRange       |
| expense_manager.py     | Core expense management logic                      |
| comparator.py          | Comparison algorithms for different periods        |
| data_store.py          | Data persistence layer                             |
| visualizer.py          | Chart and graph generation                         |
| cli.py                 | Interactive command-line interface                 |
| main.py                | Application entry point                            |
+------------------------+----------------------------------------------------+

--------------------------------------------------------------------------------
                            MCP INTEGRATION
--------------------------------------------------------------------------------

The system uses Model Context Protocol for agent-tool communication:

MCP Server (server.py)
Provides the following tools via stdio transport:
- validate_python_syntax: Validates code without execution
- write_file: Creates files in output directory
- read_file: Reads generated files
- create_directory: Creates directories
- append_to_file: Appends to existing files
- list_directory: Lists directory contents

MCP Client (client.py)
- Connects to MCP server via StdioServerParameters
- Uses langchain-mcp-adapters to load tools into LangChain agents
- Creates ReAct agents with langgraph.prebuilt.create_react_agent

--------------------------------------------------------------------------------
                                NOTES
--------------------------------------------------------------------------------

- All generated files are saved to the output/ directory
- The system uses Google's Gemini 2.5 Flash model for all agents
- Usage tracking is implemented via LangChain callbacks
- The GUI runs on http://127.0.0.1:7860 by default

--------------------------------------------------------------------------------
                            TROUBLESHOOTING
--------------------------------------------------------------------------------

"GOOGLE_API_KEY not set"
Ensure you've exported your API key:
    export GOOGLE_API_KEY="your-key"

"mcp module not found"
Install dependencies:
    pip install -r requirements.txt

"Test file not found"
Run the code generation first before running tests.

--------------------------------------------------------------------------------
                          TEAM CONTRIBUTIONS
--------------------------------------------------------------------------------

All team members contributed to the design, implementation, and testing of the 
multi-agent system. Commit history is available in the GitHub repository.

================================================================================

