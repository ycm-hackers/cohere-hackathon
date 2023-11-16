#main.py
import subprocess
import os
import logging
from dotenv import load_dotenv
import cohere
import weaviate

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_query(query_text, cohere_client, weaviate_client):
    logging.info("Sending query to Cohere and Weaviate.")
    # Generate embeddings using Cohere
    embedding_response = cohere_client.embed(model="baseline-shrimp", texts=[query_text])

    # Check if the embedding was successful
    if embedding_response is None or len(embedding_response.embeddings) == 0:
        logging.error("Failed to generate embedding.")
        return None

    embedding = embedding_response.embeddings[0]

    # Query Weaviate using the embeddings
    response = weaviate_client.query.get(
        "ClassName",  # Replace with your class name
        ["properties"]  # Replace with the properties you want to retrieve
    ).with_near_vector(embedding).do()

    return response if response else None

def format_response(response_json):
    logging.info("Formatting response.")
    responses = []
    if response_json and "data" in response_json:
        for response in response_json["data"]["Get"]["ClassName"]:  # Adjust according to your class name
            responses.append(response["properties"])  # Adjust according to your properties
    else:
        responses.append("I'm sorry, I couldn't fetch the data.")
    return ' '.join(responses)

def main():
    logging.info("Starting main function.")
    # Load environment variables
    load_dotenv()

    # Get environment variables
    cohere_api_key = os.getenv("COHERE_API_KEY")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    weaviate_url = os.getenv("WEAVIATE_URL")

    # Initialize Cohere client
    cohere_client = cohere.Client(cohere_api_key)
    logging.info("Cohere client initialized.")

    # Initialize Weaviate client
    weaviate_client = weaviate.Client(
        url=weaviate_url,
        auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key)
    )
    logging.info("Weaviate client initialized.")

    ticker = input("Enter the ticker for the company you want to crawl: ").upper()
    subprocess.run(["python", "ingest.py", ticker])
    
    logging.info("Crawl finished. You can now chat with the data.")

    print("Welcome to the chatbot. Type your message and press enter to chat. Type 'exit' to end the conversation.")
    chat_history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            logging.info("Exiting the program.")
            break

        # Generate a response with the current chat history
        response = cohere_client.chat(
            user_input,
            model="command-light",
            temperature=0.8,
            chat_history=chat_history
        )
        answer = response.text

        print("Chatbot: " + answer)

        # Add message and answer to the chat history
        user_message = {"role": "USER", "message": user_input}
        bot_message = {"role": "CHATBOT", "message": answer}
        chat_history.append(user_message)
        chat_history.append(bot_message)

if __name__ == "__main__":
    main()
