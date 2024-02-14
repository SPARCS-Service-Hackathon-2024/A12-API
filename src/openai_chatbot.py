from openai import OpenAI
from typing import List
import json

from src.env import get_api_key

OPENAI_API_KEY = get_api_key()
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = "You are someone who empathizes with other people's feelings. \
          Based on past conversation records, \
          you have to sympathize with the content and ask more about what happened in the past. \
          Ask if there was any memorable incident in the family unit."

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
    
    return {"respone": output}


class chatting_history:
  def __init__(self) -> None:
    self.history = dict()

  def get_history_list(self, user:str):
    try:
      return self.history[user]
    except: #when no history exists
      return []
    
  def update_history_list(self, text:str, user:str):
    try:
      self.history[user].append([text])
    except:
      self.history[user] = [text]

  def reset_history_list(self, user:str):
    self.history[user] = []



if __name__ == '__main__':

    #가족 구성원에 대한 대답

    input_example = "가족 단위 행사로는 설날, 명절에 윷놀이를 자주 했던 것 같아."
    history_example = ["어제는 할아버지 생신이셔서 다같이 외식을 했어."]

    output = return_chatbot_response(input_example, history_example)
    print(output)