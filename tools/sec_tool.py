import os
from typing import Optional, Type
import weaviate
import cohere
from dotenv import load_dotenv
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.pydantic_v1 import Field
from langchain.retrievers.weaviate_hybrid_search import WeaviateHybridSearchRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever
from langchain.tools.base import BaseModel, BaseTool

# Load environment variables
load_dotenv()


class SecToolSchema(BaseModel):
    query: str = Field(description="A string query")


class SecTool(BaseTool):
    name = "SEC Tool"
    description = """
        Use to retrieve in depth factual financial statements released by the SEC
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


class SecToolAPI:
    def __init__(self):
        WEAVIATE_URL = os.getenv("WEAVIATE_URL")
        COHERE_API_KEY = os.getenv("COHERE_API_KEY")

        if WEAVIATE_URL is None:
            raise Exception("WEAVIATE_URL is not a defined environment variable")
        WEAVIATE_API_KEY = weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))
        if WEAVIATE_API_KEY is None:
            raise Exception("WEAVIATE_API_KEY is not a defined environment variable")
        if COHERE_API_KEY is None:
            raise Exception("COHERE_API_KEY is not a defined environment variable")

        self.client = weaviate.Client(
            url=WEAVIATE_URL,
            auth_client_secret=WEAVIATE_API_KEY,
            additional_headers={
                "X-Cohere-Api-Key": COHERE_API_KEY,
            },
        )
        self.co_client = cohere.Client(api_key=COHERE_API_KEY)
        self.rerank = CohereRerank(
            client=self.co_client, user_agent="langchain", cohere_api_key=COHERE_API_KEY
        )

    def retrieve(self, query: str, k: int = 3, max_str_len: int = 4080):
        """Fetch market news and return a summary."""
        retriever = WeaviateHybridSearchRetriever(
            client=self.client,
            index_name="DocText",
            k=k,
            text_key="orgText",
            attributes=["vector", "cik", "source"],
            create_schema_if_missing=False,
        )
        ccr = ContextualCompressionRetriever(
            base_retriever=retriever, base_compressor=self.rerank
        )
        docs = ccr.get_relevant_documents(
            query,
        )
        res = "\n".join([doc.page_content for doc in docs])[0:max_str_len]
        source = docs[0].metadata["source"]

        return f"""Contexts:{res}\nQuery:{query}.""", source

    def _pretty_print(self, docs):
        for doc in docs:
            print(doc.metadata)
            print("\n\n" + doc.page_content)
            print("\n\n" + "-" * 30 + "\n\n")


# if __name__ == "__main__":
#     sec = SecToolAPI()
#     print(sec.retrieve("What is Apple's core business in 2022?"))
