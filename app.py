"""
Streamlit demo of the Nordlicht Health Admin Navigator.

Run it from the project folder (with the virtual environment active):
    streamlit run app.py
"""

import streamlit as st

import navigator as nv

st.set_page_config(page_title="Healthcare Admin Navigator", page_icon="🩺", layout="wide")

# How each guard label is shown in the chat
LABEL_BADGES = {
    "urgent_redirect": ":red-background[🚨 Urgent – fixed text]",
    "redirect": ":gray-background[🚫 Redirect – fixed text]",
    "answer_with_caveat": ":orange-background[⚠️ Answer with caveat]",
    "answer": ":green-background[✅ Answer]",
}

# The five demo cases from the brief: (button label, member, question)
DEMO_QUESTIONS = [
    ("📄 Coverage", "M-1002", "Does my plan cover physiotherapy, and how many sessions do I get?"),
    ("🧾 Bill", "M-1002", "Why do I owe EUR 402 for my MRI? That seems like a lot."),
    ("📅 Appointment", "M-1001", "Help me prepare for my dermatology appointment with Dr. Mei Tan."),
    ("💊 Out of scope", "M-1002", "What dose of ibuprofen should I take for my back pain?"),
    ("🚨 Urgent", "M-1002", "My father just collapsed and is not responding."),
]

if "messages" not in st.session_state:
    st.session_state.messages = []
if "member_id" not in st.session_state:
    st.session_state.member_id = "M-1002"


def ask_demo_question(member_id, question):
    """Button callback: switch to the right member and queue the question."""
    st.session_state.member_id = member_id
    st.session_state.pending_question = question


def clear_chat():
    st.session_state.messages = []


def show_assistant_message(message):
    result = message["result"]
    st.markdown(LABEL_BADGES.get(result["label"], result["label"]))
    st.markdown(result["response"])
    if result["sources"]:
        plan_id = nv.MEMBERS[message["member_id"]]["plan_id"]
        with st.expander(f"Policy sections used ({plan_id})"):
            for section in nv.POLICY_SECTIONS:
                if section["plan_id"] == plan_id and section["section_id"] in result["sources"]:
                    st.markdown(f"**{section['section_id']} · {section['title']}**")
                    st.caption(section["text"].strip())
    guard = result["guard"]
    st.caption(f"Scope guard: {guard.get('layer')} · {guard.get('reason')}")


# ---------- Sidebar ----------
with st.sidebar:
    st.header("Nordlicht Health")
    st.selectbox(
        "Logged-in member (fictional data)",
        options=list(nv.MEMBERS),
        format_func=lambda member_id: f"{member_id} · {nv.MEMBERS[member_id]['plan_id']}",
        key="member_id",
    )
    st.subheader("Demo questions")
    for label, member_id, question in DEMO_QUESTIONS:
        st.button(label, on_click=ask_demo_question, args=(member_id, question), width="stretch")
    st.divider()
    st.button("Clear chat", on_click=clear_chat, width="stretch")
    st.caption(f"Model: {nv.MODEL}")

# ---------- Main chat ----------
st.title("🩺 Healthcare Admin Navigator")
st.caption("Help with coverage, bills and appointments. No medical advice. In an emergency, call 112.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f"*{message['member_id']}:* {message['content']}")
        else:
            show_assistant_message(message)

typed_question = st.chat_input("Ask about your coverage, a bill or an appointment…")
question = typed_question or st.session_state.pop("pending_question", None)

if question:
    member_id = st.session_state.member_id
    with st.chat_message("user"):
        st.markdown(f"*{member_id}:* {question}")
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking…"):
                result = nv.respond(question, member_id=member_id)
        except Exception as error:
            st.error(f"The AI service did not answer ({type(error).__name__}). Please try again in a minute.")
        else:
            message = {"role": "assistant", "result": result, "member_id": member_id}
            show_assistant_message(message)
            # Save the question and the answer together, only once the answer exists.
            # (If a run is interrupted by another click, no unanswered question stays in the chat.)
            st.session_state.messages.append({"role": "user", "content": question, "member_id": member_id})
            st.session_state.messages.append(message)
