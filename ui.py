import streamlit as st

# Title of the app
st.title("Ask the SEC")

# Persistent state to store chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Text input for user message
user_input = st.text_input("Your Message", key="user_input")

# Button to send message
if st.button("Send"):
    # Here, integrate with your backend script
    response = my_chat_function(user_input)  # example function call
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Bot", response))

# Display chat history
for user, message in st.session_state.chat_history:
    st.text(f"{user}: {message}")
