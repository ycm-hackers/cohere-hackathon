import subprocess
import os
from dotenv import load_dotenv
import cohere
from weaviate import Client, AuthClientApiKey

def send_query(query_text, cohere_client, weaviate_client):
    # Generate embeddings using Cohere
    embedding_response = cohere_client.embed(model="baseline-shrimp", texts=[query_text])

    # Check if the embedding was successful
    if embedding_response is None or len(embedding_response.embeddings) == 0:
        return None

    embedding = embedding_response.embeddings[0]

    # Query Weaviate using the embeddings
    response = weaviate_client.query.query(query_text, embedding)

    return response if response.status_code == 200 else None

def format_response(response_json):
    responses = []
    if response_json and "data" in response_json:
        for response in response_json["data"]:
            responses.append(response["text"])
    else:
        responses.append("I'm sorry, I couldn't fetch the data.")
    return ' '.join(responses)

def main():
    # Load environment variables
    load_dotenv()

    # Get environment variables
    cohere_api_key = os.getenv("COHERE_API_KEY")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    weaviate_url = os.getenv("WEAVIATE_URL")

    # Initialize Cohere client
    cohere_client = cohere.Client(cohere_api_key)

    # Initialize Weaviate client
    weaviate_client = Client(weaviate_url, AuthClientApiKey(api_key=weaviate_api_key))

    ticker = input("Enter the ticker for the company you want to crawl: ").upper()
    subprocess.run(["python", "ingest.py", ticker])
    
    print("Crawl finished. You can now chat with the data.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response_json = send_query(user_input, cohere_client, weaviate_client)
        print(format_response(response_json))

if __name__ == "__main__":
    main()
