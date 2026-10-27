import os
import hmac
import hashlib
import json
import base64
import time

SECRET_KEY = "campus-connect-super-secret-key-for-pakistan-students"

def hash_password(password: str) -> str:
    """Pure Python password hashing using PBKDF2 with SHA256 (no native C dependencies)."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ":" + key.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against salt:hash format with pure Python safety."""
    try:
        if ":" in hashed_password:
            salt_hex, key_hex = hashed_password.split(":", 1)
            salt = bytes.fromhex(salt_hex)
            expected_key = bytes.fromhex(key_hex)
            new_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
            return hmac.compare_digest(new_key, expected_key)
        return plain_password == hashed_password
    except Exception:
        return False

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def _b64url_decode(s: str) -> bytes:
    padding = 4 - (len(s) % 4)
    if padding < 4:
        s += '=' * padding
    return base64.urlsafe_b64decode(s)

def create_access_token(data: dict) -> str:
    """Generate a standard JWT token using pure Python HMAC-SHA256."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + (7 * 24 * 3600)  # 7 days
    
    hdr_b64 = _b64url_encode(json.dumps(header).encode('utf-8'))
    pay_b64 = _b64url_encode(json.dumps(payload).encode('utf-8'))
    message = f"{hdr_b64}.{pay_b64}".encode('utf-8')
    sig = hmac.new(SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(sig)
    
    return f"{hdr_b64}.{pay_b64}.{sig_b64}"
