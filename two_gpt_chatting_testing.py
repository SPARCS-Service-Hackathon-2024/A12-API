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
############## this block is just for import moudles ######
current_path = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(current_path)
grand_path = os.path.dirname(parent_path)
sys.path.append(parent_path)
###########################################################
from src.env import get_api_key

OPENAI_API_KEY = get_api_key()
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = "너는 가족 사이의 소중함을 알고 있는 사람이야. 질문이 들어오면, 이에 대한 기억을 생성해야 해."

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
                    api_url:str='http://example.com/api/endpoint',
                    is_first_chatting:bool=False):
    #입력으로 들어오는 text는 gpt 질문

    #gpt 질문 바탕 user가 text 생성
    text = return_user_response(text)

    data = {'user': 'jonghyo',
            'mp3': None,
            'text': text,
            'first_chatting': is_first_chatting,
            "is_text": True}

    #유저 답변 생성으로 gpt 질문 생성
    response = requests.post(url, data=data)

    return response.get('text')


if __name__=="__main__":
    two_gpt_chatting()