from typing import Optional

class AuthManager:
    def __init__(self, db):
        self.db = db
        self.current_user: Optional[dict] = None
    
    def login(self, username: str, password: str) -> bool:
        user = self.db.get_user_by_credentials(username, password)
        if user:
            self.current_user = user
            return True
        return False
    
    def register(self, username: str, password: str, full_name: str, email: str, phone: str) -> bool:
        return self.db.create_user(username, password, full_name, email, phone)
    
    def logout(self):
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        return self.current_user is not None
    
    def is_client(self) -> bool:
        return self.is_authenticated() and self.current_user['role'] == 'client'
    
    def is_admin(self) -> bool:
        return self.is_authenticated() and self.current_user['role'] == 'admin'
    
    def is_master(self) -> bool:
        return self.is_authenticated() and self.current_user['role'] == 'master'