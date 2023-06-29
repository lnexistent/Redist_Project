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


def get_ideas(redis_conn):
    # Retrieve the list of ideas from the database
    ideas = redis_conn.hgetall('ideas')
    idea_dict = {}

    for idea, votes in ideas.items():
        idea_name = idea.decode()
        votes_count = int(votes.decode())
        idea_dict[idea_name] = []

        # Retrieve the names of people who made the idea
        names_key = f'idea_names:{idea_name}'
        names = redis_conn.smembers(names_key)
        for name in names:
            idea_dict[idea_name].append(name.decode())

    return idea_dict