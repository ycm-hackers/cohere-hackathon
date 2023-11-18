#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from dotenv import load_dotenv


# In[ ]:


load_dotenv()


# In[ ]:


COHERE_API_KEY = os.environ['COHERE_API_KEY']


# In[ ]:


from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.llms import Cohere, OpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent


# In[ ]:


from tools import (
    MarketauxTool,
    SecTool,
    AlpacaBuyOrderTool,
    AlpacaBuyingPowerTool,
    AlpacaCurrentPositionsTool,
    AlpacaGainLossStatusTool,
    AlpacaOpenOrdersTool,
    AlpacaSellOrderTool
)


# In[ ]:


tools = [
    MarketauxTool(),
    SecTool(),
    AlpacaBuyOrderTool(),
    AlpacaBuyingPowerTool(),
    AlpacaCurrentPositionsTool(),
    AlpacaGainLossStatusTool(),
    AlpacaOpenOrdersTool(),
    AlpacaSellOrderTool()
]


# In[ ]:


def create_agent_chain():
    system_message = """
    You are a portfolio manager agent. Your job is the manage the stock portoflio based on latest financial news.
    Always understand buying power and current positions of the portfolio before performing trades actions on a stocks based 
    on your recommendations. 
    If you're sending a JSON payload that includes a calculation, perform the calculation in advance and only send the result.
    """

    FORMAT_INSTRUCTIONS = """To use a tool, please use the following format:
    '''
    Thought: Do I need to use a tool? Yes
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    '''

    When you have gathered all the information on a trading decision, just write the last thought to the user in the form of a response.

    '''
    Thought: Do I need to use a tool? No
    AI: [write last thought response]
    '''
    """

    SUFFIX = '''

    Begin!

    Previous conversation history:
    {chat_history}

    Instructions: {input}
    {agent_scratchpad}
    '''

    memory = ConversationBufferMemory(memory_key="chat_history")
    llm = Cohere(cohere_api_key=COHERE_API_KEY)
    return initialize_agent(tools,
                            llm,
                            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                            verbose=True,
                            memory=memory,
                            handle_parsing_errors=True,
                            agent_kwargs={
                                'system_message': system_message, 
                                'format_instructions': FORMAT_INSTRUCTIONS,
                                'suffix': SUFFIX
                            })


# In[ ]:


def prompt_chain(query, agent):
    print(agent.run(input=query))
    prompt = input("Whould you like to ask another question? ")
    prompt_chain(prompt)


# In[ ]:


def main():
    prompt = input("What do you want to know? ")
    agent = create_agent_chain()
    prompt_chain(prompt, agent)


# In[ ]:


if __name__ == "__main__":
    main()


# In[ ]:




