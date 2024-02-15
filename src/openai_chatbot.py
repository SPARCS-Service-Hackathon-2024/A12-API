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
langchain_chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY,model_name = "gpt-3.5-turbo")
client = OpenAI(api_key=OPENAI_API_KEY)

# SYSTEM = "You are someone who empathizes with other people's feelings. \
#           You have to answer current response based on the past conversation log. \
#           Ask if there was any memorable incident in the family unit in the past. \
#           You should ask for a past or probable event more than the one you're talking about now. \
#           Respone with language that same with question and length should between 2~4 sentence. \
#           If respone is not proper, ask to answer again."
SYSTEM = "You are someone who empathizes with other people's feelings. \
          You have to answer current response based on the past conversation log. \
          You should ask for a past or probable event more than the one you're talking about now. \
          Respone with language that same with question and length should between 2~4 sentence. \
          If respone is not proper, ask to answer again. Speak in Korean. \
          If the conversation has intensified to some extent, switch to a completely different topic."

def return_chatbot_response(info_str:str=None,
                            history_list:List=None,
                            question_list:List=None) -> json:
    """
    history example:
    
    Answer 1: ~ \n
    Answer 2: ~ \n
    
    system 제약 조건에서 user의 질문에 assistant 기반으로 답변
    """
    history_str = "Following information is about previous chatting log. \n"

    max_len = len(history_list)
    for i in range(max_len):
      if i >= 2:
          break
      history_str = history_str + f"# Answer Log {i}: {history_list[max_len-1-i]} \n \
                                    # Question Log {i}: {question_list[max_len-1-i]} \n"

    print(history_str)

    response = client.chat.completions.create(
    model="gpt-4",
    #model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": f"{SYSTEM}"},
        {"role": "user", "content": f"{info_str}"},
        {"role": "assistant", "content": f"{history_str}"},
    ]
    )
    output = response.choices[0].message.content
    
    return output


"""

history -> dict

user1 -> [ str, str, str, str ]
user2 

  question = 챗봇의 답변
  history = 사용자가 입력한 부분.
  info_str = 가장 최근 사용자가 입력한 텍스트 (history에도 포함되어있음)


"""


