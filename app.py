import streamlit as st
import os
from database import init_db, add_user, login_user, save_message, get_messages

# Khởi tạo
init_db()
if not os.path.exists("uploads"):
    os.makedirs("uploads")

st.set_page_config(page_title="Việt Chat Pro", layout="wide")

# Quản lý Session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.title("🚀 Việt Chat System")
    tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])
    
    with tab1:
        u1 = st.text_input("Username", key="l_user")
        p1 = st.text_input("Password", type="password", key="l_pass")
        if st.button("Vào phòng chat"):
            if login_user(u1, p1):
                st.session_state.logged_in = True
                st.session_state.username = u1
                st.rerun()
            else:
                st.error("Sai tài khoản rồi!")

    with tab2:
        u2 = st.text_input("Username mới", key="r_user")
        p2 = st.text_input("Password mới", type="password", key="r_pass")
        if st.button("Tạo tài khoản"):
            if add_user(u2, p2):
                st.success("Xong! Qua tab Đăng nhập nhé.")
            else:
                st.error("Tên này đã có người dùng.")

# --- MÀN HÌNH CHAT CHÍNH ---
else:
    with st.sidebar:
        st.header(f"👤 {st.session_state.username}")
        phong_chat = st.radio("Phòng chat:", ("📚 Học tập", "🎮 Giải trí", "💻 Code"))
        
        st.divider()
        st.subheader("📷 Gửi ảnh")
        img_file = st.file_uploader("Chọn ảnh", type=['png', 'jpg', 'jpeg'])
        if img_file and st.button("Gửi ảnh"):
            path = os.path.join("uploads", img_file.name)
            with open(path, "wb") as f:
                f.write(img_file.getbuffer())
            save_message(st.session_state.username, path, phong_chat, is_image=1)
            st.rerun()

        if st.button("Đăng xuất"):
            st.session_state.logged_in = False
            st.rerun()

    st.title(f"💬 {phong_chat}")
    
    # Hiển thị tin nhắn
    msgs = get_messages(phong_chat)
    for m in msgs:
        role = "user" if m[0] == st.session_state.username else "assistant"
        with st.chat_message(role):
            st.write(f"**{m[0]}**")
            if m[4] == 1: # Nếu là ảnh
                st.image(m[1], width=250)
            else:
                st.write(m[1])
            st.caption(m[2])

    if prompt := st.chat_input("Nhập nội dung..."):
        save_message(st.session_state.username, prompt, phong_chat, is_image=0)
        st.rerun()