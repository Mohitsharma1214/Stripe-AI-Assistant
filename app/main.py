from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core.rag import RAGPipeline
import uvicorn

app = FastAPI(title="Indicnode AI Assistant - Stripe Domain")
pipeline = RAGPipeline()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    status: str
    latency: float
    context_used: list = []

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        result = await pipeline.run(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
def root():
    return {
        "message": "Welcome to the Stripe AI Assistant API",
        "docs": "/docs",
        "endpoints": {
            "query": "/query (POST)",
            "health": "/health (GET)"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
