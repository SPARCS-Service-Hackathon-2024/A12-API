from src.dalle import return_dalle_response
from src.openai_chatbot import return_chatbot_response, chatting_history
from src.text2speech import convert_text_to_mp3
from src.speech2text import convert_mp3_to_text
import io
import time
import concurrent.futures
import asyncio
import threading

def background_task(user, info_str):
        chat_history.validate_current_user_response(user, info_str)


def get_mp3_based_on_text(info:dict):
    """
    info = {
        "user": str,   #사용자 이름 (고유값)
        "mp3": wav, #mp3 데이터,
        "text": str
        "first_chatting": boolean  #해당 사용자가 처음 대화를 시작하는지의 여부
        "is_text": boolean
    }
    
    """
    
    time_start = time.time()

    if info.get('first_chatting'):
        chat_history.reset_history_list(info.get('user'))
    
    #mp3정보를 text로 변환
    if info.get('is_text'):
        info_str = info.get('text')
    else:
        info_str = convert_mp3_to_text(info.get('mp3'))
    
    #text정보를 통해 답변 생성
    response_str = return_chatbot_response(info_str=info_str, history_list=chat_history.get_history_list(info.get('user')))    
    
    #history정보 업데이트
    chat_history.update_history_list(response_str, user = info.get('user'))
    
    
    thread = threading.Thread(target=background_task, args=(info.get('user'), info_str))
    thread.daemon = True
    thread.start()

    response = {
        "text": response_str,
    }
    
    time_text2audio = time.time()

    time.sleep(60)
    print(f"===========\n{chat_history.correct_answer}")

    print("====================")
    print(response_str)
    print("===================")
    print(f"total time spent {time_text2audio-time_start}")


if __name__=="__main__":

    chat_history = chatting_history()

    info = {
        "user": "jonghyo",
        "mp3": "test.wav",
        "is_text": False,
        "text": None,
        "first_chatting": True
    }

    get_mp3_based_on_text(info)