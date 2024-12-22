import streamlit as st
from llama_index.llms.groq import Groq
from llama_index.core import Settings

from src.conversation import initialize_chatbot, chat_interface, load_chat_store
import src.sidebar as sidebar
from src.env import GROQ_API_KEY

llm = Groq(model="llama3-8b-8192", api_key=GROQ_API_KEY)
Settings.llm = llm

def main():
    sidebar.show_sidebar()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if st.session_state.logged_in:
        username = st.session_state.username

        st.header("💬 KDP CHATBOT")
        chat_store = load_chat_store()
        container = st.container()
        agent = initialize_chatbot(chat_store, container, username)
        chat_interface(agent, chat_store, container, username)
        print("--> CALL CHAT!")

if __name__ == "__main__":
    main()
