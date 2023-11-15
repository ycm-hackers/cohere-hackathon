from typing import Optional, Type, Union, Dict, Tuple
from langchain.tools.base import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from tools.alpaca_tools.alpaca_api import AlpacaToolApi

class AlpacaGainLossStatusTool(BaseTool):
    name = "Alpaca Gain-Loss Status"
    description = """
        Run this tool to retrieve the current gain or loss of the portfolio
        """
    
    def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        return (), {}

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        search_wrapper = AlpacaToolApi()
        
        return search_wrapper.gain_loss()

    async def _arun(
        self,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("AlpacaGainLossStatus does not support async")