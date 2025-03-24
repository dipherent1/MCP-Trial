# MCP SQLite Server - README

This server is part of the Model Context Protocol (MCP) system and provides a set of SQLite-based tools to enable LLM-driven database interaction. It exposes tools, prompts, and resources for interactive data analysis.

---

## 📦 Features

### ✅ Tools
This server exposes the following tools:
- `read_query`: Execute SELECT queries on the database
- `write_query`: Execute INSERT, UPDATE, DELETE SQL statements
- `create_table`: Create a new table using a CREATE TABLE statement
- `list_tables`: List all tables in the current SQLite database
- `describe_table`: Get schema information for a specific table
- `append_insight`: Append business insights to a memo resource

### 📝 Prompts
This server includes a demo prompt:
- `mcp-demo`: A guided scenario template that walks the user through generating a business narrative, creating tables, querying data, generating insights, and producing a business memo.

### 📄 Resources
- `memo://insights`: A resource that stores live insights discovered throughout the session.

---

## 🛠️ Requirements
- Python 3.10+
- `uvx` (or compatible runtime to execute the server)
- Dependencies listed in `requirements.txt`

---

## 🚀 How to Run

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the server
```bash
uvx sqlite_server.py --db-path ./test.db
```
This launches the MCP SQLite server which listens on stdin/stdout and responds to JSON-RPC requests.

Alternatively, you can run the server directly via Python:
```bash
python sqlite_server.py
```

Make sure your runtime can handle `async` stdin/stdout (e.g., via `uvloop`, `uvicorn`, or `uvx`).

---

## 🔧 Server Capabilities

The server registers the following capabilities:
- `@server.list_tools()` → Advertises all tool definitions
- `@server.call_tool()` → Routes tool execution requests to appropriate SQL handlers
- `@server.list_prompts()` and `@server.get_prompt()` → Returns interactive guided prompts
- `@server.list_resources()` and `@server.read_resource()` → Provides access to live insight memos

---

## 🧠 How It Works

1. The main function initializes the SQLite database
2. The server registers all MCP endpoints (tools, prompts, resources)
3. When a request is received (e.g., `call_tool`), it matches the tool name to the logic in `handle_call_tool()`
4. SQL queries are executed using the built-in `sqlite3` module
5. Insights are stored in-memory and returned via the `memo://insights` resource

---

## 🧪 Example Tool Execution
To execute a tool like `list_tables`, the MCP client sends:
```json
{
  "tool": "list_tables",
  "arguments": {}
}
```
And receives:
```json
{
  "result": [ { "name": "users" }, { "name": "sales" } ]
}
```

---

## 📂 Project Structure (Core Components)
```
sqlite_server.py        # Main server entry point
PROMPT_TEMPLATE         # Template used for demo prompt response
SqliteDatabase          # Class that wraps SQLite logic
handle_call_tool        # Tool router for executing SQL
```

---

## ✅ Summary
- Supports querying, editing, and introspecting SQLite databases
- Includes demo prompts and memo insights
- Fully compatible with any MCP-compatible LLM assistant via stdio
- Easy to extend with more tools or resources

This SQLite server is ideal for demos, local analysis, and LLM-integrated workflows.

