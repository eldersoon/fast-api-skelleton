"""
Arquivo para executar a aplicação FastAPI.
Usage: uvicorn run:app --reload
"""
from app.main import app

__all__ = ["app"]

