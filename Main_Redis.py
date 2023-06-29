import redis
import os
import sys 
from dotenv import load_dotenv
from difflib import SequenceMatcher

Env_Path = ""

load_dotenv(Env_Path)

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD)

# Check if the connection was successful
try:
    r.ping()
    print("Connected to Redis successfully!")
except redis.ConnectionError:
    print("Failed to connect to Redis!")
    sys.exit(1)
