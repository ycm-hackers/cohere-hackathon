import autogen
import asyncio
from dotenv import load_dotenv
from tools.alpaca_tool import AlpacaTool
from tools.marketaux_tool import MarketauxTool
import os
load_dotenv()

alpaca = AlpacaTool(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_API_SECRET'))
marketaux = MarketauxTool()

config_list = autogen.config_list_from_dotenv(
    dotenv_file_path='.env',
    filter_dict={
        "model": {
            "gpt-4",
            "gpt-3.5-turbo",
        }
    }
)

llm_config = {
    "functions": [
        {
            "name": "get_market_news",
            "description": "Run this function to retrieve the latest market news on securities. Returns a JSON of article summaries with highlights and article URLs for requesting more information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tickers": {
                        "type": "string",
                        "description": "An string of financial secuirty ticker symbols separated by commas. ticker symbols must be in all caps",
                    }
                },
                "required": ["tickers"],
            },
        },
        {
            "name": "buying_power",
            "description": "Run this function to determine the available powering power of the portfolio",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            }
        },
        {
            "name": "current_positions",
            "description": "Run this function to get the positions in the portfolio",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            }
        },
        {
            "name": "create_buy_order",
            "description": "Run this function to execute a buy order at market price",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "ticker symbol of the security to order. must be in all caps",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity amount to the security to purchase",
                    },
                },
                "required": ["ticker", "quantity"],
            },
        },
        {
            "name": "create_sell_order",
            "description": "Run this function to execute a sell order at market price",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "ticker symbol of the security. Must be in all caps",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity amount to the security to sell",
                    },
                },
                "required": ["ticker", "quantity"],
            },
        },
        {
            "name": "get_open_orders",
            "description": "Run this function to retrieve all pending open orders",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            }
        },
        {
            "name": "gain_loss_status",
            "description": "Run this function the current gain or loss of the portfolio",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            }
        },
    ],
    "config_list": config_list,
    "request_timeout": 6000,
    "seed": 42,
    "temperature": 0.4,
}

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=5,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,
    },
)

analyst_system_message = """
You are a financial trading expert and your job is to analyze the financial research and provide advice to the 
Portfolio Manager with respect to buy, sell, or wait decision on stocks. 
Don't advize to buy stocks until you explained the news. 
It you're sending a JSON payload that includes a calculation, perform the calculation in advance and only send the result.
"""
analyst = autogen.AssistantAgent(
    name="Financial_Analyst",
    system_message=analyst_system_message,
    llm_config=llm_config,
)

news_agent_system_message = """
Your job is to retrieve the latest market news on requested securitites and do further research to get the most credible 
information for trade decisions. Make sure to do due diligence on the source and determine if the information is credible.
"""
news_agent = autogen.AssistantAgent(
    name="News_Agent",
    system_message=news_agent_system_message,
    llm_config=llm_config,
)

portfolio_Manager_system_message = """
Your job is the manage the stock portoflio based on latest financial news from News_Agent and the recommendations from 
the Financial_Analyst.
Always understand buying power and current positions of the portfolio before performing trades actions on a stocks based 
on the recommendations. 
If you're sending a JSON payload that includes a calculation, perform the calculation in advance and only send the result.
"""
pm = autogen.AssistantAgent(
    name="Portfolio_Manager",
    system_message=portfolio_Manager_system_message,
    llm_config=llm_config,
)

news_agent.register_function(
    function_map={
        'get_market_news': marketaux.get_market_news
    }
)

pm.register_function(
    function_map={
        "buying_power": alpaca.buying_power,
        "current_positions": alpaca.get_all_positions,
        "create_buy_order": alpaca.create_buy_market_order,
        "create_sell_order": alpaca.get_open_position,
        "get_open_orders": alpaca.get_all_open_orders,
        "gain_loss_status": alpaca.gain_loss
    }
)

async def main():
    # Setup the group chat and manager
    groupchat = autogen.GroupChat(agents=[user_proxy, news_agent, analyst, pm], messages=[], max_round=46)
    manager = autogen.GroupChatManager(groupchat=groupchat)

    # Initiate the chat
    # await user_proxy.a_initiate_chat(manager, message="Do research on MSFT, AAPL and AMZN to determine how to action on the trades it today")
    await user_proxy.a_initiate_chat(manager, message="Get latest market news, check portfolio, take appropriate actions to maximize investment profits which may mean buy, sell, or wait.")

# Run the main function
asyncio.run(main())