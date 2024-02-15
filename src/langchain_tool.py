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
from openai import OpenAI

OPENAI_API_KEY = get_api_key()
#llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY,model_name = "gpt-3.5-turbo") #ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)

# define tools
def quit2(content:str)->str:
    """
    input : 사용자 답변
    output : 종료 의미시 1 반환, 아니면 0 반환
    """
    SYSTEM = "너는 지금 사용자와 대화를 하고 있는 챗봇이야. 만약, 사용자가 이제 그만하자, 대화 그만하고 싶어, 대화 종료, 저리 가 등의 어감이 담긴 말을 하면 1을 반환하고, 그렇지 않으면 0을 반환해. \
                텍스트 없이 무조건 숫자 하나로만 답변해. 명삼해, 1 또는 0만 대답할 수 있어."
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"{SYSTEM}"},
        {"role": "user", "content": f"{content}"},
    ]
    )
    output = response.choices[0].message.content
    print(f"is end output: {output}")
    if '1' in output: #output == 1:
        return 'isend'
    elif '0' in output: #== 0:
        return 'ing'
    else:
        return 'quit return error'
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



# print(quit2("I want to stop our conversation."))
# print(quit2("I want to continue our conversation."))
#print(quit2("Go away"))
#print(quit2("이제 그만 할래"))
# print(quit2("이제 그만 할래"))
# print(quit2("이제 그만 할래"))

