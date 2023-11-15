from typing import Optional, Type, Union, Dict, Tuple
from langchain.tools.base import BaseTool, BaseModel
from langchain.pydantic_v1 import Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from tools.alpaca_tools.alpaca_api import AlpacaToolApi

class AlpacaCurrentPositionsSchema(BaseModel):
    query: str = Field("""Is an empty field that is not required""")

class AlpacaCurrentPositionsTool(BaseTool):
    name = "Alpaca Current Positions"
    description = """
        Run this tool to get the current positions in the portfolio
        """
    args_schema: Type[AlpacaCurrentPositionsSchema] = AlpacaCurrentPositionsSchema

    def _run(
        self,
        query,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        search_wrapper = AlpacaToolApi()
        print(query)
        
        return search_wrapper.get_all_positions()

    async def _arun(
        self,
        query,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("AlpacaCurrentPositionsTool does not support async")