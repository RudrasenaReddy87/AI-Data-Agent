import requests
import os

# Get current script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to sample Excel file in uploads folder
file_path = os.path.join(BASE_DIR, "uploads", "test.xlsx")

# Check if file exists
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

# 0️⃣ Signup and Login to get token
signup_resp = requests.post("http://127.0.0.1:8000/signup", json={"username": "testuser", "email": "test@example.com", "password": "testpass"})
print("Signup Response:")
print(signup_resp.json() if signup_resp.status_code == 200 else f"Status: {signup_resp.status_code} - {signup_resp.text}")

login_resp = requests.post("http://127.0.0.1:8000/login", json={"email": "test@example.com", "password": "testpass"})
print("\nLogin Response:")
if login_resp.status_code == 200:
    login_data = login_resp.json()
    token = login_data.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(login_data)
else:
    print(f"Status: {login_resp.status_code} - {login_resp.text}")
    exit(1)

# 1️⃣ Test Excel upload
with open(file_path, "rb") as f:
    files = {'file': f}
    upload_resp = requests.post("http://127.0.0.1:8000/upload-excel", files=files, headers=headers)

print("Upload Response:")
upload_data = None
if upload_resp.status_code == 200:
    upload_data = upload_resp.json()
    print(upload_data)
else:
    print(f"Status: {upload_resp.status_code}")
    print(upload_resp.text)

# 2️⃣ Test /ask endpoint with multiple questions
questions = [
    "Show all employees in Sales department",
    "How many employees are there?",
    "What is the average age?",
    "Sum of ages",
    "Predict the next age"
]

if upload_data and 'file_path' in upload_data:
    file_path_from_upload = upload_data['file_path']
    for question in questions:
        question_data = {"question": question, "file_path": file_path_from_upload}
        ask_resp = requests.post("http://127.0.0.1:8000/ask", json=question_data, headers=headers)

        print(f"\nAsk Response for '{question}':")
        if ask_resp.status_code == 200:
            resp_json = ask_resp.json()
            print(resp_json)
            if 'image' in resp_json and resp_json['image']:
                print("Image generated successfully!")
        else:
            print(f"Status: {ask_resp.status_code}")
            print(ask_resp.text)
else:
    print("Upload failed, cannot test /ask")
