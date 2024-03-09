# config.py
import os


class Config:
    # 通用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_default_secret_key'

    # Flask-Mail 配置
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


def config():
    return None