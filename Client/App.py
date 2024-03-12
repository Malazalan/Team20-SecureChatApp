from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from Database import get_user

app = Flask(__name__)

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
    return render_template('home.html')

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

if __name__ == '__main__':
    app.run(debug=True)

