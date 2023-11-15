import os
import cohere
import weaviate
from dotenv import load_dotenv

from tools.sec_tool import SecToolAPI
from rag_co import augment_prompt

load_dotenv()
co_api_key = os.getenv('COHERE_API_KEY')
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
weaviate_url = os.getenv("WEAVIATE_URL")

weaviate_client = weaviate.Client(
    url=weaviate_url,
    auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key),
    additional_headers={
        "X-Cohere-Api-Key": co_api_key,
    },
)
co = cohere.Client(co_api_key)

sec = SecToolAPI()

RAG = True
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
            if RAG:
                # message = augment_prompt(message, co, weaviate_client, k=3, use_rerank=True)
                message, src = sec.retrieve(message)
                srcs = "\n\nsource:\n" + src

            # Generate a response with the current chat history
            response = co.chat(
                message,
                model="command-light",
                temperature=0.8,
                chat_history=chat_history
            )
            answer = response.text
            if RAG:
                answer += srcs

            # Print the bot's response to the terminal
            print("Chatbot: " + answer)

            # Add message and answer to the chat history
            user_message = {"role": "USER", "message": message}
            bot_message = {"role": "CHATBOT", "message": answer}
            chat_history.append(user_message)
            chat_history.append(bot_message)

    except Exception as e:
        print(f"An error occurred: {e}")
