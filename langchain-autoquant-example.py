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
    # MarketauxTool(),
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
    memory = ConversationBufferMemory(memory_key="chat_history")
    llm = Cohere(cohere_api_key=COHERE_API_KEY)
    return initialize_agent(tools,
                            llm,
                            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                            verbose=True,
                            memory=memory,
                            handle_parsing_errors=True)

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




