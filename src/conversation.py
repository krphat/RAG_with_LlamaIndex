import os
import json
from datetime import datetime
import streamlit as st
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent.react import ReActAgent
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.llms.groq import Groq
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import PromptTemplate

import torch

from src.global_settings import INDEX_STORAGE, CONVERSATION_FILE
from src.prompts import CUSTORM_AGENT_SYSTEM_TEMPLATE, TEXT_QA_TEMPLATE_STR, REFINE_TEMPLATE_STR
from src.env import GROQ_API_KEY

user_avatar = "data/images/user.jpg"
bot_avatar = "data/images/kdp_bot.png"

device_type = "cuda" if torch.cuda.is_available() else "cpu"
embedding_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", device=device_type)
Settings.embed_model = embedding_model

llm = Groq(model="gemma2-9b-it", api_key=GROQ_API_KEY, temperature=0.2, device_type=device_type)
Settings.llm = llm

def load_chat_store():
    print("--> Call load_chat_store")
    if os.path.exists(CONVERSATION_FILE) and os.path.getsize(CONVERSATION_FILE) > 0:
        try:
            chat_store = SimpleChatStore.from_persist_path(CONVERSATION_FILE)
        except json.JSONDecodeError:
            chat_store = SimpleChatStore()
    else:
        chat_store = SimpleChatStore()
    return chat_store


def display_messages(chat_store, container, key):
    print("--> Call display_messages")
    with container:
        for message in chat_store.get_messages(key=key):
            if message.role == "user":
                with st.chat_message(message.role, avatar=user_avatar):
                    st.markdown(message.content)
            elif message.role == "assistant" and message.content != None:
                with st.chat_message(message.role, avatar=bot_avatar):
                    st.markdown(message.content)


def initialize_chatbot(chat_store, container, username):
    print("\n--> CALL initialize_chatbot")
    memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000, 
        chat_store=chat_store, 
        chat_store_key= username
    )  
    storage_context = StorageContext.from_defaults(
        persist_dir=INDEX_STORAGE
    )
    index = load_index_from_storage(
        storage_context
    )
    kdp_engine = index.as_chat_engine(
        memory=memory,
        llm=llm,
        text_qa_template=PromptTemplate(TEXT_QA_TEMPLATE_STR),
        refine_template=PromptTemplate(REFINE_TEMPLATE_STR),
    )

    # kdp_tool= QueryEngineTool(
    #     query_engine=kdp_engine, 
    #     metadata=ToolMetadata(
    #         name="kdp_english",
    #         description=(
    #             f"Cung cấp các thông tin liên quan đến việc học tiếng Anh"
    #             f". Sử dụng câu hỏi văn bản thuần túy chi tiết làm đầu vào cho công cụ"
    #         ),
    #     )
    # )   

    # agent = ReActAgent.from_tools(
    #     tools=[kdp_tool], 
    #     memory=memory,
    #     system_prompt=CUSTORM_AGENT_SYSTEM_TEMPLATE
    # )

    display_messages(chat_store, container, key=username)

    return kdp_engine


def chat_interface(agent, chat_store, container, username):
    print("--> Call chat_interface")
    if not os.path.exists(CONVERSATION_FILE) or os.path.getsize(CONVERSATION_FILE) == 0 or len(chat_store.get_messages(key=username))==0:
        with container:
            with st.chat_message(name="assistant", avatar=bot_avatar):
                st.markdown("Chào bạn, mình là KDP được phát triển bởi hắc coder Phary Dragneel. Mình sẽ giúp bạn học tiếng Anh một cách thuận tiện và hiệu quả. Hãy cùng nhau trao đổi nào!.")
    prompt = st.chat_input("Trao đổi tại đây...")
    if prompt:
        with container:
            with st.chat_message(name="user", avatar=user_avatar):
                st.markdown(prompt)
            response = str(agent.chat(prompt))
            with st.chat_message(name="assistant", avatar=bot_avatar):
                st.markdown(response)
        chat_store.persist(CONVERSATION_FILE)


