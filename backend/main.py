"""
Vercel Entrypoint for FastAPI Application
"""
from app.main import app

# Export app for Vercel Serverless Function handler
__all__ = ["app"]
