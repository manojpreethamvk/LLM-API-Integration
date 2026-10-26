
import uuid
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="ContextBot",
    page_icon="💬",
    layout="centered"
)

st.title("💬 ContextBot")
st.caption("A context-aware AI chatbot powered by Google Gemini")

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Conversation")
    st.write("Your chat maintains its own conversation ID.")
    if st.button("New conversation"):
        st.session_state.conversation_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(
                    API_URL,
                    json={
                        "message": prompt,
                        "conversation_id":
                            st.session_state.conversation_id
                    },
                    timeout=30
                )

                if response.ok:
                    data = response.json()
                    reply = data["reply"]
                    st.markdown(reply)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reply
                    })

                else:
                    try:
                        detail = response.json().get(
                            "detail", "The request failed."
                        )
                    except ValueError:
                        detail = "The request failed."

                    st.error(f"Chatbot error: {detail}")

    except requests.Timeout:
        st.error("The request timed out. Please try again.")

    except requests.RequestException:
        st.error(
            "Cannot connect to the backend. "
            "Check that the FastAPI server is running."
        )
