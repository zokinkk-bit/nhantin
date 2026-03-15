import streamlit as st
import os
import time
from database import init_db, add_user, login_user, save_message, get_messages

# 1. Khởi tạo
init_db()
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# 2. Cấu hình trang & Giao diện CSS Custom
st.set_page_config(page_title="Việt Chat Pro", layout="wide", page_icon="💬")

st.markdown("""
    <style>
    /* Tổng thể font và màu nền */
    .stApp { background-color: #000000; }
    
    /* Tùy chỉnh bong bóng chat chung */
    [data-testid="stChatMessage"] {
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 10px;
        max-width: 80%;
    }
    
    /* Tin nhắn CỦA VIỆT (User) - Màu xanh Messenger, nằm bên PHẢI */
    [data-testid="stChatMessage"]:has(svg[aria-label="User icon"]) {
        background-color: #0084ff !important;
        color: white !important;
        margin-left: auto !important;
        border-bottom-right-radius: 4px;
    }
    
    /* Tin nhắn NGƯỜI KHÁC (Assistant) - Màu xám, nằm bên TRÁI */
    [data-testid="stChatMessage"]:has(svg[aria-label="Assistant icon"]) {
        background-color: #3e4042 !important;
        color: white !important;
        margin-right: auto !important;
        border-bottom-left-radius: 4px;
    }

    /* Ẩn các icon mặc định của Streamlit để trông giống Messenger hơn */
    [data-testid="stChatMessage"] svg { display: none; }
    [data-testid="stChatMessageContent"] { margin: 0 !important; }
    
    /* Tùy chỉnh Sidebar */
    section[data-testid="stSidebar"] { background-color: #1c1d1f; border-right: 1px solid #333; }
    
    /* Cố định ô nhập liệu ở dưới cùng */
    .stChatInput { position: fixed; bottom: 30px; z-index: 1000; }
    </style>
""", unsafe_allow_html=True)

# Quản lý Session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- HÀM HIỂN THỊ CHAT BIỆT LẬP (FRAGMENT) ---
@st.fragment(run_every="1s")
def chat_stream(phong_chat):
    msgs = get_messages(phong_chat)
    # Container tự cuộn xuống cuối khi có tin nhắn mới
    chat_container = st.container(height=550, border=False)
    with chat_container:
        for idx, m in enumerate(msgs):
            # Nếu là chính mình gửi thì hiện role 'user' để ăn CSS màu xanh
            role = "user" if m[0] == st.session_state.username else "assistant"
            with st.chat_message(role):
                if len(m) > 4 and m[4] == 1:  # Nếu là ảnh
                    st.image(m[1], width=300)
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
        if st.button("Vào phòng chat", use_container_width=True):
            if login_user(u1, p1):
                st.session_state.logged_in = True
                st.session_state.username = u1
                st.rerun()
            else:
                st.error("Sai tài khoản rồi!")

    with tab2:
        u2 = st.text_input("Username mới", key="r_user")
        p2 = st.text_input("Password mới", type="password", key="r_pass")
        if st.button("Tạo tài khoản", use_container_width=True):
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
        if img_file and st.button("Gửi ảnh", use_container_width=True):
            path = os.path.join("uploads", img_file.name)
            with open(path, "wb") as f:
                f.write(img_file.getbuffer())
            save_message(st.session_state.username, path, phong_chat, is_image=1)
            st.rerun()

        st.divider()
        if st.button("Đăng xuất", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    st.title(f"💬 {phong_chat}")
    
    # Hiển thị tin nhắn nhảy realtime
    chat_stream(phong_chat)

    # Ô nhập tin nhắn
    if prompt := st.chat_input("Nhập tin nhắn vào " + phong_chat + "..."):
        save_message(st.session_state.username, prompt, phong_chat, is_image=0)
        # Vì có fragment nên tin nhắn sẽ tự hiện lên sau 1s mà không cần rerun cả trang