from app.agents.state import AgentState
from app.config import settings
from langchain_groq import ChatGroq
import logfire

# Direct Groq call — the LLM Gateway (Portkey routing/fallback/caching) arrives in a later stage
llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL, temperature=0)

def planner_node(state: AgentState):
    """
    The Planner determines if a search is needed based on the ENTIRE conversation.
    """
    # Get the conversation history (excluding the latest message)
    history = ""
    for msg in state["messages"][:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"

    #extract the latest user message
    user_message = state["messages"][-1]["content"] if state["messages"] else ""

    prompt = f"""
    You are Compliso's intelligent Assistant Planner.
    Analyze the conversation history and the latest user message.

    CONVERSATION HISTORY:
    {history}

    LATEST MESSAGE:
    "{user_message}"

    Task:
    1. If the latest message is a greeting (hi, hello) or a question that can be answered using ONLY the conversation history above (e.g., "what turnover did I mention earlier"), respond with 'CONVERSATIONAL'.
    2. If it is a compliance question about GST, MSME classification, Udyam registration, GST return filing, the composition scheme, or MSME payment-delay protection that requires looking up current regulatory documentation, output a refined search query.
    3. If it is unrelated to Indian MSME/GST/compliance topics (e.g., general coding help, unrelated business advice, or any other domain), respond with 'OUT_OF_SCOPE'.

    Output ONLY 'CONVERSATIONAL', 'OUT_OF_SCOPE', or the search query.
    """

    with logfire.span("🧠 Planner Decision"):
        decision = llm.invoke(prompt).content.strip()
        logfire.info(f"Intent identified: {decision}")

    if decision == "CONVERSATIONAL":
        return {
            "current_query": "CONVERSATIONAL",
            "status": "Handling conversationally (using memory)...",
            "plan": ["Intent: Conversational/Memory", "Retrieval: Skipped"]
        }

    return {
        "current_query": decision,
        "status": f"Technical research needed. Searching for: {decision}",
        "plan": ["Intent: Technical", f"Search Term: {decision}"]
    }