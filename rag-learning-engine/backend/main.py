from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .routes import router

app = FastAPI(
    title="AI Learning Engine API",
    description="RAG-powered educational assistant backend",
    version="1.0.0"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "AI Learning Engine API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-learning-engine"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 