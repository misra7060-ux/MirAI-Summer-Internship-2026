import streamlit as st
from google import genai
from dotenv import load_dotenv
import os

# ----------------------------
# Load API Key
# ----------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(page_title="AI Multiverse", page_icon="🤖")

st.title("🌍 AI Multiverse")
st.write("Talk with different AI Personalities!")

# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.title("Choose Personality")

personality = st.sidebar.selectbox(
    "Select",
    [
        "Common Indian Man",
        "Crazy Salman Khan Fan",
        "Little Boy",
        "Motivational Coach",
        "Software Engineer",
        "College Professor",
        "Stand-up Comedian",
        "Entrepreneur",
        "Friendly Teacher",
        "AI Assistant"
    ]
)

if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# ----------------------------
# Session State
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------
# Display Chat History
# ----------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------------------
# Chat Input
# ----------------------------
if prompt := st.chat_input("Type your message..."):

    # Save User Message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Personality Instruction
    instruction = f"""
You are acting as {personality}.
Always stay in character.
Reply according to that personality.
Keep your answers interesting and natural.
"""

    # Build Conversation History
    conversation = instruction + "\n\n"

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            conversation += f"User: {msg['content']}\n"
        else:
            conversation += f"Assistant: {msg['content']}\n"

    # Gemini Response
    with st.spinner("Thinking..."):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=conversation
            )

            answer = response.text

        except Exception as e:
            answer = f"Error: {e}"

    # Save AI Response
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

    # Display AI Response
    with st.chat_message("assistant"):
        st.markdown(answer)