class chatting_history:
  def __init__(self) -> None:
    self.history = dict() #사용자가 입력한 로그
    self.question = dict() #챗봇이 답변한 로그
    self.correct_answer = dict() ## 이미지 + text + .wav 정보 저장하는 리스트
    self.correct_history = dict() # question과 부합하는 history들의 모음 
    self.correct_labels = dict() # correct_history들간의 유사성을 기반으로 묶어 라벨링

  def get_history_list(self, user:str) -> Tuple[Dict,Dict]:
    try:
      return self.history[user], self.question[user]
    except: #when no history exists
      return [], []
    
  def update_history_list(self, 
                          history_text:str, 
                          question_text:str,
                          user:str):
    try:
      self.history[user].append(history_text)
      self.question[user].append(question_text)
    except:
      self.history[user] = [history_text]
      self.question[user] = [question_text]

  def reset_history_list(self, user:str):
    self.history[user] = []
    self.question[user] = []
  
  def score_similar_context(self, text1, text2, choice=None, threshold = 0.6):
    """
    choice = ['qna', 'ana'] question and anwer간, answer와 answer간.
    output = 0 or 1
    """
    if choice == 'qna':
      score_template = """ 아래의 주어진 질문과 답변이 주어졌을때, 해당 답변이 주어진 질문에 대한 적절한 답변인지의 정도를
        0과 1 사이의 값으로 수치화해서 채점해주세요. 1이 완벽히 두 내용이 연결성이 있을 경우에 부여하는 점수이고, 0은 전혀 관련이 없을때 부여합니다. 점수만 말해주면 됩니다. 다른 말은 필요하지 않습니다.질문: {question}, 답변: {answer}""" 
    elif choice == 'ana':
      score_template = """ 아래의 주어진 두 내용은 각각 직전 발화와 현재 발화에 해당합니다. 현재 발화와 직전 발화가 비슷한 이야기를 하고있는지의 정도를
        0과 1 사이의 값으로 수치화해서 채점해주세요. 점수만 말해주면 됩니다. 다른 말은 필요하지 않습니다. 직전발화: {question}, 현재발화: {answer}""" 
    else:
      print('[EXCEPTION] INAVAILABLE CHOICE');return 0
      
    try:
      #print('text1 =', text1)
      #print('text2 =', text2)
      pattern =  r'\b\d+\.\d+\b|\b\d+\b'
      prompt = PromptTemplate.from_template(score_template)
      score = langchain_chat_model.predict(prompt.format(question=text1, answer = text2))
      score = float((re.findall(pattern, score))[0]) ##
      
      print(f'score = {score}')
    except:
      print(f'[EXCEPTION] score : {score}')

    return  1 if score >= threshold else 0

  def return_summarized_responses(self, content:str):
    """
    input : 사용자 답변들(비슷한 맥락의)
    output : 요약된 답변

    말투 / 문장 수 제한
    """
    SYSTEM = "너는 다른사람이 들려주는 이야기를 잘 요약해주는 사람이야. 그리고 너는 이야기의 핵심적인 흐름을 잘 파악하는 사람이야. 너는 항상 최대 두 문장으로 너무 길지 않게 답변해. \
      너는 아이에게 책을 읽어주는 말투로 이야기해."

    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": f"{SYSTEM}"},
        {"role": "user", "content": f"{content}"},
    ]
    )
    output = response.choices[0].message.content
    
    return output


  
  def validate_current_user_response(self, user:str, info_str:str):
      threshold = 0.6
      #정제된 답변 만들어야 함. 얘로 달리랑 더빙 할거임
      new_info_str = info_str

      # 1) 올바른 답변인지 검증 -> output = 0/1
      #gpt에게 질문과 답변 쌍을 수고 질문에 대한 적절한 답인지를 묻는다?  langchain // gpt 
    
      result = self.score_similar_context(self.question[user][-1], info_str, choice = 'qna')

      #올바른 답변이라면, 이미지 더빙하기에 적합한 텍스트 설명문장 요약/생성 -> user_chat을 바탕으로 output = 상황에 적합한 더빙
      #user chatting input이 들어온 상황에서 사람이 어떤 이미지를 소개하는 듯한 문장이 생성되어야 함.
      if(result):
          new_info_str = self.return_summarized_responses(new_info_str)
          print('SUMMARIZED: ', new_info_str)
          self.add_story(user, new_info_str)

      return None   


      #   try:
      #     result2 = self.score_similar_context(self.correct_history[user][-1], info_str, choice = 'ana')
      #     self.correct_history[user].append(info_str) # 현재 답변이 올바른 답변이므로 추가
      #   except:
      #     self.correct_history[user] = [info_str] # = self.history[user][-1]     
      #     result2 = -1

      #   #print(f"result2: {result2}, info_str: {info_str}")

      #   # 비슷한 맥락이면 동일 label, 다르면 새로운 label
      #   if result2 == 1:   
      #     self.correct_labels[user].append(self.correct_labels[user][-1])

      #     #비슷한 내용 많으면 쪼개기
      #     if len(self.correct_labels[user])>=3:
      #       self.correct_labels[user].append(self.correct_labels[user][-1] + 1) # 1만큼 라벨 증가 
      #       # 새로운 label을 받은 경우, 그전까지(같은 라벨인 동안)를 묶어서 -> 요약/생성 시킴(=new_info_str)
      #       labels= np.array(self.correct_labels[user][:-1])
      #       histories = np.array(self.correct_history[user][:-1])
      #       new_info_lst = histories[labels == self.correct_labels[user][-2]]
      #       new_info_str = ' '.join(new_info_lst)
      #       new_info_str = self.return_summarized_responses(new_info_str)

      #       print('SUMMARIZED: ', new_info_str)
      #       self.add_story(user, new_info_str)  

      #   elif result2 == -1:
      #     self.correct_labels[user] = [0] #시작값 = 0
      #   else:
      #     self.correct_labels[user].append(self.correct_labels[user][-1] + 1) # 1만큼 라벨 증가 
      #     # 새로운 label을 받은 경우, 그전까지(같은 라벨인 동안)를 묶어서 -> 요약/생성 시킴(=new_info_str)
      #     labels= np.array(self.correct_labels[user][:-1])
      #     histories = np.array(self.correct_history[user][:-1])
      #     new_info_lst = histories[labels == self.correct_labels[user][-2]]
      #     new_info_str = ' '.join(new_info_lst)
      #     new_info_str = self.return_summarized_responses(new_info_str)

      #     print('SUMMARIZED: ', new_info_str)
      #     self.add_story(user, new_info_str)  
      # else:
      #   print('Not matched')

      # return None


  def add_story(self, user:str, info_str:str):
    
    #variable info_str in this function is processed user input!!!

    #지금은 dalle prompt를 상황 더빙 문장이 들어가는데, 키워드로 테스트할 필요성 다분 -> 괜찬
    url = return_dalle_response(info_str)

    print("=============")
    print(url)
    print("================")

    wav = convert_text_to_mp3(info_str, "test1.wav")

    try:
      self.correct_answer[user].append((info_str,url,wav))
    except:
      self.correct_answer[user] = [(info_str,url,wav)]


