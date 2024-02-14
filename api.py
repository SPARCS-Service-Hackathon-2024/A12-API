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

def background_task(user, info_str):
        chat_history.validate_current_user_response(user, info_str)


app = Flask(__name__)
# CORS(app, resources={r'*': {'origins': '*'}}, supports_credentials=True )


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite를 사용하고자 할 때
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'  # PostgreSQL을 사용하고자 할 때
db = SQLAlchemy(app)


  
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
        response_str = return_chatbot_response(info_str=info_str, history_list=chat_history.get_history_list(info.get('user')))    
        
        #history정보 업데이트
        chat_history.update_history_list(response_str, user = info.get('user'))
        

        thread = threading.Thread(target=background_task, args=(info.get('user'), info_str))
        thread.daemon = True
        thread.start()
        

        response = {
            "text": response_str,
        }
        
        return build_actual_response(jsonify(response), 200)



@app.route('/make_story', methods=['POST'])
def make_story():
    data = request.json

    user = data.get('user')

    story_list = chat_history.correct_answer #List[Tuple[str,url,.wav]]
    
    return jsonify({"story_list": story_list}), 200




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    yyyymmdd = db.Column(db.String(100), nullable=False)
    familyname = db.Column(db.String(100), nullable=False)
    familyposition = db.Column(db.String(100), nullable=False)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    yyyymmdd = data.get('yyyymmdd')
    familyname = data.get('familyname')
    familyposition = data.get('familyposition')

    if not (username and password and yyyymmdd and familyname and familyposition):
        return jsonify({'message': '모든 필드를 제대로 입력해주세요.'}), 400

    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': '이미 존재하는 사용자명입니다.'}), 400

    new_user = User(username=username, password=password, yyyymmdd=yyyymmdd, familyname=familyname, familyposition=familyposition)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '사용자 등록이 완료되었습니다.'}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({'message': 'Invalid username or password'}), 401
    
    # 사용자 정보 반환
    user_info = {
        'id': user.id,
        'username': user.username,
        'yyyymmdd': user.yyyymmdd,
        'familyname': user.familyname,
        'familyposition': user.familyposition
    }
    
    return jsonify({'message': '로그인이 성공적으로 완료되었습니다.', 'user_info': user_info}), 200



if __name__ == '__main__':
    chat_history = chatting_history()
    app.run(debug=True)