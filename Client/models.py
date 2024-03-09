from flask_mail import Message
from flask import current_app, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from Client.Api import mail

db = SQLAlchemy()


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), unique=True, index=True)
    email_verified = db.Column(db.Boolean, default=False)
    last_login_ip = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_confirmation_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return None
        return User.query.get(data['user_id'])

    def send_confirmation_email(user):
        token = user.generate_confirmation_token()
        msg = Message('Confirm Your Account', sender='your-email@example.com', recipients=[user.email])
        msg.body = f'''To confirm your account, visit the following link:
    {url_for('confirm_email', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
        mail.send(msg)