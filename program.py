# secure_system.py - Group 7
import hashlib
import sqlite3

class SecureAcademicSystem:
    def __init__(self):
        self.setup_database()
    
    def setup_database(self):
        """Initialize secure database"""
        self.conn = sqlite3.connect('academic.db')
        self.cursor = self.conn.cursor()
        
        # Secure table creation
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                role TEXT,
                created_at TIMESTAMP
            )
        ''')
    
    def hash_password(self, password):
        """Secure password hashing"""
        salt = b'secure_salt_value'  # In production, use random salt
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )
        return hash_obj.hex()
    
    def register_user(self, username, password, role):
        """Secure user registration with parameterized query"""
        hashed_pw = self.hash_password(password)
        
        # SECURE: Parameterized query prevents SQL injection
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hashed_pw, role)
            )
            self.conn.commit()
            return True
        except:
            return False
    
    def authenticate(self, username, password):
        """Secure authentication"""
        # SECURE: Parameterized query
        self.cursor.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        result = self.cursor.fetchone()
        
        if result:
            stored_hash = result[0]
            input_hash = self.hash_password(password)
            return stored_hash == input_hash
        return False

# Demonstration
system = SecureAcademicSystem()
system.register_user("admin", "SecurePass123", "staff")
print("Authentication test:", system.authenticate("admin", "SecurePass123"))
