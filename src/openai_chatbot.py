from openai import OpenAI
from typing import List
import json
import os
import sys

############## this block is just for import moudles ######
current_path = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(current_path)
grand_path = os.path.dirname(parent_path)
sys.path.append(parent_path)
###########################################################
from src.dalle import return_dalle_response
from src.env import get_api_key
from src.text2speech import convert_text_to_mp3

OPENAI_API_KEY = get_api_key()
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = "You are someone who empathizes with other people's feelings. \
          Based on past conversation records, \
          you have to sympathize with the content and ask more about what happened in the past. \
          Ask if there was any memorable incident in the family unit. \
          Encourage them to ask each age group about their case."

def return_chatbot_response(info_str:str=None,
                            history_list:List=None) -> json:
    """
    history example:
    
    Answer 1: ~ \n
    Answer 2: ~ \n
    
    
    system 제약 조건에서 user의 질문에 assistant 기반으로 답변
    """
    history_str = ""
    for i, his in enumerate(history_list):
      history_str = history_str + f"Previous answer {i}: {his} \n"

    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": f"{SYSTEM}"},
        {"role": "user", "content": f"{info_str}"},
        {"role": "assistant", "content": f"{history_str}"},
    ]
    )
    output = response.choices[0].message.content
    
    return output


class chatting_history:
  def __init__(self) -> None:
    self.history = dict()
    self.correct_answer = dict() ## 이미지 + text + .wav 정보 저장하는 리스트

  def get_history_list(self, user:str):
    try:
      return self.history[user]
    except: #when no history exists
      return []
    
  def update_history_list(self, text:str, user:str):
    try:
      self.history[user].append(text)
    except:
      self.history[user] = [text]

  def reset_history_list(self, user:str):
    self.history[user] = []
  
  def validate_current_user_response(self, user:str, info_str:str):
    
    #정제된 답변 만들어야 함. 얘로 달리랑 더빙 할거임
    new_info_str = info_str

    if True:
      self.add_story(user, new_info_str)

    return None




  def add_story(self, user:str, info_str:str):
    
    #variable info_str in this function is processed user input!!!

    url = return_dalle_response(info_str)

    wav = convert_text_to_mp3(info_str, "test1.wav")

    try:
      self.correct_answer[user].append((info_str,url,wav))
    except:
      self.correct_answer[user] = [(info_str,url,wav)]


if __name__ == '__main__':

    #가족 구성원에 대한 대답

    input_example = "어제는 할아버지 생신이셔서 다같이 외식을 했어."
    history_example = [""]

    output = return_chatbot_response(input_example, history_example)
    print(output)