# AI Data Agent

● Stack: React frontend, Python backend, SQL database  
● Core Feature: File upload system that accepts Excel files and converts them for analysis  
● AI Agent: Natural language query processing that understands user questions about their uploaded data

## Features

- User authentication (signup/login) with JWT
- Excel file upload and processing (handles multiple sheets, dirty data)
- Natural language query interface
- AI-powered data analysis using LangChain and OpenAI
- Dynamic chart and table generation
- Session-based conversation history

## Tech Stack

- **Backend**: FastAPI, PostgreSQL, SQLAlchemy, OpenAI API, LangChain
- **Frontend**: React, Vite, Tailwind CSS, Axios
- **Authentication**: JWT with bcrypt password hashing

## Setup

1. Clone the repository
2. Set up PostgreSQL database
3. Install backend dependencies: `cd backend && pip install -r requirements.txt`
4. Install frontend dependencies: `cd frontend && npm install`
5. Create `.env` file in backend/ with:
   - DATABASE_URL=postgresql://username:password@localhost:5432/db_name
   - JWT_SECRET=your_secret_key
   - OPENAI_API_KEY=your_openai_key
6. Run backend: `cd backend && uvicorn app.main:app --reload`
7. Run frontend: `cd frontend && npm run dev`
8. Open http://localhost:5173

## API Endpoints

- POST /signup: User registration
- POST /login: User login
- POST /upload-excel: Upload Excel file
- POST /ask: Ask questions about uploaded data
- GET /users: List users (protected)

## Project Structure

```
/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── auth.py
│   │   └── utils.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── README.md
