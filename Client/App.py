from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_socketio import SocketIO
import importlib
import os
import Database
importlib.reload(Database)
import User
importlib.reload(User)
import SocketComms
importlib.reload(SocketComms)

from User import User
from Database import get_user, get_user_ids
from SocketComms import * # should maybe be changed but * works for now

app = Flask(__name__)
socketio = SocketIO(app, max_http_buffer_size=10000000)

app.secret_key = "very_secret_key" # TODO: this

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'


if os.path.exists("cert.pem") and os.path.exists("key.pem"):
    ip_addr = "https://team20.joe-bainbridge.com/"
else:
    ip_addr = "http://127.0.0.1:5000"

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
        return render_template('chat.html', target_user_id = target_user_id, ip_addr=ip_addr)
    return redirect(url_for('home_page'))

@app.route('/login', methods=['POST'])
def login_post():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        browser_fingerprint = request.form.get('browserFingerprint')
        if username and password:
            user = get_user(username)
            if user is not None:
                if user.validate_fingerprint(browser_fingerprint):
                    if user.password_correct(password):
                        login_user(user)
                        return redirect(url_for('home_page'))
    # 如果登录验证失败，则重定向到登录页面，并附带 loginFailed 参数
    return redirect(url_for('login_page', loginFailed=True))

@app.route('/register/<target_user>/<invite_id>')
def register_page(target_user, invite_id):
    if current_user.is_authenticated:
         logout_user()
    invite = Database.get_invite(target_user)
    if invite and invite['invite_id']==invite_id and not get_user(invite['_id']):
        return render_template('register.html', username = target_user)
    return redirect(url_for('login_page')) 

@app.route('/register_submit', methods = ['GET', 'POST'])
def register_function():
    if request.method == 'POST':
        password = request.form.get('password')

        browser_fingerprint = request.form.get('browserFingerprint') 
        username = request.headers.get('Referer').split('/')[-2]          
        email = "bleh@gmail.com" #TODO: remove all refrences to email in all the files - it is not used anymore                                      
        
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
    Database.set_room(current_user.get_id(), request.sid) # For extra privacy, could this be stored in the servers memory?

@socketio.on('disconnect')
def handle_disconnect_event():
    Database.set_room(current_user.get_id(), None) # For extra privacy, could this be stored in the servers memory?
   
@socketio.on('message_sent')
def handle_message_sent(data):
    app.logger.info(f"{data['username']} has sent {data['message']} to {data['target']}") #this is temporary
    target = get_user(data['target'])
    if target:
        sender_room = request.sid
        target_room = target.current_room
        if target_room is not None:
            socketio.emit('recieve_message', data, room=sender_room)
            socketio.emit('recieve_message', data, room=target_room)
        else:
            failure_data = data
            failure_data['message'] = "Message failed to send, target user not online"
            socketio.emit('recieve_message', data, room=sender_room)
           
@socketio.on('file_sent')
def handle_file_sent(data):
    file = data['suitable_name'] # would not work just being called 'file', so i figured this was the next best name
    file_name = data['file_name']

    if True: # TODO: Input checking on file maybe?
        print("2")
        target = get_user(data['target'])
        if target:
            sender_room = request.sid
            target_room = target.current_room
            if target_room is not None:
                socketio.emit('recieve_file', {
                    'username': data['username'],
                    'target': data['target'],
                    'file': file,
                    'file_name': file_name,

                }, room=sender_room)
                socketio.emit('recieve_file', {
                    'username': data['username'],
                    'target': data['target'],
                    'file': file,
                    'file_name': file_name,

                }, room=target_room)              
            else:
                failure_data = data
                failure_data['message'] = "File failed to send, target user not online"
                socketio.emit('recieve_message', data, room=sender_room)
        
if __name__ == '__main__':
    if os.path.exists("cert.pem") and os.path.exists("key.pem"):
        socketio.run(app, debug=True, ssl_context=('cert.pem', 'key.pem'), port=443)
    else:
        socketio.run(app, debug=True)

        

