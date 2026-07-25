"""
Compliso Guardrails - LangGraph Integration
Wraps the existing LangGraph agent with guardrails checks.
"""

from typing import Dict, Any, List, Optional
from app.agents.state import AgentState
from guardrails.actions.custom_actions import GuardrailsManager, guardrails_manager
import logfire


class GuardrailsWrapper:
    """Wrapper that adds guardrails to the LangGraph agent."""

    def __init__(self, manager: Optional[GuardrailsManager] = None):
        self.manager = manager or guardrails_manager

    def check_input(self, state: AgentState) -> Dict[str, Any]:
        """Check input rails before processing."""
        if not state.get("messages"):
            return {"safe": True}

        latest_message = state["messages"][-1].get("content", "")
        return self.manager.check_input(latest_message)

    def filter_retrieval(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter retrieved chunks through retrieval rails."""
        return self.manager.filter_retrieval(chunks)

    def check_output(self, response: str, sources: List[str]) -> Dict[str, Any]:
        """Check output rails after generating response."""
        return self.manager.check_output(response, sources)

    def get_safe_response(self, rail_type: str) -> str:
        """Get a safe fallback response for blocked content."""
        responses = {
            "input": "I can only help with GST, MSME, and compliance questions. Please ask about tax filing, registration, or regulatory matters.",
            "output": "I apologize, but I cannot provide that response. Please ask a specific compliance question about GST, MSME registration, or tax filing.",
            "retrieval": "I found relevant information, but I cannot verify the sources. Please check the official GST portal (gst.gov.in) for the most current information.",
        }
        return responses.get(rail_type, responses["output"])


class GuardrailsAgent:
    """Agent with integrated guardrails."""

    def __init__(self, graph, wrapper: Optional[GuardrailsWrapper] = None):
        self.graph = graph
        self.wrapper = wrapper or GuardrailsWrapper()

    def invoke(self, input_data: Dict[str, Any], config: Optional[Dict] = None) -> Dict[str, Any]:
        """Invoke agent with guardrails."""
        state = input_data if isinstance(input_data, dict) else {"messages": [input_data]}

        # Input rails check
        input_check = self.wrapper.check_input(state)
        if not input_check.get("safe", True):
            logfire.info("Input blocked by guardrails")
            return {
                "messages": state.get("messages", []),
                "final_answer": self.wrapper.get_safe_response("input"),
                "status": "blocked_by_input_rails",
                "blocked": True,
            }

        # Run the graph
        with logfire.span("Agent Execution (with guardrails)"):
            result = self.graph.invoke(input_data, config)

        # Output rails check
        if result.get("final_answer") and result.get("documents"):
            output_check = self.wrapper.check_output(
                result["final_answer"],
                result.get("documents", [])
            )
            if not output_check.get("safe", True):
                logfire.info("Output blocked by guardrails")
                result["final_answer"] = self.wrapper.get_safe_response("output")
                result["status"] = "blocked_by_output_rails"
                result["blocked"] = True

        return result

    async def ainvoke(self, input_data: Dict[str, Any], config: Optional[Dict] = None) -> Dict[str, Any]:
        """Async invoke agent with guardrails."""
        state = input_data if isinstance(input_data, dict) else {"messages": [input_data]}

        # Input rails check
        input_check = self.wrapper.check_input(state)
        if not input_check.get("safe", True):
            logfire.info("Input blocked by guardrails")
            return {
                "messages": state.get("messages", []),
                "final_answer": self.wrapper.get_safe_response("input"),
                "status": "blocked_by_input_rails",
                "blocked": True,
            }

        # Run the graph
        with logfire.span("Agent Execution (with guardrails)"):
            result = await self.graph.ainvoke(input_data, config)

        # Output rails check
        if result.get("final_answer") and result.get("documents"):
            output_check = self.wrapper.check_output(
                result["final_answer"],
                result.get("documents", [])
            )
            if not output_check.get("safe", True):
                logfire.info("Output blocked by guardrails")
                result["final_answer"] = self.wrapper.get_safe_response("output")
                result["status"] = "blocked_by_output_rails"
                result["blocked"] = True

        return result


def wrap_graph_with_guardrails(graph):
    """Wrap a LangGraph graph with guardrails."""
    return GuardrailsAgent(graph)
