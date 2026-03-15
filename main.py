from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import sqlite3
from datetime import datetime
import json

app = FastAPI()

# --- 1. KHỞI TẠO DATABASE ---
def init_db():
    conn = sqlite3.connect("chat_pro.db")
    cursor = conn.cursor()
    # Tạo bảng lưu tin nhắn nếu chưa có
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      sender TEXT, content TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

def save_message(sender, content):
    conn = sqlite3.connect("chat_pro.db")
    cursor = conn.cursor()
    time_now = datetime.now().strftime("%H:%M")
    cursor.execute("INSERT INTO messages (sender, content, timestamp) VALUES (?, ?, ?)", 
                   (sender, content, time_now))
    conn.commit()
    conn.close()
    return time_now

# --- 2. QUẢN LÝ KẾT NỐI REALTIME ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message_obj: dict):
        # Gửi dữ liệu dạng JSON cho tất cả mọi người
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message_obj))

manager = ConnectionManager()

# --- 3. ĐƯỜNG ỐNG WEBSOCKET ---
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    
    # Khi mới vào, có thể gửi thông báo người dùng tham gia
    join_msg = {"sender": "Hệ thống", "content": f"{client_id} đã vào phòng", "time": ""}
    await manager.broadcast(join_msg)
    
    try:
        while True:
            # Nhận tin nhắn từ người dùng
            data = await websocket.receive_text()
            
            # Lưu vào Database
            timestamp = save_message(client_id, data)
            
            # Đẩy tin nhắn đi cho tất cả mọi người (bao gồm cả người gửi)
            msg_packet = {
                "sender": client_id,
                "content": data,
                "time": timestamp
            }
            await manager.broadcast(msg_packet)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        exit_msg = {"sender": "Hệ thống", "content": f"{client_id} đã rời phòng", "time": ""}
        await manager.broadcast(exit_msg)