from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pandas as pd
import os
from dotenv import load_dotenv
from .utils import clean_excel, analyze_data
import json
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import timedelta
from .database import SessionLocal, engine, Base
from .models import User
from .auth import UserSignup, UserLogin, Token, hash_password, verify_password, create_access_token, get_current_user, local_users, save_local_users

load_dotenv()

app = FastAPI()

@app.on_event("startup")
def create_tables():
    try:
        # Create tables if they don't exist (no drop for production)
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating tables: {e}")
        # Continue starting the app even if DB connection fails

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://frontend-production-7fcb.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage for conversation context (in-memory, use database for production)
sessions = {}

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Auth endpoints
@app.post("/signup")
async def register(user: UserSignup):
    """Register endpoint: Accepts username, email, password. Hashes password with bcrypt, saves user, returns success message."""
    try:
        db = SessionLocal()
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            db.close()
            raise HTTPException(status_code=400, detail="Email already exists")
        hashed = hash_password(user.password)
        db_user = User(username=user.username, email=user.email, password=hashed)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()
        return {"message": "User created successfully"}
    except Exception as e:
        print(f"DB error: {e}, using local storage")
        if user.email in local_users:
            raise HTTPException(status_code=400, detail="Email already exists")
        local_users[user.email] = {"username": user.username, "password": hash_password(user.password)}
        save_local_users()
        return {"message": "User created successfully"}

