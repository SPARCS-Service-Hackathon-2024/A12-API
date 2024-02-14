from src.dalle import return_dalle_response
from src.openai_chatbot import return_chatbot_response, chatting_history
from src.text2speech import convert_text_to_mp3
from src.speech2text import convert_mp3_to_text
import io
from time import time

def get_mp3_based_on_text(info:dict):
    """
    info = {
        "user": str,   #사용자 이름 (고유값)
        "mp3": wav, #mp3 데이터, 현재는 wav파일 주소
        "first_chatting": boolean  #해당 사용자가 처음 대화를 시작하는지의 여부
    }
    
    """
    
    time_start = time()

    if info['first_chatting']:
        chat_history.reset_history_list(info['user'])
    
    #mp3정보를 text로 변환
    info_str = convert_mp3_to_text(info['mp3'])
    
    time_audio2text = time()

    #text정보를 통해 답변 생성
    response_str = return_chatbot_response(info_str=info_str, history_list=chat_history.get_history_list(info['user']))    
    
    time_text2response = time()

    #history정보 업데이트
    chat_history.update_history_list(response_str, user = info['user'])
    
    #답변을 mp3로 변환
    audio = convert_text_to_mp3(response_str, "test_response.wav")
    
    time_text2audio = time()

    print("====================")
    print(response_str)
    print("===================")
    print(f"text2audio {time_text2audio-time_text2response}")
    print(f"respone {time_text2response-time_audio2text}")
    print(f"audio2text {time_audio2text-time_start}")


if __name__=="__main__":

    chat_history = chatting_history()

    info = {
        "user": "jonghyo",
        "mp3": "test.wav",
        "first_chatting": True
    }

    get_mp3_based_on_text(info)