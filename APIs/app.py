from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes.upload_document import router as upload_router
from routes.conversations import router as conversations_router

version = "v2"
# Danh sách các origin được phép
origins = [
    "http://localhost:3001",  # Origin của frontend
    "http://127.0.0.1:3001", # Nếu cần thêm domain
]



app = FastAPI(
    title="RAG",
    description='A REST API for Chatbot supports learning English.',
    version=version,
    contact={
        "email": "keiryphat@gmail.com"
    },
    docs_url=f"/api/{version}/docs"
)

# Thêm middleware xử lý CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Các domain được phép
    allow_credentials=True,  # Có cho phép gửi cookies hay không
    allow_methods=["*"],  # Các HTTP method được phép
    allow_headers=["*"],  # Các HTTP header được phép
)

# Include routers
app.include_router(upload_router, prefix=f"/api/{version}", tags=["documents"])
app.include_router(conversations_router, prefix=f"/api/{version}", tags=["conversations"])

if __name__ == "__main__":

    uvicorn.run("app:app")

"""
    Run server: python app.py
    APIs document: http://127.0.0.1:8000/api/v2/docs
"""