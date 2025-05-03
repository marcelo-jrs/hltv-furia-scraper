import requests
from dotenv import load_dotenv
import os

load_dotenv()

response = requests.get(os.getenv('JSON_URL'))
data = response.json()
print(data)
