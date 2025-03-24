import asyncio
import traceback

from pydantic import ValidationError

from beeai_framework.agents.types import AgentExecutionConfig
from beeai_framework.backend.chat import ChatModel
from beeai_framework.backend.message import UserMessage
from beeai_framework.memory import UnconstrainedMemory

from typing import Any
from beeai_framework.emitter.types import EmitterOptions
from beeai_framework.emitter.emitter import Emitter, EventMeta


# Import agent components
from beeai_framework.workflows.agent import AgentFactoryInput, AgentWorkflow
from beeai_framework.workflows.workflow import WorkflowError

# MCP Tool
from beeai_framework.tools.mcp_tools import MCPTool
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

# Create connection to Tool Server
server_params = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "server.py",
    ],
    env=None,
)


async def tools_from_client() -> MCPTool:
    async with (
        stdio_client(server_params) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        return await MCPTool.from_client(session, server_params)


mcp_tools = asyncio.run(tools_from_client())


async def process_agent_events(
    event_data: dict[str, Any], event_meta: EventMeta
) -> None:
    """Process agent events and log appropriately"""

    if event_meta.name == "error":
        print("Agent 🤖 : ", event_data["error"])
    elif event_meta.name == "retry":
        print("Agent 🤖 : ", "retrying the action...")
    elif event_meta.name == "update":
        print(
            f"Agent({event_data['update']['key']}) 🤖 : ",
            event_data["update"]["parsedValue"],
        )
    elif event_meta.name == "newToken":
        print(event_data["value"].get_text_content(), end="")


async def observer(emitter: Emitter) -> None:
    emitter.on("*.*", process_agent_events, EmitterOptions(match_nested=True))


async def main() -> None:
    llm = ChatModel.from_name("ollama:granite3.1-dense:8b")
    try:
        workflow = AgentWorkflow(name="Smart assistant")
        workflow.add_agent(
            agent=AgentFactoryInput(
                model_config={"stream": True},
                name="EmployeeChurn",
                instructions="You are a churn prediction specialist capable of predicting whether an employee will churn. Respond only if you can provide a useful answer.",
                tools=mcp_tools,
                llm=llm,
                execution=AgentExecutionConfig(max_iterations=3),
            )
        )

        employee_sample = {
            "YearsAtCompany": 1,
            "EmployeeSatisfaction": 0.01,
            "Position": "Non-Manager",
            "Salary": 2.0,
        }
        prompt = f"Will this employee churn {employee_sample}?"
        memory = UnconstrainedMemory()
        await memory.add(UserMessage(content=prompt))
        await workflow.run(messages=memory.messages).observe(observer)

    except WorkflowError:
        traceback.print_exc()
    except ValidationError:
        traceback.print_exc()


