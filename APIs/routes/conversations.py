import asyncio
from fastapi import APIRouter, HTTPException
from core.chat_handler import initialize_chatbot, handle_user_message, load_chat_store
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    username: str
    message: str

class ChatResponse(BaseModel):
    username: str
    user_message: str
    bot_response: str

class ConversationHistoryResponse(BaseModel):
    username: str
    messages: list

@router.post("/conversations/chat/", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):

    try:

        agent, chat_store = await initialize_chatbot(request.username)

        bot_response = await handle_user_message(agent, chat_store, request.message)

        return ChatResponse(
            username=request.username,
            user_message=request.message,
            bot_response=bot_response
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during chatbot interaction: {str(e)}")
    

@router.get("/conversations/history/{username}", response_model=ConversationHistoryResponse)
async def get_conversation_history(username: str):

    try:

        chat_store = await load_chat_store()

        messages = chat_store.get_messages(key=username)

        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        return ConversationHistoryResponse(
            username=username,
            messages=formatted_messages
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversation history: {str(e)}")