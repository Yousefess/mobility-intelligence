from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.agents.tools import ALL_TOOLS
from app.core.config import settings

SYSTEM_PROMPT = (
    "You are a mobility data analyst assistant. You answer questions about "
    "GPS trajectory data (GeoLife dataset, Beijing) using the tools provided. "
    "Always call a tool to get real numbers before answering -- never guess "
    "statistics. If a question needs a mode you don't recognize, tell the "
    "user which modes are available instead of guessing."
)


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


llm = ChatOpenAI(
    model="qwen/qwen3.8-27b",
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
    temperature=0,
).bind_tools(ALL_TOOLS)


def call_llm(state: AgentState) -> dict:
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", call_llm)
graph_builder.add_node("tools", ToolNode(ALL_TOOLS))
graph_builder.set_entry_point("agent")
graph_builder.add_conditional_edges(
    "agent", should_continue, {"tools": "tools", END: END}
)
graph_builder.add_edge("tools", "agent")

graph = graph_builder.compile()
