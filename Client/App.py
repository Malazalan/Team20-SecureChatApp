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

import threading

from User import User
from Database import get_user, get_user_ids
from SocketComms import * # should maybe be changed but * works for now

app = Flask(__name__)
socketio = SocketIO(app)

app.secret_key = "very_secret_key" # TODO: this

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
        browser_fingerprint = request.form.get('browserFingerprint')
        if username and password:
            user = get_user(username)
            if user is not None:
                if user.validate_fingerprint(browser_fingerprint): #TODO: failure message
                    if user.password_correct(password):
                        login_user(user)
                        return redirect(url_for('home_page'))
    return redirect(url_for('login_page')) # TODO: add failure message?

@app.route('/register/<target_user>/<invite_id>')
def register_page(target_user, invite_id):
    if current_user.is_authenticated:
         logout_user()
    invite = Database.get_invite(target_user)
    if invite and invite['invite_id']==invite_id and not get_user(invite['_id']):
        return render_template('register.html', username = target_user)
    return redirect(url_for('login_page')) #TODO: need error handling telling the user it was an invalid invite?
  
@app.route('/register_submit', methods = ['GET', 'POST'])
def register_function():
    if request.method == 'POST':
        password = request.form.get('password')

        browser_fingerprint = request.form.get('browserFingerprint') 
        username = request.headers.get('Referer').split('/')[-2]          
        email = "bleh@gmail.com"                                         
        
        user = get_user(username)
        if user is None:  
            Database.write_user(username, email, password, browser_fingerprint)
            Database.remove_invite(username) #TODO: could add error handling here in vase the function returns false
            user = get_user(username)
            if user is not None:
                login_user(user)
                return redirect(url_for('home_page'))
    return redirect(url_for('register_page')) #TODO: add error handling for if user is not none and this happens

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
def handle_message_sent(data):
    app.logger.info(f"{data['username']} has sent {data['message']} to {data['target']}")

    try:
        #SocketComms.py stuff
        #the line below is here just as a test to see if the lines below that will fail the try 
        prepare_message("Alice", "Bob", f"{data['message']}", "", "")
        writeThread = threading.Thread(target=prepare_message, args=("Alice", "Bob", f"{data['message']}", "", ""))
        writeThread.start()
    except:
        print("Server stuff not working")

    socketio.emit('recieve_message', data, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)

