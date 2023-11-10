import cohere
import os
from dotenv import load_dotenv

load_dotenv() 
api_key = os.getenv('COHERE_API_KEY')
co = cohere.Client(api_key)

# Initialize the chat history
chat_history = []

print("Welcome to the chatbot. Type your message and press enter to chat. Type 'quit' to end the conversation.")

# Start a conversation loop
while True:
    try:
        # Get the user's message from the terminal
        message = input("User: ").strip()

        # End the conversation if the user types 'quit'
        if message.lower() == 'quit':
            print("Ending the conversation. Thank you for chatting!")
            break

        # Only send the message if it's not empty
        if message:
            # Generate a response with the current chat history
            response = co.chat(
                message,
                model="command-light",
                temperature=0.8,
                chat_history=chat_history
            )
            answer = response.text

            # Print the bot's response to the terminal
            print("Chatbot: " + answer)

            # Add message and answer to the chat history
            user_message = {"role": "USER", "message": message}
            bot_message = {"role": "CHATBOT", "message": answer}
            chat_history.append(user_message)
            chat_history.append(bot_message)

    except Exception as e:
        print(f"An error occurred: {e}")