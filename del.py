from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",   # ✅ CURRENT WORKING MODEL
    messages=[
        {"role": "user", "content": "Explain how AI works in a few words."}
    ]
)

print("OUTPUT:", response.choices[0].message.content)
