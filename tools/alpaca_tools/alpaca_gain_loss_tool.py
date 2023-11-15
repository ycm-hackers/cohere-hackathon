from typing import Optional, Type, Union, Dict, Tuple
from langchain.tools.base import BaseTool, BaseModel
from langchain.pydantic_v1 import Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from tools.alpaca_tools.alpaca_api import AlpacaToolApi

class AlpacaGainLossStatusSchema(BaseModel):
    query: str = Field("""Is an empty field that is not required""")

class AlpacaGainLossStatusTool(BaseTool):
    name = "Alpaca Gain-Loss Status"
    description = """
        Run this tool to retrieve the current gain-loss status of the portfolio
        """
    args_schema: Type[AlpacaGainLossStatusSchema] = AlpacaGainLossStatusSchema

    def _run(
        self,
        query,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        alpaca_wrapper = AlpacaToolApi()
        print(query)

        return alpaca_wrapper.gain_loss()

    async def _arun(
        self,
        query,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("AlpacaGainLossStatus does not support async")