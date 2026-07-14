import os
import streamlit as st
import requests
import time
import uuid
import logfire
from dotenv import load_dotenv


# Load environment variables explicitly from the root directory
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)


# Initialize Logfire
try:
    token = os.getenv("LOGFIRE_TOKEN") or os.getenv("LOGFIRE_API_KEY")
    if not token:
        print("ERROR: LOGFIRE_TOKEN is empty or None!")
    logfire.configure(token=token)
    LOGFIRE_STATUS = "Connected & Tracing"
except Exception as e:
    print(f"Logfire Init Error in UI: {e}")
    LOGFIRE_STATUS = f"Standby (Error: {e})"


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Compliso.ai — GST & MSME Compliance Assistant",
    page_icon="⚖️",
    layout="wide",
)

# --- AVATARS ---
AI_AVATAR = "⚖️"
USER_AVATAR = "👤"

# --- DOMAIN TOPICS ---
COMPLISO_TOPICS = [
    "GST Registration",
    "GST Rate Slabs",
    "GST Returns & Due Dates",
    "GST Composition Scheme",
    "Udyam Registration",
    "MSME Payment Protection",
]

QUICK_PROMPTS = [
    "What is the GST composition scheme turnover limit?",
    "How do I register for Udyam?",
    "What are the GST return filing due dates?",
    "What protection does MSMED Act offer for delayed payments?",
    "What are the current GST rate slabs?",
]


# --- SESSION MANAGEMENT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    logfire.info(f"New User Session Created: {st.session_state.session_id}")

if "messages" not in st.session_state:
    st.session_state.messages = []


# --- SIDEBAR ---
with st.sidebar:
    st.title("⚖️ Compliso")
    st.caption("GST & MSME Compliance Copilot")
    st.markdown("---")

    # Topic coverage
    st.markdown("**I can help with:**")
    for topic in COMPLISO_TOPICS:
        st.markdown(f"• {topic}")

    st.markdown("---")
    st.success(f"Logfire: {LOGFIRE_STATUS}")
    st.info(f"Session: {st.session_state.session_id[:8]}")

    if st.button("🗑️ New Conversation", width="stretch", type="primary"):
        logfire.warn(f"Memory Wipe Triggered for session: {st.session_state.session_id}")
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("---")
    st.caption(
        "⚠️ Compliso provides informational guidance only. "
        "Always verify against the official GST portal or a qualified CA."
    )


# --- MAIN CHAT ---
st.title("⚖️ Compliso.ai")
st.caption("Your AI compliance copilot for Indian GST & MSME law")


# --- QUICK PROMPTS (shown when chat is empty) ---
if not st.session_state.messages:
    st.markdown("### 👋 Ask me anything about Indian GST & MSME compliance")
    cols = st.columns(2)
    for i, prompt in enumerate(QUICK_PROMPTS):
        col = cols[i % 2]
        with col:
            if st.button(prompt, key=f"quick_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()


# Display history
for message in st.session_state.messages:
    avatar = AI_AVATAR if message["role"] == "assistant" else USER_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about GST, MSME classification, Udyam registration..."):
    with logfire.span("User Chat Interaction", user_query=prompt, session_id=st.session_state.session_id):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)

        # Assistant Response
        with st.chat_message("assistant", avatar=AI_AVATAR):
            with st.status("🔍 Compliso is researching...", expanded=True) as status:
                try:
                    with logfire.span("Calling RAG Backend"):
                        base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                        url = f"{base_url}/query"
                        payload = {"q": prompt, "thread_id": st.session_state.session_id}
                        response = requests.post(url, json=payload, timeout=60)
                        data = response.json()

                    # Handle OUT_OF_SCOPE responses
                    intent = data.get("intent", "")
                    if intent == "OUT_OF_SCOPE":
                        status.update(label="⚠️ Outside compliance scope", state="complete", expanded=False)
                        out_of_scope_msg = (
                            "This question is outside my compliance expertise. "
                            "I can help with **GST, MSME classification, Udyam registration, "
                            "GST returns, composition scheme, and MSME payment protection**."
                        )
                        st.warning(out_of_scope_msg)
                        st.session_state.messages.append({"role": "assistant", "content": out_of_scope_msg})
                        st.stop()

                    # Show Reasoning Steps from Backend
                    steps = data.get("thought_process", [])
                    for step in steps:
                        st.write(f"⚙️ {step}")

                    status.update(label="✅ Answer ready", state="complete", expanded=False)

                    # --- SHOW SOURCES ---
                    sources = data.get("sources", [])
                    if sources:
                        with st.expander("📚 Sources & References"):
                            for i, source in enumerate(sources):
                                preview = source[:120].replace("\n", " ") + "..."
                                with st.expander(f"Reference {i+1}: {preview}"):
                                    st.info(source)

                except Exception as e:
                    logfire.error(f"UI-Backend Connection Failed: {e}")
                    status.update(label="❌ Connection failed", state="error")
                    st.error("Unable to reach Compliso backend. Please try again.")
                    st.stop()

            # Final Answer Streaming
            answer_placeholder = st.empty()
            full_answer = data.get("answer", "No response.")

            curr_text = ""
            for char in full_answer:
                curr_text += char
                answer_placeholder.markdown(curr_text + "▌")
                time.sleep(0.005)

            answer_placeholder.markdown(full_answer)
            st.session_state.messages.append({"role": "assistant", "content": full_answer})
            logfire.info("Chat cycle completed successfully.")

# --- BOTTOM DISCLAIMER ---
st.markdown("---")
st.caption(
    "⚠️ Compliso.ai provides informational guidance based on publicly available regulatory sources "
    "and is **not a substitute for a qualified Chartered Accountant, GST practitioner, or legal advisor**. "
    "Always verify time-sensitive figures against the official GST portal (gst.gov.in) or Udyam portal (udyamregistration.gov.in)."
)
