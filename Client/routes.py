from adodbapi.examples.db_print import db
from app import app
from flask import render_template, abort, redirect, url_for, flash, request
from flask_login import login_user

from Client.Forms import RegistrationForm, LoginForm
from Client.models import User


# Account Register Service
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(csrf_enabled=False)
    ip_address = request.remote_addr
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, last_login_ip=ip_address)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
    return render_template('register.html', title='Register', form=form)


# Account Login Service
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    current_ip = request.remote_addr
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # email or password incorrect
        if user is not None or user.check_password(form.password.data):
            flash(f'Error email or password!')
            return redirect(url_for('login'))
        # different ip address
        if user.last_login_ip != current_ip:
            flash(f'Not a common IP address, email verification is required!')
        return redirect(url_for('confirm_email', user_id=user.id))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)



# Confirmation of Email
@app.route('/confirm/<token>',methods=['GET','POST'])
def confirm_email(token):
    user = User.verify_confirmation_token(token)
    if not user:
        flash(f'That is an invalid or expired token')
        return redirect(url_for('index'))
    if user.email_verified:
        flash(f'Account already confirmed. Please login.')
    else:
        user.email_verified = True
        user.last_login_ip = request.remote_addr
        db.session.commit()
        flash(f'You have confirmed your account. Thanks!')
    return redirect(url_for('index'))



