import os
import json
import asyncio

import sys
sys.path.append("...") # Adds higher directory to python modules path.

from llama_index.core import Settings
from llama_index.core import load_index_from_storage, StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent.react import ReActAgent
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core import PromptTemplate

from config.settings import INDEX_STORAGE, CONVERSATION_FILE, POSTGRES_CONFIG_FILE, CHAT_HISTORY_DATABASE
from config.prompts import CUSTOM_AGENT_SYSTEM_TEMPLATE, PROMPT_USER_INPUT, TEXT_QA_TEMPLATE_STR, REFINE_TEMPLATE_STR
from core.utils import initialize_settings


from core.indexing import load_vector_index
from database.postgres.chat_history_manager import ChatStoreInitializer

async def initialize_chatbot(username):

    embedding_model, llm = await asyncio.to_thread(initialize_settings)

    Settings.llm = llm
    Settings.embed_model = embedding_model

    chat_store_initializer = ChatStoreInitializer(POSTGRES_CONFIG_FILE, CHAT_HISTORY_DATABASE)
    chat_store = chat_store_initializer.initialize_chat_store()

    memory = ChatMemoryBuffer.from_defaults(
        token_limit=10,
        chat_store=chat_store,
        chat_store_key=username
    )

    index = await load_vector_index()

    if index is None:
        raise Exception("Index not found")
    
    else:

        kdp_engine = index.as_chat_engine(
            memory=memory,
            llm=llm,
            text_qa_template=PromptTemplate(TEXT_QA_TEMPLATE_STR),
            refine_template=PromptTemplate(REFINE_TEMPLATE_STR),
        )

        return kdp_engine

    # kdp_tool = QueryEngineTool(
    #     query_engine=kdp_engine,
    #     metadata=ToolMetadata(
    #         name="kdp_english",
    #         description="Cung cấp các thông tin liên quan đến việc học tiếng Anh. Sử dụng câu hỏi văn bản thuần túy chi tiết làm đầu vào cho công cụ."
    #     )
    # )

    # agent = ReActAgent.from_tools(
    #     tools=[kdp_tool],
    #     memory=memory,
    #     system_prompt=PromptTemplate(CUSTOM_AGENT_SYSTEM_TEMPLATE)
    # )

    # if len(chat_store.get_messages(key=username))==0:

    #     embedding_model, llm = await asyncio.to_thread(initialize_settings)

    #     Settings.llm = llm
    #     Settings.embed_model = embedding_model

    #     response = agent.chat(CUSTOM_AGENT_SYSTEM_TEMPLATE)
    #     chat_store.persist(CONVERSATION_FILE)



async def handle_user_message(agent, user_message):

    embedding_model, llm = await asyncio.to_thread(initialize_settings)

    Settings.llm = llm
    Settings.embed_model = embedding_model

    response = agent.chat(user_message)

    return response.response
