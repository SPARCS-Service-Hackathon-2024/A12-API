from flask import Flask

from src.dalle import return_dalle_response
from src.openai_chatbot import return_chatbot_response
from src.text2speech import *

app = Flask(__name__)


@app.route('/image')
def get_image_respone():
    
    image_url_list = {
        "respone": []
    }
    
    return image_url_list


@app.route('/chat')
def get_mp3_based_on_text(info:dict):
    
    info_str = None
    
    #mp3정보를 text로 변환
    info_str = convert_mp3_to_text(info)
    
    #text정보를 통해 답변 생성
    response_str = return_chatbot_response(info_str=info_str, history_list=get_history_list())    
    
    #history정보 업데이트
    update_history_list(respone_str)
    
    #답변을 mp3로 변환
    response_mp3 = return_mp3_respone(response_str)
    
    response = {
        "text": response_str,
        "mp3": response_mp3
    }
    
    return response
    

if __name__ == '__main__':
    app.run(debug=True)