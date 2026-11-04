# ClaudeVault Backend API

Production-ready backend foundation using FastAPI, SQLAlchemy 2.0, and Alembic.

## Requirements
- Python 3.10+
- PostgreSQL

## Getting Started
1. Create virtual environment: `python -m venv venv`
2. Activate venv: `.\venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env`
5. Run server: `uvicorn app.main:app --reload`
