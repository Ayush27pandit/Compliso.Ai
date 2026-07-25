"""
Pytest fixtures for Compliso tests.
"""

import pytest
from app.agents.state import AgentState


@pytest.fixture
def sample_state():
    """Create a sample AgentState for testing."""
    return AgentState(
        messages=[{"role": "user", "content": "What is the GST rate for gold?"}],
        current_query="",
        documents=[],
        plan=[],
        status="",
        final_answer=""
    )


@pytest.fixture
def empty_state():
    """Create an empty AgentState for testing."""
    return AgentState(
        messages=[],
        current_query="",
        documents=[],
        plan=[],
        status="",
        final_answer=""
    )


@pytest.fixture
def conversation_state():
    """Create a state with conversation history."""
    return AgentState(
        messages=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hello! How can I help you with GST or MSME compliance?"},
            {"role": "user", "content": "What is the GST rate for gold?"}
        ],
        current_query="",
        documents=[],
        plan=[],
        status="",
        final_answer=""
    )
