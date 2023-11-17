import streamlit as st
from langchain_autoquant import create_agent_chain


# Title of the app
st.title("Ask the SEC")

agent = create_agent_chain()
# tickers = ""

# Create a placeholder
placeholder = st.empty()


# Persistent state to store chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Prompt LLM Agent
def my_chat_function(input):
    # Display a loading message
    placeholder.text('Loading data... Please wait.')
    return agent.run(input=input)

# Set ticker symbol
# def set_stock(symbol):
#     tickers = symbol

# Ticker input
# st.header("Please enter the stock symbol")
# symbol = st.text_input(label="symbol",key="symbol")
# if symbol:
#     set_stock(symbol)

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


