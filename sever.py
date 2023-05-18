from flask import Flask, render_template, session, request , redirect, url_for,jsonify
from datetime import datetime
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from werkzeug.security import generate_password_hash,check_password_hash
import requests
import openai

chat_records = {}



import eventlet
eventlet.monkey_patch()

app = Flask(__name__,template_folder="temp")
socketio = SocketIO(app)
app.config['SECRET_KEY'] = "bruh"
openai.api_key = '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'




db= sqlite3.connect('temp\data\loginDetail.db') 
cur=db.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        password TEXT
    )
''')
cur.execute('''
    CREATE TABLE IF NOT EXISTS chat_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        sender TEXT,
        room TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
db.commit()
# 提交更改


# 关闭连接
db.close()



@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = request.form.get('id')
        password = request.form.get('password')
        print('zzz')
        try:
            # Connect to the database
            db = sqlite3.connect('temp\data\loginDetail.db')
            cur = db.cursor()
            cur.execute('SELECT * FROM users WHERE id=?', (id,))
            user = cur.fetchone()

            if user and check_password_hash(user[3], password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                return 'success'
            else:
                return 'failure'
        except Exception as e:
            error = 'An error occurred while accessing the database'
            print(str(e))
            return render_template('login.html', error=error)
        finally:
            if db:
                db.close()

    return render_template('login.html')



@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        print(f"id: {id}, username: {name}, email: {email}, password: {password}")
        
        try:
            db = sqlite3.connect('temp\data\loginDetail.db')
            cur = db.cursor()
            cur.execute("INSERT INTO users (id, name, email, password) VALUES (?, ?, ?, ?)",
            (id, name, email, hashed_password))

            db.commit()
            return 'success'
        except Exception as e:
            error = 'An error occurred while accessing the database'
            print(str(e))
            return render_template('register.html', error=error)
        finally:
            if db:
                db.close()

    return render_template('register.html')




@app.route("/check_duplicate_id", methods=['POST'])
def check_duplicate_id():
    id = request.form.get('id')

    try:
           db = sqlite3.connect('temp/data/loginDetail.db')
           cur = db.cursor()
           cur.execute('SELECT * FROM users WHERE id=?', (id,))
           existing_user = cur.fetchone()
           db.close()

           if existing_user:
            return 'duplicate_id'
           else:
            return 'success'

    except sqlite3.Error as e:
        print("Error accessing the database:", str(e))
        return 'error'
# 2

@app.route("/main")
def main():
   
    return render_template("chat.html")

@app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    # 连接到 SQLite 数据库
    db = sqlite3.connect('temp\data\loginDetail.db')
    cur = db.cursor()
    cur.execute

    # 执行查询获取最近二十条聊天记录
    cur.execute('SELECT message, sender FROM chat_records ORDER BY id DESC LIMIT 20')
    chat_history = cur.fetchall()
    print('zzzzz')
    # 关闭数据库连接
    cur.close()
    db.close()

    # 将聊天记录转换为字典列表，以便进行 JSON 序列化
    chat_history_dict = [{'sender': row[1]+":",'message': row[0]} for row in chat_history]

    return jsonify(chat_history=chat_history_dict)



@socketio.on('message')
def handleMessage(msg):
    print("收到: " + msg)
    room = session.get('room')
    if room:
        # 获取发送消息的用户名
        username = session.get('username')
        # 构建聊天记录对象
        record = {'username': username, 'message': msg, 'timestamp': datetime.now()}
        # 将聊天记录添加到房间的记录列表中
        chat_records.setdefault(room, []).append(record)
        # 广播消息给房间内的所有用户
        emit('message', record, room=room)
        emit('chat_history_updated', chat_records.get(room, []), room=room)

    else:
        print('User not in a room')

# 4
@socketio.event
def sendMsg(message):
    print(message)
    username = session.get('username', 'Unknown User')
    Room_name=message['room']
    emit('SendtoAll', {"msg":message["msg"], "user":username}, to=Room_name)
    db = sqlite3.connect('temp/data/loginDetail.db')
    cur = db.cursor()
    cur.execute("INSERT INTO chat_records (message, sender, room) VALUES (?, ?, ?)", (message["msg"], username, message["room"]))
    db.commit()
    db.close()
    

@socketio.event
def joinRoom(message):
    room_number=message['room']
    print(message)
    session['room_number'] = room_number
    join_room(room_number)
    
    session['room_number'] = room_number
    username = session.get('username', 'Unknown User')
    emit("roomJoined", {
        "user" : username,
        "room" : message['room']
    }, to=message['room'])

@socketio.event
def leaveRoom(message):
    Room_name=message['room']
    print(message)
    username = session.get('username', 'Unknown User')
    emit('roomLeftPersonal', {"room": message['room'], "user": username})
    leave_room(Room_name)
    emit('roomLeft', {"room":message['room'], "user":username}, to=message['room'])



if __name__ == "__main__":
    app.run( debug=True, threaded=True)
    socketio.run(app)
  