# run FastAPI app
# usage: python run_app.py
import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting Metamorph KDK to RD Converter API...")
    print("📖 Swagger docs available at: http://localhost:8000/swagger")
    print("📋 ReDoc available at: http://localhost:8000/redoc")
    print("🏥 Health check at: http://localhost:8000/health")
    print("-" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )