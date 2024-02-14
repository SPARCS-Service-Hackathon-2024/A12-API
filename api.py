from flask import Flask

from src.dalle import return_dalle_response
from src.openai_chatbot import return_chatbot_response, chatting_history
from src.text2speech import convert_text_to_mp3
from src.speech2text import convert_mp3_to_text
import io
from flask import Flask, send_file

app = Flask(__name__)


@app.route('/image')
def get_image_respone(info:dict):
    """
    info = {
        "user" : str
    }
    """
    
    url_list = []
    for history in chat_history.get_history_list(info['user']):
        url = return_dalle_response(info_str=history)
        url_list.append(url)
    
    image_url_list = {
        "respone": url_list
    }
    
    return image_url_list


@app.route('/chat')
def get_mp3_based_on_text(info:dict):
    """
    info = {
        "user": str,   #사용자 이름 (고유값)
        "mp3": wav, #mp3 데이터
        "first_chatting": boolean  #해당 사용자가 처음 대화를 시작하는지의 여부
    }
    
    """
    
    if info['first_chatting']:
        chat_history.reset_history_list(info['user'])
    
    #mp3정보를 text로 변환
    info_str = convert_mp3_to_text(info['mp3'])
    
    #text정보를 통해 답변 생성
    response_str = return_chatbot_response(info_str=info_str, history_list=chat_history.get_history_list(info['user']))    
    
    #history정보 업데이트
    chat_history.update_history_list(response_str, user = info['user'])
    
    #답변을 mp3로 변환
    audio = convert_text_to_mp3(response_str)
    
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    buffer.seek(0)
    
    response = {
        "text": response_str,
        "mp3": send_file(buffer, mimetype="audio/mpeg", as_attachment=True, attachment_filename="speech.wav")
    }
    
    return response
    

if __name__ == '__main__':
    chat_history = chatting_history()
    app.run(debug=True)