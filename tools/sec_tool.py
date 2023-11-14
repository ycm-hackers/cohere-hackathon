from langchain.chat_models import ChatCohere
from langchain.retrievers import CohereRagRetriever
from langchain.retrievers.weaviate_hybrid_search import WeaviateHybridSearchRetriever
from langchain.schema import Document
import weaviate
import os
from dotenv import load_dotenv
import requests
import json
from typing import Optional, Type
from langchain.tools.base import BaseTool, BaseModel
from langchain.pydantic_v1 import Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

# Load environment variables
load_dotenv()

class SecToolSchema(BaseModel):
    query: str = Field(description="A string query")

class SecTool(BaseTool):
    name = "Marketaux"
    description = """
        Use to retrieve relevant SEC financial statements
        """
    args_schema: Type[SecToolSchema] = SecToolSchema

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        search_wrapper = SecToolAPI()
        
        return search_wrapper.retrieve(query)

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("SecTool does not support async")

# Constants
class SecToolAPI:
    def __init__(self):
        WEAVIATE_URL = os.getenv("WEAVIATE_URL")
        WEAVIATE_API_KEY = weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))
        COHERE_API_KEY = os.getenv("COHERE_API_KEY")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        if WEAVIATE_URL is None:
            raise Exception('WEAVIATE_URL is not a defined environment variable')
        if WEAVIATE_API_KEY is None:
            raise Exception('WEAVIATE_API_KEY is not a defined environment variable')
        if COHERE_API_KEY is None:
            raise Exception('COHERE_API_KEY is not a defined environment variable')
        if OPENAI_API_KEY is None:
            raise Exception('OPENAI_API_KEY is not a defined environment variable')

        self.client = weaviate.Client(
            url=WEAVIATE_URL,
            auth_client_secret=WEAVIATE_API_KEY,
            additional_headers={
                "X-Cohere-Api-Key": COHERE_API_KEY,
                "X-Openai-Api-Key": OPENAI_API_KEY,
            },
        )

    def retrieve(self, query: str):
        """Fetch market news and return a summary."""
        retriever = WeaviateHybridSearchRetriever(
            client=self.client,
            index_name="LangChain",
            text_key="text",
            attributes=[],
            create_schema_if_missing=True,
        )

        docs = retriever.get_relevant_documents(
            query,
            score=True,
        )

        return self._pretty_print(docs)

    def _pretty_print(self, docs):
        for doc in docs:
            print(doc.metadata)
            print("\n\n" + doc.page_content)
            print("\n\n" + "-" * 30 + "\n\n")