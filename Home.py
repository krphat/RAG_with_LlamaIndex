import streamlit as st
from src.authen import login, register, guest_login
import src.sidebar as sidebar

def main():
    sidebar.show_sidebar()
    
    # Login page
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.expander('KDP LEARNING', expanded=True):
            login_tab, create_tab, guest_tab = st.tabs(
                [
                    "Đăng nhập",
                    "Tạo tài khoản",
                    "Khách"
                ]
            )
            with create_tab:
                register()
            with login_tab:
                login()
            with guest_tab:
                guest_login()
    else:
        
        col1, col2 = st.columns(2)
        with col1:
            st.image("data/images/kdp_bot.png")
            if st.button("KDP Chatbot", key="btn_chat_1"):
                st.switch_page("pages/chat.py")
        with col2:
            st.image("data/images/kdp_bot.png")
            if st.button("KDP Chatbot", key="btn_chat_2"):
                st.switch_page("pages/chat.py")

        st.success(f'Chào mừng {st.session_state.username} đến với KDP Chatbot!', icon="🎉")

if __name__ == "__main__":
    
    # run code: streamlit run Home.py

    main()
