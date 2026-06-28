"""The thinking engine: a minimal LangGraph graph over an OpenAI chat model."""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from langgraph.graph import START, MessagesState, StateGraph


class Mind:
    """A tiny language-model brain: give it text, get back a reply."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        llm = ChatOpenAI(model=model)

        def respond(state: MessagesState) -> dict:
            return {"messages": [llm.invoke(state["messages"])]}

        # One-node graph: user message in -> model reply out.
        self._graph = (
            StateGraph(MessagesState)
            .add_node("respond", respond)
            .add_edge(START, "respond")
            .compile()
        )

    def think(self, text: str) -> str:
        """Process a piece of text and return the model's reply."""
        result = self._graph.invoke({"messages": [{"role": "user", "content": text}]})
        return result["messages"][-1].content
