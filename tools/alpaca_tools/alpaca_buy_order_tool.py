from typing import Optional, Type
from langchain.tools.base import BaseTool, BaseModel
from langchain.pydantic_v1 import Field
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from tools.alpaca_tools.alpaca_api import AlpacaToolApi

class AlpacaBuyOrderSchema(BaseModel):
    query: str = Field("""
        Should be a 2 value string seperated by a comma with the following values:
        1st value is `ticker` (A ticker symbol of the security to order. must be in all caps) 
        and the 2nd value is `quantity` (and integer amount of the security to purchase)
        """)

class AlpacaBuyOrderTool(BaseTool):
    name = "Alpaca Create Buy Order"
    description = """
        Run this function to execute a buy order at current market price
        """
    args_schema: Type[AlpacaBuyOrderSchema] = AlpacaBuyOrderSchema

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        search_wrapper = AlpacaToolApi()
        ticker, quantity = query.split(',')
        
        return search_wrapper.create_buy_market_order(params={"ticker": ticker, "quantity": quantity})

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("AlpacaBuyOrderTool does not support async")