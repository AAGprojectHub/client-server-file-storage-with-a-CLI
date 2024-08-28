from flask import Flask, request, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from functools import wraps
import os
import jwt
import datetime


app = Flask(__name__)
app.secret_key = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testapp.db'
db = SQLAlchemy(app)
app.app_context().push()


class file_name(db.Model):
    name = db.Column(db.String(100), nullable = False, primary_key=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)


db.create_all()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            response_text = 'No token'
            return response_text
        
        try:
            decoded_token = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            current_user = User.query.get(decoded_token['user_id'])
        except Exception as e:
            return jsonify({'message': 'Token error'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


@app.route('/', methods=["GET", "POST"])
@token_required
def download(current_user):
    if not 'file' in request.files:
        response_text = 'Нет файла'
        return response_text

    file = request.files.get('file')
    file_size = request.content_length
    target_path = os.path.join('storage/', file.filename)
    if file.filename == '':
        response_text = 'Пустое имя файла'
        return response_text
    else:
        with open(target_path, 'wb') as f:
            track_upload = file_size/100
            uploaded = 0
            i = 1
            while True:
                chunk = file.stream.read(4096)
                if not chunk:
                    break
                f.write(chunk)
                uploaded = uploaded + 4096
                if track_upload*i < uploaded:
                    print('Загрузка ',i,'% из 100%')
                    i+=1
        db.session.add(file_name(name = file.filename))
        db.session.commit()
        response_text = 'Успешная загрузка'
        return response_text


@app.route('/storage', methods=["GET", "POST"])
@token_required
def check_files(current_user):
    file_names = file_name.query.all()
    data = {}
    i=0
    for name in file_names:
        data[i] = name.name
        i+=1

    print(data)
    return jsonify(data)
    

@app.route('/storage/<path:filename>')
@token_required
def send_attachment(current_user,filename):
    print(filename)
    return send_from_directory('storage/', filename, as_attachment=True)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    data = request.get_json()
    login = data['login']
    password = data['password']
    if login and password:
        user = User.query.filter_by(login=login).first()
        if user and user.password==password:
            token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)}, app.secret_key, algorithm='HS256')
            response = {
                'message': 'Успешный вход',
                'token': token
            }
            return jsonify(response)
        else:
            response_text = 'Ошибка в логине или пароле'
            return response_text, 404
    response_text = 'Ошибка в логине или пароле'
    return response_text, 404


@app.route('/register', methods=['GET', 'POST'])
def register():
    data = request.get_json()
    login = data['login']
    password = data['password']
    if request.method == 'POST':
        db.session.add(User(login=login, password=password))
        db.session.commit()
        response_text = 'Успешная регистрация'
        return response_text


if __name__ == '__main__':
    app.run(debug=True)