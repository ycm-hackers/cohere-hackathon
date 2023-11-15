import streamlit as st

# Title of the app
st.title("Ask the SEC")

# Persistent state to store chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# TODO: delete - For testing purposes
def my_chat_function(input):
    return f"{input}? You got that right!"

# TODO: delete - For testing purposes
def set_stock(symbol):
    print(symbol)

# Ticker input
st.header("Please enter the stock symbol")
symbol = st.text_input(label="symbol",key="symbol")
if symbol:
    set_stock(symbol)

# Text input for user message
user_input = st.chat_input("Your Message", key="user_input")



# Button to send message
if user_input:
    # Here, integrate with your backend script
    response = my_chat_function(user_input)  # example function call
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Bot", response))

# Display chat history
for user, message in st.session_state.chat_history:
    st.text(f"{user}: {message}")


