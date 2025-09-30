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
```

## Skills and Features Used

- **Backend Development**: Built with FastAPI for high-performance async web APIs, including user authentication with JWT and bcrypt hashing.
- **Database Management**: PostgreSQL with SQLAlchemy ORM for efficient data storage and querying.
- **AI Integration**: LangChain for natural language processing and OpenAI API for advanced data analysis and query understanding.
- **Frontend Development**: React with Vite for fast development, Tailwind CSS for styling, and Axios for API communication.
- **File Processing**: Excel file upload and processing, handling multiple sheets and data cleaning.
- **Data Visualization**: Dynamic chart and table generation for query results.
- **Authentication & Security**: JWT-based authentication system with secure password hashing.
- **Deployment**: Docker containerization and Procfile for easy deployment.

## Feature Enhancements

To achieve full functionality, we plan to enhance the AI capabilities using the OpenAI API in the following ways:

- **Advanced Query Understanding**: Integrate OpenAI's GPT models to better parse complex natural language queries, improving accuracy in data analysis.
- **Intelligent Data Summarization**: Use OpenAI API to generate concise summaries and insights from large datasets.
- **Conversational AI**: Implement multi-turn conversations where the AI remembers context from previous queries within a session.
- **Automated Insights**: Leverage OpenAI to automatically suggest relevant questions and provide proactive insights based on uploaded data.
- **Error Handling and Clarification**: Use AI to handle ambiguous queries by asking for clarification or providing alternative interpretations.

## Deployment

### Database: Supabase

The project uses Supabase as the database. The connection is configured in `backend/.env` with the provided DATABASE_URL.

### Backend: Vercel

1. Go to [Vercel](https://vercel.com) and sign in or create an account.
2. Click "New Project" and import your GitHub repository.
3. For the backend, select the `backend` directory as the root directory.
4. Set the following environment variables in Vercel:
   - `DATABASE_URL`: The Supabase PostgreSQL connection string
   - `JWT_SECRET`: A secure random string for JWT signing
   - `OPENAI_API_KEY`: Your OpenAI API key
5. Deploy the backend.

### Frontend: Vercel

1. In Vercel, create another new project for the frontend.
2. Select the `frontend` directory as the root directory.
3. Set the following environment variables:
   - `VITE_API_BASE_URL`: The URL of the deployed backend (e.g., https://your-backend.vercel.app)
   - `VITE_SUPABASE_KEY`: The Supabase anon key (eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...)
4. Deploy the frontend.

The frontend will be accessible at the Vercel-provided URL, and it will communicate with the backend API.
