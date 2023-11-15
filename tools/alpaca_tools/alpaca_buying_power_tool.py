from typing import Optional, Type, Union, Dict, Tuple
from langchain.tools.base import BaseTool, BaseModel
from langchain.pydantic_v1 import Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from tools.alpaca_tools.alpaca_api import AlpacaToolApi

class AlpacaBuyingPowerSchema(BaseModel):
    query: str = Field("""Is an empty field that is not required""")

class AlpacaBuyingPowerTool(BaseTool):
    name = "Alpaca Buying Power"
    description = """
        Run this tool to determine the available buying power of the portfolio
        """
    args_schema: Type[AlpacaBuyingPowerSchema] = AlpacaBuyingPowerSchema

    def _run(
        self,
        query,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        search_wrapper = AlpacaToolApi()
        print(query)
        
        return search_wrapper.buying_power()

    async def _arun(
        self,
        query,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("AlpacaBuyingPowerTool does not support async")