from flask import Flask
from flask import render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/home')
def home_page():

    username = request.args.get('username')
    password = request.args.get('password')

    if username and password:
        return render_template('home.html', username=username)
    else:
        return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)

