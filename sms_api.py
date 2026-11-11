import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("TEMP_API_TOKEN")
BASE_URL = "https://tempnumbers.net/api"

def get_number(range_id=None, sid=None):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    # allocated=0 ka matlab unallocated numbers
    url = f"{BASE_URL}/view_gennumbers?allocated=0&limit=1"
    
    if range_id:
        url += f"&rangeid={range_id}"
    if sid:
        url += f"&sid={sid}"
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            json_data = res.json()
            if json_data.get("data"):
                return json_data["data"][0]["Number"]
            else:
                print(f"API Response (No Data): {json_data}")
        else:
            print(f"API Error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Number API Error: {e}")
    return None
