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
    Classify the user's message into exactly ONE of these three categories:

    1. 'CONVERSATIONAL' — The message is a greeting, small talk, a general knowledge question (e.g., "what is finance", "what is GST", "explain inflation"), a follow-up to the conversation, or anything you can confidently answer WITHOUT looking up specific regulatory documents. When in doubt, prefer this category.

    2. A search query — The message is a specific compliance question about GST rates, MSME classification thresholds, Udyam registration process, GST return filing deadlines, the composition scheme limits, or MSME payment-delay protection (Section 15 MSMED Act / Section 43B(h)) that requires looking up current regulatory documentation. Output the refined search query.

    3. 'OUT_OF_SCOPE' — ONLY for messages completely unrelated to business, finance, or compliance (e.g., "write me a poem", "what's the capital of France", "help me debug Python code", "tell me a joke"). Even borderline finance/business questions should be CONVERSATIONAL, not OUT_OF_SCOPE.

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