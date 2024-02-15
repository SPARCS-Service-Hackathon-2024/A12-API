from langchain.chat_models import ChatOpenAI
from langchain.agents import tool
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent 
from langchain.agents import AgentExecutor
import sys
import os
import sys
import re
import numpy as np
############## this block is just for import modules ######
current_path = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(current_path)
grand_path = os.path.dirname(parent_path)
sys.path.append(parent_path)
###########################################################
from src.env import get_api_key

OPENAI_API_KEY = get_api_key()
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY,model_name = "gpt-3.5-turbo") #ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)

# define tools
#@tool
def quit(content: str) -> str:
    template = """
         If the given sentence includes words or sentences that wants to quit the conversation, return 1. Else, return 0. sentence: {sentence}
    """
    prompt = PromptTemplate.from_template(template)
    result = (llm.predict(prompt.format(sentence = content)))
    if result == 1:
        return 'isend'
    else:
        return 'ing'

"""
tools = [quit]

# create agent
system_message = SystemMessage(content="You are very powerful assistant. You ask some given questions.")

prompt = OpenAIFunctionsAgent.create_prompt(system_message=system_message)

agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# running the executor to fetch the 
import time
from time import time
start = time()
print(1)
res = agent_executor.run("I don't want to talk with you anymore.")
print(res)
end = time()
print(end - start)
#print(quit("Go away."))
"""

print(quit("I want to stop our conversation."))
