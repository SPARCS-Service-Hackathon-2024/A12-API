from openai import OpenAI
from typing import List
import json

OPENAI_API_KEY = "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"
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




if __name__ == '__main__':

    #가족 구성원에 대한 대답

    input_example = "나는 지금 가족과 함께 살고 있어."
    history_example = ""

    output = return_chatbot_response(input_example, history_example)
    print(output)