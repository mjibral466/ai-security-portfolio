import sqlite3
import hashlib
import hmac

def verify_user_login(db_path: str, username: str, password: str) -> bool:
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT password_hash, salt FROM users WHERE username = ?"
            cursor.execute(query, (username,))
            user_data = cursor.fetchone()

            if not user_data:
                return False

            stored_hash, salt = user_data
            
            salt_bytes = salt.encode('utf-8') if isinstance(salt, str) else salt
            calculated_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt_bytes,
                100000
            ).hex()

            return hmac.compare_digest(stored_hash, calculated_hash)

    except sqlite3.Error:
        return False