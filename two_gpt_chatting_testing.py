from openai import OpenAI
from langchain.prompts import PromptTemplate
# from langchain.chat_models import ChatOpenAI # NO longer supported as of langchain==0.2.0
from langchain_community.chat_models import ChatOpenAI
from typing import List, Dict, Tuple
import json
import os
import sys
import re
import numpy as np
import requests
import time
############## this block is just for import moudles ######
current_path = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(current_path)
grand_path = os.path.dirname(parent_path)
sys.path.append(parent_path)
###########################################################
from src.env import get_api_key

OPENAI_API_KEY = get_api_key()
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = "너는 가족 사이의 소중함을 알고 있는 사람이야. 질문이 들어오면, 이에 대한 기억을 생성해야 해. \
          한국어로 말해야 해. 3줄 이상 말하지는 마."

def return_user_response(info_str:str=None,):
    """
    history example:
    
    Answer 1: ~ \n
    Answer 2: ~ \n

    system 제약 조건에서 user의 질문에 assistant 기반으로 답변
    """
    response = client.chat.completions.create(
    #model="gpt-4",
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": f"{SYSTEM}"},
        {"role": "user", "content": f"{info_str}"},
    ]
    )
    output = response.choices[0].message.content
    
    return output



def two_gpt_chatting(text:str,
                    url:str='https://ckkzfwkxjrrfknrj.tunnel-pt.elice.io/proxy/5001/chat',
                    is_first_chatting:bool=False,
                    loop:int=0):
    #입력으로 들어오는 text는 gpt 질문

    #gpt 질문 바탕 user가 text 생성
    text = return_user_response(text)

    print(f"Answer {loop}: {text}")

    start_time = time.time()

    data = {'user': 'jonghyo',
            'mp3': None,
            'text': text,
            'first_chatting': is_first_chatting,
            "is_text": True}

    #유저 답변 생성으로 gpt 질문 생성
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    end_time = time.time()

    print(f"\nRespone end in {end_time-start_time}\n")

    json_data = json.loads(response.text)
    text_info = json_data["text"]

    return text_info


if __name__=="__main__":
    num_iter = 10
    text = "안녕! 이번주에 특별한 활동이 있었니?"
    for i in range(num_iter):
        print(f"Question {i}: {text}\n")
        if i==0:
            text= two_gpt_chatting(text=text,
                                    is_first_chatting=True,
                                    loop=i)
        else:
            text = two_gpt_chatting(text=text,
                                    is_first_chatting=False,
                                    loop=i)
        

    print("sleeping start...")
    #time.sleep(300)

    data = {'user': 'jonghyo'}

    headers = {"Content-Type": "application/json"}
    response = requests.post("https://ckkzfwkxjrrfknrj.tunnel-pt.elice.io/proxy/5001/make_story", 
                            data=json.dumps(data), 
                            headers=headers)

    print("======================================")
    for res in response:
        print(res)
    print("------------------")