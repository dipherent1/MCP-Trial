# MCP Tool Assistant - How It Works (README)

This document explains the step-by-step logic and flow behind the MCP Tool Assistant, focusing on how it initializes, discovers tools, communicates with servers, and executes tools using a connected Large Language Model (LLM). This breakdown follows the actual execution path and includes explanations of what happens under the hood.

---

## 🛠️ How to Run the Assistant

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
Make sure you have `npx`, `uvx`, or any other command used by your tool servers available in your PATH.

### 2. Prepare Your `.env` File
Create a `.env` file with your Groq API key:
```
LLM_API_KEY=your_groq_api_key_here
```

### 3. Define Tool Server Configurations
Create a file named `servers_config.json`:
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "./test.db"]
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

### 4. Start the Assistant
```bash
python your_main_script.py
```
Then interact via the terminal:
```
You: what tables exist in the database?
```

---

## 1. Initialize LLM Client (Groq)

The assistant begins by initializing the LLM client:
```python
llm_client = LLMClient(api_key)
```
This client is used to send user prompts and system messages to Groq’s LLM endpoint and retrieve responses.

---

## 2. Initialize MCP Servers

Each server (like `sqlite`, `puppeteer`) is initialized using name and arguments defined in `servers_config.json`. Example config:
```json
"sqlite": {
  "command": "uvx",
  "args": ["mcp-server-sqlite", "--db-path", "./test.db"]
}
```

The servers are instantiated and passed to the `ChatSession`:
```python
servers = [Server(name, config) for name, config in server_config["mcpServers"].items()]
chat_session = ChatSession(servers, llm_client)
```

---

## 3. Start the Chat Session

```python
await chat_session.start()
```
This kicks off the full assistant lifecycle:

### 3.1. Initialize All Servers
```python
await server.initialize()
```
This runs the following logic:
- Determine the executable path:
```python
command = shutil.which("npx") if self.config["command"] == "npx" else self.config["command"]
```
- Build `StdioServerParameters`:
```python
server_params = StdioServerParameters(command=command, args=args, env=env)
```
- Start subprocess:
```python
stdio_transport = await stdio_client(server_params)  # Returns (read, write)
```
- Create a ClientSession using `read` and `write`:
```python
session = await ClientSession(read, write)
await session.initialize()
```

This establishes a bidirectional connection to the tool server via stdin/stdout using structured JSON-RPC messages.

**NOTE:**
> When I call `call_tool` from the client side, it runs the function `@server.call_tool()` on the server side using the `read` and `write` pipe passed to `ClientSession`.

### 🔍 Under the Hood:
- `call_tool(...)` sends a message through `write`
- Server reads from stdin using `read`
- Matches the request to a registered tool (`@server.call_tool()`)
- Executes the function
- Sends JSON-RPC response back via stdout
- ClientSession reads the response and returns it to your script

---

## 4. Get Tools From the Server

After initialization:
```python
tools_response = await server.list_tools()
tools = []
```
- Sends this JSON-RPC message:
```json
{
  "jsonrpc": "2.0",
  "method": "list_tools",
  "id": 1
}
```
- Receives this:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [ { "name": "query", ... }, ... ]
  }
}
```
- Converts to high-level tool objects:
```python
for tool in tools_response:
  tools.append(Tool(tool.name, tool.description, tool.inputSchema))
```

Each tool is formatted for the LLM:
```python
Tool: read_query
Description: Execute a SELECT query on the SQLite database
Arguments:
- query: SQL query to execute (required)
```

---

## 5. Send Messages to LLM

Once tools are known, they are sent to the LLM as part of the system message:
```python
llm_response = self.llm_client.get_response(messages)
```

---

## 6. Process LLM Response

The assistant checks if the response is a tool call (JSON):
```json
{
  "tool": "list_tables",
  "arguments": {}
}
```
- If it's a valid tool:
```python
result = await server.execute_tool(tool_name, arguments)
```
This calls:
```python
result = await self.session.call_tool(tool_name, arguments)
```
Which sends the request to the server via `write`, and awaits the response via `read`.

- If no server has the tool:
```python
return f"No server found with tool: {tool_call['tool']}"
```
- If it's not a tool at all, return `llm_response` directly.

---

## 7. Tool Execution Logic

Each server defines what to do for each tool in `@server.call_tool()`:
```python
@server.call_tool()
async def handle_call_tool(name, args):
    if name == "list_tables":
        ...
    elif name == "read_query":
        ...
```
So when the client calls `call_tool("read_query", {"query": "SELECT * FROM users"})`, it hits the server-side handler registered for that tool.

---

## ✅ Summary

- `ClientSession` uses `read` and `write` to talk to the tool server
- `list_tools()` and `call_tool()` use JSON-RPC to communicate
- Tools are defined and handled in the server using `@server.list_tools()` and `@server.call_tool()`
- The LLM decides which tool to use and formats its decision in structured JSON
- Your assistant parses that, locates the matching server, and executes the tool call

This setup allows any tool server (e.g. SQLite, Puppeteer, Browser, Custom APIs) to be connected and queried by an LLM in real-time.

