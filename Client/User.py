from werkzeug.security import check_password_hash

class User:

    def __init__(self, user_data):
        
        self.username = user_data['_id']
        self.email = user_data['email']
        self.password = user_data['password']

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True 
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.username
    
    def password_correct(self, password_to_check):
        return check_password_hash(self.password, password_to_check)

