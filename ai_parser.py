import os
from groq import Groq
from dotenv import load_dotenv
import re

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_otp(sms_text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an OTP extractor. Reply ONLY with the numeric OTP from the text. If no OTP, reply 'NONE'."},
                {"role": "user", "content": sms_text}
            ],
            model="llama3-8b-8192",
            temperature=0.1,
        )
        result = chat_completion.choices[0].message.content.strip()
        if result.isdigit():
            return result
            
        # Fallback regex if AI misses it
        match = re.search(r'\b(\d{4,8})\b', sms_text)
        if match:
            return match.group(1)
            
        return None
    except Exception as e:
        print(f"AI Error: {e}")
        return None
