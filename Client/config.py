# config.py
class Config:
    SECRET_KEY = 'demo'
    
    # 以下是示例密钥，仅用于演示。在生产环境中，你应该使用安全的方式生成和存储密钥。
    PRIVATE_KEY = './public_key.pem'

    PUBLIC_KEY = './private_key.pem'
