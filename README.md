intialize llm client using groq, initialize each server name and arg and store it into servers,

pass both to chat session  and initiate it 

chat_session.start(): 
initialize all servers, using server.initialize() 


get all the tools from the server, using tools = await server.list_tools()


format and pass the tool to the llm as system message, wait fot for input from the user, get response from  self.llm_client.get_response(messages)
process llm response using result = await self.process_llm_response(llm_response)

server.initialize()
Locates the command to run the tool server (like npx or uvx) and get tthe path of executing package 
get the command and root adreass 
command = (
            shutil.which("npx")
            if self.config["command"] == "npx"
            else self.config["command"]
        )

creates StdioServerParameters using name,arg and optional env
server_params = StdioServerParameters(
            command=command,
            args=self.config["args"],
            env={**os.environ, **self.config["env"]}
            if self.config.get("env")
            else None,
        )
Starts that server as a subprocess

Connects to it using stdin/stdout pipes (read and write)
stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
Creates a session so you can send requests (like list_tools, call_tool, etc.)

session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.session = session
then cleans up await self.cleanup()

server.list_tools()
get tools from python package client session that has a read and write connection with the server 

tools_response = await self.session.list_tools()
tools = []

Returns a list of low-level tool objects that came from the tool server (like mcp-server-sqlite or server-puppeteer).

This sends a structured message like:

{
  "jsonrpc": "2.0",
  "method": "list_tools",
  "id": 1
}
The tool server replies with:

{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "query",
        "description": "Run SQL on the DB",
        "inputSchema": {
          "type": "object",
          "properties": {
            "sql": {
              "type": "string",
              "description": "The SQL statement to run"
            }
          },
          "required": ["sql"]
        }
      },
      ...
    ]
  }
}

for item in tools_response:
            if isinstance(item, tuple) and item[0] == "tools":
                for tool in item[1]:
                    tools.append(Tool(tool.name, tool.description, tool.inputSchema))
convert the tools in to readable objects 
        return f"""
Tool: {self.name}
Description: {self.description}
Arguments:
{chr(10).join(args_desc)}
"""
args_desc is made from input schema property

get response using 
llm_response = self.llm_client.get_response(messages)

process llm response using 
result = await self.process_llm_response(llm_response)
checks if the response requires a tool (in the form)
"{\n"
                '    "tool": "tool-name",\n'
                '    "arguments": {\n'
                '        "argument-name": "value"\n'
                "    }\n"
                "}\n\n"
tool_call = json.loads(llm_response)

look for the tool required 
tools = await server.list_tools()
                    if any(tool.name == tool_call["tool"] for tool in tools):

if found execute the tool using the name and args from the response
result = await server.execute_tool(
                                tool_call["tool"], tool_call["arguments"]
                            )
if it worked 
return f"Tool execution result: {result}"

if no tool found return f"No server found with tool: {tool_call['tool']}"

if the response is not a tool return llm_response

async def execute_tool 
execute tool using this 
result = await self.session.call_tool(tool_name, arguments)