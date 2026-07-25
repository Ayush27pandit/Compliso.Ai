"""
Tests for the planner node.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.agents.nodes.planner import planner_node
from app.agents.state import AgentState


class TestPlannerNode:
    """Tests for planner node intent classification."""

    def test_greeting_returns_conversational(self):
        """Test that greetings are classified as CONVERSATIONAL."""
        state = AgentState(
            messages=[{"role": "user", "content": "Hello!"}],
            current_query="",
            documents=[],
            plan=[],
            status="",
            final_answer=""
        )

        with patch("app.agents.nodes.planner.llm") as mock_llm:
            mock_llm.invoke.return_value.content = "CONVERSATIONAL"
            result = planner_node(state)

        assert result["current_query"] == "CONVERSATIONAL"
        assert "Conversational" in result["plan"][0]

    def test_compliance_query_returns_technical(self):
        """Test that compliance queries are classified as TECHNICAL."""
        state = AgentState(
            messages=[{"role": "user", "content": "What is the GST rate for gold?"}],
            current_query="",
            documents=[],
            plan=[],
            status="",
            final_answer=""
        )

        with patch("app.agents.nodes.planner.llm") as mock_llm:
            mock_llm.invoke.return_value.content = "GST rate for gold"
            result = planner_node(state)

        assert result["current_query"] == "GST rate for gold"
        assert "Technical" in result["plan"][0]

    def test_poem_request_returns_out_of_scope(self):
        """Test that unrelated requests are classified as OUT_OF_SCOPE."""
        state = AgentState(
            messages=[{"role": "user", "content": "Write me a poem about taxes"}],
            current_query="",
            documents=[],
            plan=[],
            status="",
            final_answer=""
        )

        with patch("app.agents.nodes.planner.llm") as mock_llm:
            mock_llm.invoke.return_value.content = "OUT_OF_SCOPE"
            result = planner_node(state)

        assert result["current_query"] == "OUT_OF_SCOPE"
        assert "Out of scope" in result["plan"][0]

    def test_history_included_in_prompt(self):
        """Test that conversation history is included in the prompt."""
        state = AgentState(
            messages=[
                {"role": "user", "content": "What is GST?"},
                {"role": "assistant", "content": "GST is Goods and Services Tax."},
                {"role": "user", "content": "What about MSME?"}
            ],
            current_query="",
            documents=[],
            plan=[],
            status="",
            final_answer=""
        )

        with patch("app.agents.nodes.planner.llm") as mock_llm:
            mock_llm.invoke.return_value.content = "CONVERSATIONAL"
            planner_node(state)

            # Check that the prompt includes history
            call_args = mock_llm.invoke.call_args
            prompt = call_args[0][0]
            assert "What is GST?" in prompt
            assert "GST is Goods and Services Tax." in prompt