if __name__ == '__main__':

    #가족 구성원에 대한 대답

    input_example = "10년 전에 부모님의 결혼기념일이 생각나네. 그때 양복을 입고 계신 모습들이 예뻣어."
    history_example = ["어제는 할아버지 생신이셔서 다같이 외식을 했어.",
                        "제작년에 할머니 환갑잔치를 갔어.",
                        "가족이 다함께 맛있는 국수를 먹어서 좋았어."
                        ]
    question_example = ["예전에 가족들이 있었을 때 기억에 남는 사건이 있었나요? 어떤 일이 있었는지 궁금해요.",
                        "제작년에 가족들과 함께 보냈던 할머니의 환갑잔치는 아주 특별한 시간이었겠네요. 그날 있었던 특별하거나 기억에 남는 일이 있었는지 말씀해주실 수 있나요?",
                        "다함께 국수를 먹는 그 날도 특별했겠지만, 그 이외의 기억에 남는 가족 단위의 사건이 있었나요? 예를 들어, 누군가의 생일, 일주년, 결혼식, 이사 등을 생각해볼 수 있겠네요."]

    output = return_chatbot_response(input_example,
                                     history_example,
                                     question_example)
    print(output)


    # input_example = "어제 할아버지 생신이셔서 오랜만에 다같이 외식을 했어."
    # history_example = [ "최근에 BTS 노래 새로 나왔는데 진짜 명곡이더라", "나는 그 친구랑 십년전에 절교했어.","걔는 내가 너무 질투난대.",
    #   "할아버지가 많이 편찮으시대", "요즘엔 할아버지를 자주 봽지 못해서 아쉬웠어.", "어제는 할아버지 생신이셔서 다같이 외식을 했어."]
    # question_example = ["아하 노래듣는거 좋아하는 구나. 요즘에 영화는 뭐있지?", "그렇구나. 유진이는 너랑 왜 절교한거야?",
    #   "가족분들은 건강하셔?", "어머나 걱정이 되겠다. 할아버지는 자주 만나는 편이야?", "정말 아쉬웠겠네.. 최근에 할아버지를 마지막으로 본게 언제야?"]
    # correct_history_example = ["노래듣는거 되게 좋아해. 최신음악도 자주 들어.", "나는 컴퓨터공학과에서 공부중이야.", "나는 해커톤에서 개발할때 너무 행복해!"]
    # correct_labels_example = [0, 0, 1]

    # history = {'yoo':history_example, 'za': history_example}
    # question = {'yoo':question_example, 'za': history_example}
    # correct_history = {'yoo' : correct_history_example}
    # correct_labels = {'yoo': correct_labels_example}
    
    # test.history['yoo'] = history['yoo']
    # test.question['yoo'] = question['yoo']
    # test.correct_history['yoo'] = correct_history['yoo']
    # test.correct_labels['yoo'] = correct_labels['yoo']

    # test.history['za'] = history['za']
    # test.question['za'] = question['za']
    
    # #test.validate_current_user_response('yoo', input_example)
