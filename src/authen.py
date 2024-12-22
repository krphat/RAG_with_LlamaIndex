import streamlit as st
import yaml
import hashlib
import os
from src.global_settings import USERS_FILE
# Đọc dữ liệu từ file YAML
def load_users():
    if os.path.exists(USERS_FILE) and os.path.getsize(USERS_FILE) > 0:
        with open(USERS_FILE, 'r') as file:
            users = yaml.safe_load(file)
        return users
    else:
        return {"usernames": {}}

# Lưu dữ liệu vào file YAML
def save_users(users):
    with open(USERS_FILE, 'w') as file:
        yaml.safe_dump(users, file)

# Mã hóa mật khẩu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Kiểm tra mật khẩu
def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# Tạo giao diện đăng ký
def register():
    with st.form(key="register"):
        st.subheader('Register')
        username = st.text_input('Tên tài khoản')
        password = st.text_input('Mật khẩu', type='password')
        confirm_password = st.text_input('Xác nhận mật khẩu', type='password')

        if st.form_submit_button('Đăng ký'):
            users = load_users()
            if len(users['usernames']) >= 10:
                st.error('Số lượng người dùng đã đạt giới hạn tối đa!')
            elif not username or not password:
                st.error('Bạn cần nhập tên tài khoản và mật khẩu!')
            elif password == confirm_password:
                if username in users['usernames']:
                    st.error('Tên tài khoản không hợp lệ!')
                else:
                    hashed_password = hash_password(password)
                    users['usernames'][username] = {
                        'password': hashed_password
                    }
                    save_users(users)
                    st.session_state.username = username
                    st.session_state.logged_in = True

                    st.rerun()
            else:
                st.error('Mật khẩu không khớp!')

# Tạo giao diện đăng nhập
def login():
    with st.form(key="login"):
        username = st.text_input('Tên đăng nhập')
        password = st.text_input('Mật khẩu', type='password')

        if st.form_submit_button('Đăng nhập'):
            users = load_users()
            if username in users['usernames']:
                stored_password = users['usernames'][username]['password']
                if verify_password(stored_password, password):
                    st.session_state.username = username
                    st.session_state.logged_in = True

                    st.rerun()
                else:
                    st.error('Mật khẩu không chính xác!')
            else:
                st.error('Tên đăng nhập không đúng!')

def guest_login():
    if st.button('Khách đăng nhập'):
        st.session_state.logged_in = True
        st.session_state.username = 'guest'

        st.rerun()


if __name__ == '__main__':
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.expander('KDP CHATBOT', expanded=True):
            login_tab, create_tab = st.tabs(
                [
                    "Đăng nhập",
                    "Tạo tài khoản",
                ]
            )
            with create_tab:
                register()
            with login_tab:
                login()
    else:
        st.write(f"Welcome, {st.session_state.username}!")
