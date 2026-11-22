from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from app.agents.graph import graph

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = graph.invoke({"messages": [HumanMessage(content=request.question)]})
    answer = result["messages"][-1].content
    return ChatResponse(answer=answer)
