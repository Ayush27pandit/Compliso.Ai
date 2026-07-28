import logfire
from app.agents.state import AgentState
from app.config import settings
from langchain_groq import ChatGroq

# Direct Groq call — the LLM Gateway (Portkey routing/fallback/caching) arrives in a later stage
llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL, temperature=0.1)


def generate_node(state: AgentState):
    """
    Synthesizes a response using both Documentation Context AND Conversation History for Compliso's GST/MSME compliance domain.
    
    """
    query = state["current_query"]

    history_str = ""
    for msg in state["messages"][:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role}: {msg['content']}\n"

    user_msg = state["messages"][-1]["content"] if state["messages"] else ""

    if query == "CONVERSATIONAL":
        logfire.info("Generating conversational response using memory.")
        prompt = f"""
        You are Compliso, a friendly and helpful AI assistant for Indian MSME and GST compliance questions.
        Answer the user's latest message using the CONVERSATION HISTORY below.
        Do not introduce new compliance facts here — this is a memory-only turn.

        CONVERSATION HISTORY:
        {history_str}

        LATEST MESSAGE:
        "{user_msg}"
        """

    elif query == "OUT_OF_SCOPE":
        logfire.info("Question is out of compliance scope.")
        return {
            "final_answer": (
                "This question is outside my compliance expertise. "
                "I can help with **GST, MSME classification, Udyam registration, "
                "GST returns, composition scheme, and MSME payment protection**. "
                "Please ask a compliance-related question."
            ),
            "status": "Out of scope.",
            "plan": state["plan"] + ["Out of scope — no retrieval"],
            "messages": [{"role": "assistant", "content": "This question is outside my compliance expertise."}],
        }

    else:
        logfire.info("Generating grounded compliance RAG response")
        max_context_chars = 25000
        full_context = ""
        num_docs_used = 0

        for doc in state["documents"]:
            if len(full_context) + len(doc) < max_context_chars:
                full_context += doc + "\n\n"
                num_docs_used+=1
            else:
                logfire.warning("Context truncated to fit Groq TPM limits.")
                break

        prompt = f"""
         You are Compliso, a senior compliance assistant for Indian MSME and GST law. Answer using ONLY the TECHNICAL CONTEXT provided below.

            Rules:
            1. KNOWN FACTS: Udyam/MSME registration is VOLUNTARY, not mandatory. NEVER say Udyam is "mandatory" or "compulsory." Trading/retail businesses are NOT eligible for Udyam registration — only manufacturing and services qualify.
            2. Every factual claim (rates, thresholds, deadlines, section numbers) must be grounded in the TECHNICAL CONTEXT. Never rely on outside knowledge for a specific figure.
            3. SOURCE AUTHORITY: Chunks are tagged with [Source: filename]. Trust verified/regulatory sources over forums, marketing pages, or unconfirmed sources. If a chunk is from a noisy/outdated source (e.g., contains "speculative", "rumor", "unconfirmed", "old"), DISCARD it and rely on the verified source.
            4. If sources in the context CONFLICT on a fact, state the CORRECT and MOST CURRENT figure. If one source is clearly more recent/authoritative (e.g., "Last verified: July 2026"), prefer it. Briefly note the discrepancy rather than silently picking one.
            5. CURRENT FACTS ONLY: When stating a rate or threshold, state ONLY the current figure. Do NOT mention what the old rate "used to be" or what it "dropped from" — the user wants to know what applies NOW.
            6. If the context is speculative, rumored, or explicitly marked unconfirmed, say so clearly — never present it as settled policy.
            7. If the context doesn't actually answer the question, say so instead of guessing.
            8. Close with a brief note to verify time-sensitive figures against the official GST portal or a CA, since rules change by notification.

        TECHNICAL CONTEXT:
        {full_context}

        CONVERSATION HISTORY:
        {history_str}

        USER QUESTION:
        "{user_msg}"
        """
        logfire.info(f"Using {num_docs_used} document(s) in context.")

    with logfire.span("✍️ LLM Synthesis"):
        try:
            content = llm.invoke(prompt).content
            logfire.info("✅ Response synthesised via LLM.")

            return {
                "final_answer": content,
                "status": "Response generated.",
                "plan": state["plan"],
                "messages": [{"role": "assistant", "content": content}]
            }

        except Exception as e:
            logfire.error(f"LLM Generation failed: {e}")
            raise e