@app.post("/login")
async def login(user: UserLogin):
    """Login endpoint: Accepts email, password. Verifies credentials, returns JWT token and welcome message with username."""
    try:
        db = SessionLocal()
        db_user = db.query(User).filter(User.email == user.email).first()
        db.close()
        if not db_user or not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))
        return {"access_token": access_token, "token_type": "bearer", "message": f"Welcome back, {db_user.username}"}
    except Exception as e:
        print(f"DB error: {e}, using local storage")
        if user.email not in local_users or not verify_password(user.password, local_users[user.email]["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))
        return {"access_token": access_token, "token_type": "bearer", "message": f"Welcome back, {local_users[user.email]['username']}"}

@app.get("/users")
async def get_users(current_user: User = Depends(get_current_user)):
    """Debug endpoint to view all users (remove in production)."""
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return [{"id": u.id, "username": u.username, "email": u.email, "created_at": u.created_at} for u in users]

@app.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current logged-in user information."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }



@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Read and clean the Excel file, handling multiple sheets
    try:
        excel_data = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
        processed_sheets = {}
        combined_df = pd.DataFrame()
        sheet_counter = 1

        for sheet_name, df in excel_data.items():
            # Handle unnamed sheets
            if isinstance(sheet_name, int) or not sheet_name or str(sheet_name).strip() == '':
                display_name = f"Sheet_{sheet_counter}"
                sheet_counter += 1
            else:
                display_name = str(sheet_name).strip()

            original_rows = len(df)
            df = clean_excel(df)
            processed_sheets[display_name] = {
                "columns": list(df.columns),
                "data": df.to_dict('records'),
                "row_count": len(df),
                "original_row_count": original_rows
            }
            # Combine all sheets into one for analysis (add sheet_name column)
            df.loc[:, 'sheet_name'] = display_name
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        # Save combined data for analysis
        combined_file_path = file_path.replace('.xlsx', '_combined.xlsx').replace('.xls', '_combined.xls')
        combined_df.to_excel(combined_file_path, index=False)

        total_original_rows = sum(processed_sheets[sheet]["original_row_count"] for sheet in processed_sheets)

        return {
            "message": "File uploaded and processed successfully",
            "file_path": combined_file_path,
            "sheets": processed_sheets,
            "total_rows": total_original_rows,
            "columns": list(combined_df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

def generate_chart(df, question, agent_response):
    """Generate chart data based on question and analysis."""
    chart_data = None
    question_lower = question.lower()

    # Try to infer chart type from question and response
    if any(word in question_lower for word in ["average", "avg", "mean"]):
        numeric_cols = df.select_dtypes(include=[float, int]).columns
        if len(numeric_cols) > 0:
            avg_data = df[numeric_cols].mean()
            chart_data = {
                "type": "bar",
                "title": "Average Values",
                "labels": list(avg_data.index),
                "data": avg_data.values.tolist()
            }
    elif any(word in question_lower for word in ["sum", "total", "totals"]):
        numeric_cols = df.select_dtypes(include=[float, int]).columns
        if len(numeric_cols) > 0:
            sum_data = df[numeric_cols].sum()
            chart_data = {
                "type": "bar",
                "title": "Total Values",
                "labels": list(sum_data.index),
                "data": sum_data.values.tolist()
            }
    elif any(word in question_lower for word in ["trend", "over time", "time series"]):
        date_cols = df.select_dtypes(include=['datetime']).columns
        numeric_cols = df.select_dtypes(include=[float, int]).columns
        if len(date_cols) > 0 and len(numeric_cols) > 0:
            df_sorted = df.sort_values(by=date_cols[0])
            chart_data = {
                "type": "line",
                "title": "Trend Over Time",
                "labels": df_sorted[date_cols[0]].dt.strftime('%Y-%m-%d').tolist(),
                "data": df_sorted[numeric_cols[0]].tolist()
            }
    elif any(word in question_lower for word in ["count", "frequency", "distribution"]):
        # For categorical data
        cat_cols = df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            value_counts = df[cat_cols[0]].value_counts().head(10)
            chart_data = {
                "type": "bar",
                "title": f"Distribution of {cat_cols[0]}",
                "labels": list(value_counts.index),
                "data": value_counts.values.tolist()
            }
    elif any(word in question_lower for word in ["compare", "comparison", "by category", "by group"]):
        # Group by categorical and sum numeric
        cat_cols = df.select_dtypes(include=['object']).columns
        numeric_cols = df.select_dtypes(include=[float, int]).columns
        if len(cat_cols) > 0 and len(numeric_cols) > 0:
            grouped = df.groupby(cat_cols[0])[numeric_cols[0]].sum().head(10)
            chart_data = {
                "type": "bar",
                "title": f"{numeric_cols[0]} by {cat_cols[0]}",
                "labels": list(grouped.index),
                "data": grouped.values.tolist()
            }

    # If no specific chart generated, try to extract from agent response
    if not chart_data and agent_response:
        # Simple heuristic: if response contains numbers, maybe create a chart
        import re
        numbers = re.findall(r'\d+\.?\d*', agent_response)
        if len(numbers) > 3:  # If there are multiple numbers, perhaps a chart
            # Assume first column is labels, second is data
            labels = [f"Item {i+1}" for i in range(len(numbers)//2)]
            data = [float(n) for n in numbers[:len(labels)]]
            chart_data = {
                "type": "bar",
                "title": "Data Analysis",
                "labels": labels,
                "data": data
            }

    return chart_data

@app.post("/ask")
async def ask_question(data: dict, current_user: User = Depends(get_current_user)):
    try:
        question = data.get("question")
        file_path = data.get("file_path")
        session_id = data.get("session_id", "default")
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")

        # Check for greetings
        greetings = ["hello", "hi", "hey", "hlo", "hi there", "hello there", "good morning", "good afternoon", "good evening", "hey there"]
        question_lower = question.lower().strip()
        if question_lower in greetings or any(greet in question_lower for greet in greetings):
            agent_response = "Hello! How can I help you analyze your data today?"
            chart_data = None
            table_data = None
        else:
            if not file_path or not os.path.exists(file_path):
                raise HTTPException(status_code=400, detail="No valid data file available")

            df = pd.read_excel(file_path)
            df = clean_excel(df)

            # Initialize session if not exists
            if session_id not in sessions:
                sessions[session_id] = {"history": []}
            history = sessions[session_id]["history"]

            # Generate answer using rule-based analysis
            agent_response = analyze_data(df, question)
            if not agent_response:
                agent_response = "Unable to analyze the data. Please try a different question."

            # Generate chart if applicable
            chart_data = generate_chart(df, question, agent_response)

            # Generate table data if needed (e.g., for queries that might benefit from tabular display)
            question_lower = question.lower()
            table_data = None
            if any(word in question_lower for word in ["show all", "list", "table", "rows", "data"]):
                table_data = df.head(20).to_dict('records')  # Limit to first 20 rows for display
            elif chart_data and len(chart_data.get('labels', [])) <= 10:
                # If we have a chart with few items, also show table
                table_data = df.head(10).to_dict('records')

        # Update history only for non-greetings
        if session_id in sessions:
            history = sessions[session_id]["history"]
            history.append({"question": question, "answer": agent_response})

        return {
            "answer": agent_response,
            "analysis": agent_response,
            "chart": chart_data,
            "table": table_data,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
