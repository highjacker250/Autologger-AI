import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("TEMP_API_TOKEN")
BASE_URL = "https://tempnumbers.net/api"

def get_number(range_id):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    url = f"{BASE_URL}/view_gennumbers?rangeid={range_id}&allocated=0&limit=1"
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200 and res.json().get("data"):
            # Here you might also want to call /api/allocate_numbers to lock it
            return res.json()["data"][0]["Number"]
    except Exception as e:
        print(f"Number API Error: {e}")
    return None
