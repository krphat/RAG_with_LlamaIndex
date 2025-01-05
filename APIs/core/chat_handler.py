import os
import json
import asyncio


from llama_index.core import Settings
from llama_index.core import load_index_from_storage, StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent.react import ReActAgent
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core import PromptTemplate

from config.settings import INDEX_STORAGE, CONVERSATION_FILE
from config.prompts import CUSTOM_AGENT_SYSTEM_TEMPLATE, PROMPT_USER_INPUT, TEXT_QA_TEMPLATE_STR, REFINE_TEMPLATE_STR
from core.utils import initialize_settings


async def load_chat_store():

    if os.path.exists(CONVERSATION_FILE) and os.path.getsize(CONVERSATION_FILE) > 0:
        try:
            chat_store = SimpleChatStore.from_persist_path(CONVERSATION_FILE)
        except json.JSONDecodeError:
            chat_store = SimpleChatStore()
    else:
        chat_store = SimpleChatStore()
    return chat_store


async def initialize_chatbot(username):

    embedding_model, llm = await asyncio.to_thread(initialize_settings)

    Settings.llm = llm
    Settings.embed_model = embedding_model

    chat_store = await load_chat_store()

    memory = ChatMemoryBuffer.from_defaults(
        token_limit=10,
        chat_store=chat_store,
        chat_store_key=username
    )

    storage_context = StorageContext.from_defaults(
        persist_dir=INDEX_STORAGE
    )

    index = await asyncio.to_thread(load_index_from_storage, storage_context)

    kdp_engine = index.as_chat_engine(
        memory=memory,
        llm=llm,
        text_qa_template=PromptTemplate(TEXT_QA_TEMPLATE_STR),
        refine_template=PromptTemplate(REFINE_TEMPLATE_STR),
    )

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


    return kdp_engine, chat_store


async def handle_user_message(agent, chat_store, user_message):

    embedding_model, llm = await asyncio.to_thread(initialize_settings)

    Settings.llm = llm
    Settings.embed_model = embedding_model

    response = agent.chat(user_message)
    chat_store.persist(CONVERSATION_FILE)

    return response.response
