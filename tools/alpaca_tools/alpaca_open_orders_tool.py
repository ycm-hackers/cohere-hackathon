from typing import Optional, Type, Union, Dict, Tuple
from langchain.tools.base import BaseTool, BaseModel
from langchain.pydantic_v1 import Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from tools.alpaca_tools.alpaca_api import AlpacaToolApi

class AlpacaOpenOrdersSchema(BaseModel):
    query: str = Field("""Is an empty field that is not required""")

class AlpacaOpenOrdersTool(BaseTool):
    name = "Alpaca Open Orders"
    description = """
        Run this tool to retrieve all pending open orders
        """
    args_schema: Type[AlpacaOpenOrdersSchema] = AlpacaOpenOrdersSchema

    def _run(
        self,
        query,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        search_wrapper = AlpacaToolApi()
        print(query)
        
        return search_wrapper.get_all_open_orders()

    async def _arun(
        self,
        query,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("AlpacaOpenOrdersTool does not support async")