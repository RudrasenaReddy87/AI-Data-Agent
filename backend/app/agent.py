import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def question_to_sql(question: str, schema_info: str) -> str:
    prompt = f"""
    You are a SQL expert. Generate an SQL query for this question:
    Schema: {schema_info}
    Question: {question}
    SQL:
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        temperature=0
    )
    return response.choices[0].text.strip()
