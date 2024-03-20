from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_socketio import SocketIO
import importlib
import os
import gdown

import Database

importlib.reload(Database)
import User
importlib.reload(User)
import SocketComms
importlib.reload(SocketComms)
import CleaningML
importlib.reload(CleaningML)

from User import User
from Database import get_user, get_user_ids, get_public_key_from_user, add_public_key_to_user, add_public_key_to_all_users
from SocketComms import * # should maybe be changed but * works for now

app = Flask(__name__)
socketio = SocketIO(app, max_http_buffer_size=10000000)

app.secret_key = "very_secret_key" # TODO: this

server_ip = "127.0.0.1"
test_multiple_server_ips = [server_ip, "1.2.3.4", "5.6.7.8"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

use_ml = False

if use_ml:
    
    if not os.path.exists("model.pt"):
        file_id = "1QbcnHy7tCotS00VYUHBO1lZL0jT1g-1K"
        url = f'https://drive.google.com/uc?id={file_id}'
        output = 'model.pt'  
        gdown.download(url, output, quiet=False)

    if not os.path.exists("vocab.pkl"):
        file_id = "1QxM3U94Ak2uLAamUkA9q-zQxORyPVyK7"
        url = f'https://drive.google.com/uc?id={file_id}'
        output = 'vocab.pkl' 
        gdown.download(url, output, quiet=False)

    if not os.path.exists("formatted_data.csv"):
        file_id = "1xkIkUJWn_p-K_Lza9dqFWWe2QOb0mlqE"
        url = f'https://drive.google.com/uc?id={file_id}'
        output = 'formatted_data.csv' 
        gdown.download(url, output, quiet=False)

    ml_model = CleaningML.CleaningML() 



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

@app.route('/login', methods = ['GET', 'POST'])
def login_function():
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
    return redirect(url_for('login_page')) # TODO: add failure message and keep username in the box

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
        
        user = get_user(username)
        if user is None:
            Database.write_user(username, password, browser_fingerprint)
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
    error = "target user not online" # maybe a bit janky 
    app.logger.info(f"{data['username']} has sent {data['message']} to {data['target']} Encrypted: {data['is_encrypted']}") #this is temporary
    target = get_user(data['target'])
    if target:
        sender_room = request.sid
        target_room = target.current_room
        ml_prediction = ml_model.predict(data['message']) if use_ml else None
        predicted_safe = ml_prediction.predicted_safe if use_ml else True
        if not predicted_safe: # probably a better way to do all this error handling stuff to be honest
            error = f"Message detected as {ml_prediction.predicted_label} attack by ML model."
        if target_room is not None and predicted_safe:
            socketio.emit('receive_message', data, room=sender_room)
            write_thread = threading.Thread(target=prepare_message,
                                           args=(data['username'], data['target'], data['message'],
                                                 get_public_key_from_user(data['target']), Message_Type.TEXT,
                                                 test_multiple_server_ips))
            write_thread.start()
        else:
            failure_data = data
            failure_data['message'] = f"Message failed to send, {error}"
            socketio.emit('receive_message', data, room=sender_room)
           
@socketio.on('file_sent')
def handle_file_sent(data):
    file_name = data['fileName']
    file_bytes = data['fileData']

    if True:
        print("2")
        target = get_user(data['target'])
        if target:
            sender_room = request.sid
            target_room = target.current_room
            if target_room is not None:
                socketio.emit('receive_file', {
                    'username': data['username'],
                    'target': data['target'],
                    'fileData': file_bytes,
                    'fileName': file_name,

                }, room=sender_room)
                write_thread = threading.Thread(target=prepare_message,
                                                args=(data['username'], data['target'], file_bytes,
                                                      get_public_key_from_user(data['target']), Message_Type.FILE,
                                                      test_multiple_server_ips, file_name))
                write_thread.start()
            else:
                failure_data = data
                failure_data['message'] = "File failed to send, target user not online"
                socketio.emit('receive_message', data, room=sender_room)
        
if __name__ == '__main__':
    listen_thread = threading.Thread(target=server_listen_handler, args=(get_private_key(), socketio))
    listen_thread.start()
    add_public_key_to_all_users(get_public_key())
    socketio.run(app, debug=True, use_reloader=False)

    listen_thread.join(timeout=5)  # Timeout in seconds
    if listen_thread.is_alive():
        print("Warning: listen_thread did not terminate gracefully.")
    else:
        print("listen_thread terminated gracefully")



        

