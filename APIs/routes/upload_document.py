import os
from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from core.ingestion import ingest_documents
from core.indexing import build_indexes
from config.settings import DOCUMENTS_PATHS

router = APIRouter()

@router.post("/documents/upload/")
async def upload_file(file: UploadFile):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = f"{DOCUMENTS_PATHS}/{file.filename}"

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        nodes = await ingest_documents(file_path)

        if nodes is not None:
            print("--> Indexing...")
            vector_index = await build_indexes(nodes)

        else:
            raise HTTPException(status_code=501, detail="Error during document ingestion.")
        
        
        if vector_index is not None:
            return JSONResponse(content={"message": "File processed successfully."})
        
        else:
            raise HTTPException(status_code=501, detail="Error during indexing.")
    
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)