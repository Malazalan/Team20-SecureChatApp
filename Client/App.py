from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager
from Database import get_user

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods = ['GET', 'POST'])
def login_function():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            user = get_user(username)
            if user is not None:
                if user.password_correct(password):
                    return render_template('home.html', username=username)
        
    return redirect(url_for('login_page'))

@login_manager.user_loader
def load_user(username):
    return get_user(username)

if __name__ == '__main__':
    app.run(debug=True)

