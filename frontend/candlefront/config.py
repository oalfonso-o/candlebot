import os
from dotenv import load_dotenv

load_dotenv(override=True)

API = os.getenv('CANDLEFRONT_API_ENDPOINT')
