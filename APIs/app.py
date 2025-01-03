from fastapi import FastAPI
import uvicorn
from routes.upload_document import router as upload_router
from routes.conversations import router as conversations_router

version = "v1"

app = FastAPI(
    title="RAG",
    description='A REST API for Chatbot supports learning English.',
    version=version,
    contact={ 
        "email": "keiryphat@gmail.com"
    },
    docs_url=f"/api/{version}/docs"
)

# Include routers
app.include_router(upload_router, prefix=f"/api/{version}", tags=["documents"])
app.include_router(conversations_router, prefix=f"/api/{version}", tags=["conversations"])

if __name__ == "__main__":

    uvicorn.run("app:app")

"""
    Run server: python app.py
    APIs document: http://127.0.0.1:8000/api/v1/docs
"""