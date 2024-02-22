from openai import OpenAI
import streamlit as st

st.title("🤖 Waiter Bot")

# Define predefined responses
responses = {
    "menu": "Sure! Here's our menu:\n- Appetizers: ...\n- Main Course: ...\n- Desserts: ...",
    "specials": "Our specials today are: ...",
    "bill": "Your total bill is $XX.XX.",
    # Add more predefined responses as needed
}

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Welcome! How can I assist you today?"}]

for msg in st.session_state.messages:
    st.text(msg["role"] + ": " + msg["content"])

if prompt := st.text_input("You:", key="user_input"):
    if prompt.lower() in responses:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": responses[prompt.lower()]})  # Change role to 'assistant'
    else:
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        client = OpenAI(api_key=openai_api_key)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "user", "content": prompt})  # Change role to 'user'
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
        generated_response = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": generated_response})  # Change role to 'assistant'
