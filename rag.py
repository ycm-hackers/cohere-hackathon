from langchain.chat_models import ChatCohere
from langchain.retrievers import CohereRagRetriever
from langchain.retrievers.weaviate_hybrid_search import WeaviateHybridSearchRetriever
from langchain.schema import Document
from dotenv import load_dotenv
import weaviate
import os

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=WEAVIATE_API_KEY,
    additional_headers={
        "X-Cohere-Api-Key": COHERE_API_KEY,
        "X-Openai-Api-Key": OPENAI_API_KEY,
    },
)

retriever = WeaviateHybridSearchRetriever(
    client=client,
    index_name="LangChain",
    text_key="text",
    attributes=[],
    create_schema_if_missing=True,
)

# PLACEHOLDER DOCS FOR TESTING
# docs = [
#     Document(
#         metadata={
#             "title": "Embracing The Future: AI Unveiled",
#             "author": "Dr. Rebecca Simmons",
#         },
#         page_content="A comprehensive analysis of the evolution of artificial intelligence, from its inception to its future prospects. Dr. Simmons covers ethical considerations, potentials, and threats posed by AI.",
#     ),
#     Document(
#         metadata={
#             "title": "Symbiosis: Harmonizing Humans and AI",
#             "author": "Prof. Jonathan K. Sterling",
#         },
#         page_content="Prof. Sterling explores the potential for harmonious coexistence between humans and artificial intelligence. The book discusses how AI can be integrated into society in a beneficial and non-disruptive manner.",
#     ),
#     Document(
#         metadata={"title": "AI: The Ethical Quandary", "author": "Dr. Rebecca Simmons"},
#         page_content="In her second book, Dr. Simmons delves deeper into the ethical considerations surrounding AI development and deployment. It is an eye-opening examination of the dilemmas faced by developers, policymakers, and society at large.",
#     ),
#     Document(
#         metadata={
#             "title": "Conscious Constructs: The Search for AI Sentience",
#             "author": "Dr. Samuel Cortez",
#         },
#         page_content="Dr. Cortez takes readers on a journey exploring the controversial topic of AI consciousness. The book provides compelling arguments for and against the possibility of true AI sentience.",
#     ),
#     Document(
#         metadata={
#             "title": "Invisible Routines: Hidden AI in Everyday Life",
#             "author": "Prof. Jonathan K. Sterling",
#         },
#         page_content="In his follow-up to 'Symbiosis', Prof. Sterling takes a look at the subtle, unnoticed presence and influence of AI in our everyday lives. It reveals how AI has become woven into our routines, often without our explicit realization.",
#     ),
# ]

# retriever.add_documents(docs)

docs = retriever.get_relevant_documents(
    "AI integration in society",
    score=True,
)


def _pretty_print(docs):
    for doc in docs:
        print(doc.metadata)
        print("\n\n" + doc.page_content)
        print("\n\n" + "-" * 30 + "\n\n")


##### COHERE RAG
# rag = CohereRagRetriever(llm=ChatCohere(cohere_api_key=os.getenv("COHERE_API_KEY")))
# _pretty_print(rag.get_relevant_documents("What is cohere ai?"))

# docs = rag.get_relevant_documents(
#     "Does langchain support cohere RAG?",
#     source_documents=[
#         Document(page_content="Langchain supports cohere RAG!"),
#         Document(page_content="The sky is blue!"),
#     ],
# )
_pretty_print(docs)
