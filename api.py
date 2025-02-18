# api.py
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
from loader import DataLoader
from rag_chain import RAGPipeline
import shutil
import os
import logging
import asyncio
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/api.log"),
        logging.StreamHandler()
    ]
)

app = FastAPI(
    title="RAG Pipeline API",
    description="API for document processing and querying using RAG",
    version="1.0.0"
)

class Query(BaseModel):
    question: str
    index_name: str

@app.post("/upload/", status_code=201)
async def upload_document(file: UploadFile):
    """
    Upload and process a PDF document for RAG pipeline.
    """
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Save the uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the document
        loader = DataLoader(file_path)
        await loader.load_docs_into_pcvs()
        
        return {
            "message": "Document processed successfully",
            "index_name": loader.vectorstore_index_name
        }
    except Exception as e:
        logging.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/query/")
async def query_document(query: Query):
    """
    Query the RAG pipeline with a specific question.
    """
    try:
        rag_pipeline = RAGPipeline(query.index_name)
        # Use the async version of the qa method
        response = await rag_pipeline.qa_async(query.question)
        
        return {
            "question": query.question,
            "answer": response,
            "index_name": query.index_name
        }
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/")
async def health_check():
    """
    Basic health check endpoint.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)