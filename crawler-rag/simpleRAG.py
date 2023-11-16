import cohere
import weaviate
from dotenv import load_dotenv
import os
import numpy as np

# Load environment variables
load_dotenv()
cohere_api_key = os.getenv("COHERE_API_KEY")
weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

# Initialize Cohere client
print("Initializing Cohere client...")
cohere_client = cohere.Client(cohere_api_key)

# Initialize Weaviate client with Cohere API key for generative module
print("Initializing Weaviate client...")
weaviate_client = weaviate.Client(
    url=weaviate_url,
    auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key)
)

def check_schema():
    print("Checking Weaviate schema...")
    try:
        schema = weaviate_client.schema.get()
        if "Document" in [cls['class'] for cls in schema.get('classes', [])]:
            print("Document class found in schema.")
            return True
        else:
            print("Document class not found in schema. Please check the schema configuration.")
            return False
    except Exception as e:
        print(f"Error checking schema: {e}")
        return False

def create_schema():
    if not check_schema():
        print("Creating schema in Weaviate...")
        document_class_schema = {
            "class": "Document",
            "description": "A class to store documents with their embeddings",
            "properties": [
                {
                    "name": "text",
                    "dataType": ["text"],
                    "description": "The text of the document"
                },
                {
                    "name": "embedding",
                    "dataType": ["number[]"],
                    "description": "The Cohere-generated embedding of the document"
                }
            ]
        }
        try:
            weaviate_client.schema.create_class(document_class_schema)
            print("Schema created successfully.")
        except Exception as e:
            print(f"Error creating schema: {e}")

# Create schema
create_schema()

def delete_existing_data():
    print("Deleting existing data in Weaviate...")
    try:
        existing_data = weaviate_client.query.get("Document", ["id"]).do()
        for doc in existing_data["data"]["Get"]["Document"]:
            weaviate_client.data_object.delete(doc["id"], "Document")
            print(f"Deleted document with ID: {doc['id']}")
    except Exception as e:
        print(f"Error deleting existing data: {e}")

def check_and_load_data():
    if check_existing_data():
        delete_existing_data()
    load_sample_data()

def check_existing_data():
    print("Checking for existing data in Weaviate...")
    try:
        existing_data = weaviate_client.query.get("Document", ["text"]).do()
        if existing_data["data"]["Get"]["Document"]:
            print("Existing data found in Weaviate:")
            for doc in existing_data["data"]["Get"]["Document"]:
                print(f"- {doc['text']}")
            return True
        else:
            print("No existing data found in Weaviate.")
            return False
    except Exception as e:
        print(f"Error checking for existing data: {e}")
        return False

def load_sample_data():
    print("Loading sample data into Weaviate...")
    documents = [
        "Python is a high-level, interpreted programming language.",
        "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France."
    ]

    for doc in documents:
        embedding_response = cohere_client.embed(
            texts=[doc],
            model='embed-english-v3.0',
            input_type='search_document'
        )
        embedding = embedding_response.embeddings[0]
        try:
            response = weaviate_client.data_object.create(
                data_object={"text": doc, "embedding": embedding},
                class_name="Document"
            )
            print(f"Document added: {doc}, Response ID: {response}")
        except Exception as e:
            print(f"Error adding document '{doc}': {e}")

def chat_interface():
    print("Chat Interface. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Exiting chat interface.")
            break
        retrieve_documents(user_input)

def retrieve_documents(query):
    print(f"Retrieving documents for query: '{query}'")
    try:
        embedding_response = cohere_client.embed(
            texts=[query],
            model='embed-english-v3.0',
            input_type='search_query'
        )
        query_embedding = np.asarray(embedding_response.embeddings[0])

        generate_prompt = "Explain why this document is relevant: {text}"
        result = (
            weaviate_client.query
            .get("Document", ["text"])
            .with_additional({
                "generate": {
                    "singleResult": {
                        "prompt": generate_prompt
                    }
                }
            })
            .with_near_vector({"vector": query_embedding.tolist()})
            .do()
        )

        if not result["data"]["Get"]["Document"]:
            print(f"No relevant documents found for query: '{query}'.")
            return

        documents = result["data"]["Get"]["Document"]
        
        print("Generated Responses:")
        for doc in documents:
            generated_text = doc['_additional']['generate']['singleResult']
            print(f"Document: {doc['text']}, Generated Response: {generated_text}")
    except Exception as e:
        print(f"Error retrieving documents for query '{query}': {e}")

if __name__ == "__main__":
    check_and_load_data()
    chat_interface()
