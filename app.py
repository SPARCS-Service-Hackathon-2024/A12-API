from flask import Flask
import concurrent.futures
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from src.dalle import return_dalle_response
from src.openai_chatbot import return_chatbot_response, chatting_history
from src.text2speech import convert_text_to_mp3
from src.speech2text import convert_mp3_to_text
import io
from flask import Flask, send_file, make_response
import concurrent.futures
import asyncio
import threading
from flask_cors import CORS
import os

from db import db

def background_task(user, info_str):
        chat_history.validate_current_user_response(user, info_str)


app = Flask(__name__)
# CORS(app, resources={r'*': {'origins': '*'}}, supports_credentials=True )

db_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),"db.sqlite")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file  # SQLite를 사용하고자 할 때
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
db.app = app

with app.app_context():
    db.create_all()

  
def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response
    
def build_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/chat', methods=['POST', 'OPTIONS'])
def get_mp3_based_on_text():
    """
    info = {
        "user": str,   #사용자 이름 (고유값)
        "mp3": wav, #mp3 데이터,
        "text": str
        "first_chatting": boolean  #해당 사용자가 처음 대화를 시작하는지의 여부
        "is_text": boolean
    }
    
    """
    if request.method == 'OPTIONS': 
        return build_preflight_response()

    elif request.method == 'POST': 
        info = request.json
        print(info)

        if info.get('first_chatting'):
            chat_history.reset_history_list(info.get('user'))
        
        #mp3정보를 text로 변환
        if info.get('is_text'):
            info_str = info.get('text')
        else:
            info_str = convert_mp3_to_text(info.get('mp3'))
        
        #text정보를 통해 답변 생성
        prev_history_list, prev_question_list = chat_history.get_history_list(info.get('user'))
        response_str = return_chatbot_response(info_str=info_str, 
                                               history_list=prev_history_list,
                                               question_list=prev_question_list)    
        
        #history정보 업데이트
        chat_history.update_history_list(history_text=info_str, 
                                         question_text=response_str, 
                                         user = info.get('user'))
        

        thread = threading.Thread(target=background_task, args=(info.get('user'), info_str))
        thread.daemon = True
        thread.start()
        

        response = {
            "text": response_str,
        }
        
        return build_actual_response(jsonify(response))



@app.route('/make_story', methods=['POST','OPTIONS'])
def make_story():
    if request.method == 'OPTIONS': 
        return build_preflight_response()

    elif request.method == 'POST': 
        data = request.json

        user = data.get('user')

        story_list = chat_history.correct_answer #List[Tuple[str,url,.wav]]
        
        return build_actual_response(jsonify({"story_list": story_list}))


@app.route('/register', methods=['POST','OPTIONS'])
def register():
    if request.method == 'OPTIONS': 
        return build_preflight_response()

    elif request.method == 'POST': 
        data = request.json
        username = data.get('userName')
        password = data.get('password')
        yyyymmdd = data.get('birthday')
        familyname = data.get('familyName')
        familypassword = data.get('familyPassword')
        phonenumber = data.get('phoneNumber')

        #해야 하는 요소
        #1. name 중복 여부
        #2. familyname 존재 여부
        #2.1. 존재 시 password가 맞는지 여부
        #2.2. 존재 없으면 password 이거로 fix
        #3. email foramt

        if not (username and password and yyyymmdd and familyname and familypassword and phonenumber):
            return build_actual_response( jsonify({'message': 'fill all the blank'}))

        #1.
        user = User.query.filter_by(userName=username).first()
        if user:
            return build_actual_response(jsonify({'message': 'user already exist'}))


        #2.
        user_famliyname = User.query.filter_by(familyName=familyname).first()
        if user_famliyname:
            #2.1.
            user = User.query.filter_by(familyName=familyname).first()
            if not user:
                return build_actual_response(jsonify({'message': 'Invalid famliy password'}))


        new_user = User(userName=username, 
                        password=password, 
                        birthday=yyyymmdd, 
                        familyName=familyname, 
                        familyPassword=familypassword,
                        phoneNumber=phonenumber)
                    
        db.session.add(new_user)
        db.session.commit()

        return build_actual_response(jsonify({'message': '사용자 등록이 완료되었습니다.'}))


@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS': 
        return build_preflight_response()
    elif request.method == 'POST': 
        data = request.json
        phoneNumber = data.get('phoneNumber')
        password = data.get('password')
        
        if not phoneNumber or not password:
            return build_actual_response(jsonify({'message': 'Missing phoneNumber or password'}))
        user = User.query.filter_by(phoneNumber=phoneNumber, password=password).first()
        if not user:
            return build_actual_response(jsonify({'message': 'Invalid phoneNumber or password'}))
        
        # 사용자 정보 반환
        user_info = {
            'id': user.id,
            'userName': user.userName,
            'birthday': user.birthday,
            'familyName': user.familyName,
            'familyPassword': user.familyPassword,
            'phoneNumber': user.phoneNumber
        }
        
        return build_actual_response(jsonify({'message': '로그인이 성공적으로 완료되었습니다.', 'user_info': user_info}))



if __name__ == '__main__':
    chat_history = chatting_history()
    app.run(debug=False, port=5001)