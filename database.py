import sqlite3
import hashlib
from datetime import datetime
import os

DB_PATH = 'data/chat_history.db'

def init_db():
    # Tạo thư mục data nếu chưa có để tránh lỗi không tìm thấy đường dẫn
    if not os.path.exists('data'):
        os.makedirs('data')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Bảng tin nhắn: lưu trữ nội dung chat và phân loại phòng
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (user TEXT, content TEXT, time TEXT, room TEXT, is_image INTEGER)''')
    
    # 2. Bảng người dùng: quản lý tài khoản
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT)''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Mã hóa mật khẩu bằng SHA-256"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(username, password):
    """Đăng ký thành viên mới"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Trả về False nếu username đã tồn tại
    finally:
        conn.close()

def login_user(username, password):
    """Kiểm tra thông tin đăng nhập"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
              (username, hash_password(password)))
    data = c.fetchone()
    conn.close()
    return data

def save_message(user, content, room, is_image=0):
    """Lưu tin nhắn văn bản hoặc đường dẫn ảnh"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%H:%M:%S")
    c.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?)", 
              (user, content, now, room, is_image))
    conn.commit()
    conn.close()

def get_messages(room):
    """Lấy danh sách tin nhắn theo phòng"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Lấy toàn bộ cột của những tin nhắn thuộc phòng 'room'
    c.execute("SELECT user, content, time, room, is_image FROM messages WHERE room = ?", (room,))
    data = c.fetchall()
    conn.close()
    return data