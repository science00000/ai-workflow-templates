"""
Test LangGraph agent pipeline structure.
"""

import pytest
from agent.graph.support_graph import build_graph, AgentState


def test_graph_built():
    graph = build_graph()
    assert graph is not None


def test_agent_state():
    state = AgentState(
        message="Hello",
        intent="greeting",
        kb_results=[],
        response="Hi there!",
        confidence=0.95,
        needs_escalation=False,
        chat_history=[],
    )
    assert state["intent"] == "greeting"
    assert state["needs_escalation"] is False
