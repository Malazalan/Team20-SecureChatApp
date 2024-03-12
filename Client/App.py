from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_socketio import SocketIO

import importlib

import Database
importlib.reload(Database)
import User
importlib.reload(User)
import SocketComms
importlib.reload(SocketComms)

from User import User
from Database import get_user, get_user_ids

app = Flask(__name__)
socketio = SocketIO(app)

app.secret_key = "very_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

@app.route('/')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    return render_template('login.html')

@app.route('/home')
@login_required
def home_page():
    user_ids = get_user_ids(current_user)
    return render_template('home.html', user_ids=user_ids)

@app.route('/chat/<target_user_id>')
@login_required
def chat_page(target_user_id):
    target_user = get_user(target_user_id)
    if target_user is not None:
        return render_template('chat.html', target_user_id = target_user_id)
    return redirect(url_for('home_page'))

@app.route('/login', methods = ['GET', 'POST'])
def login_function():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            user = get_user(username)
            if user is not None:
                if user.password_correct(password):
                    login_user(user)
                    return redirect(url_for('home_page'))
    return redirect(url_for('login_page'))

@app.route('/logout')
@login_required
def logout_function():
    logout_user()
    return redirect(url_for('login_page'))
                    
@login_manager.user_loader
def load_user(username):
    return get_user(username)

@socketio.on('user_connect')
def handle_join_room_event(data):
    app.logger.info(f"{data['username']} has opened a chat with {data['target']} ")

@socketio.on('message_sent')
def handle_join_room_event(data):
    app.logger.info(f"{data['username']} has sent {data['message']} to {data['target']}")
    socketio.emit('recieve_message', data, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)

