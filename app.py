import streamlit as st
import os
import time
from database import init_db, add_user, login_user, save_message, get_messages

# 1. Khởi tạo
init_db()
if not os.path.exists("uploads"):
    os.makedirs("uploads")

st.set_page_config(page_title="Việt Chat Pro", layout="wide", page_icon="💬")

# Quản lý Session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- HÀM HIỂN THỊ CHAT BIỆT LẬP (FRAGMENT) ---
@st.fragment(run_every="1s") # Tự động làm mới khung này mỗi 1 giây
def chat_stream(phong_chat):
    msgs = get_messages(phong_chat)
    # Container có chiều cao cố định và tự động cuộn xuống cuối (giống Messenger)
    chat_container = st.container(height=500, border=False)
    with chat_container:
        for idx, m in enumerate(msgs):
            role = "user" if m[0] == st.session_state.username else "assistant"
            with st.chat_message(role):
                if len(m) > 4 and m[4] == 1:  # Nếu là ảnh
                    st.image(m[1], width=250)
                else:
                    st.markdown(f"**{m[0]}**: {m[1]}")
                st.caption(f"{m[2]}")

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
        img_file = st.file_uploader("Chọn ảnh", type=['png', 'jpg', 'jpeg'], key="img_up")
        if img_file and st.button("Gửi ảnh"):
            path = os.path.join("uploads", img_file.name)
            with open(path, "wb") as f:
                f.write(img_file.getbuffer())
            save_message(st.session_state.username, path, phong_chat, is_image=1)
            st.rerun()

        if st.button("Đăng xuất"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    st.title(f"💬 {phong_chat}")
    
    # Gọi hàm fragment để hiển thị tin nhắn nhảy realtime
    chat_stream(phong_chat)

    # Ô nhập tin nhắn (Nằm ngoài fragment để không bị load lại khi gõ)
    if prompt := st.chat_input("Nhập nội dung..."):
        save_message(st.session_state.username, prompt, phong_chat, is_image=0)
        # Không cần rerun toàn trang, fragment sẽ tự nhận ra tin nhắn mới sau tối đa 1s