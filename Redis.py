import redis
import os
import sys
from dotenv import load_dotenv
from difflib import SequenceMatcher

Env_Path = ""

load_dotenv(Env_Path)

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

# Check if the connection was successful
try:
    r.ping()
    print("Connected to Redis successfully!")
except redis.ConnectionError:
    print("Failed to connect to Redis!")
    sys.exit(1)


def get_ideas(redis_conn):
    # Retrieve the list of ideas from the database
    ideas = redis_conn.hgetall("ideas")
    idea_dict = {}

    for idea, votes in ideas.items():
        idea_name = idea.decode()
        votes_count = int(votes.decode())
        idea_dict[idea_name] = []

        # Retrieve the names of people who made the idea
        names_key = f"idea_names:{idea_name}"
        names = redis_conn.smembers(names_key)
        for name in names:
            idea_dict[idea_name].append(name.decode())

    return idea_dict


def submit_idea(redis_conn):
    while True:
        idea = input('Enter your idea (type "/quit" to exit): ')
        if idea.strip() == "/quit":
            return False
        elif idea.strip() == "":
            print("Invalid input. Please enter your idea.")
        else:
            break

    # Check for similar ideas
    ideas = get_ideas(redis_conn)
    similar_ideas = []
    for existing_idea in ideas:
        similarity = SequenceMatcher(None, idea.lower(), existing_idea.lower()).ratio()
        if similarity >= 0.6:
            similar_ideas.append(existing_idea)

    if similar_ideas:
        print(
            "Warning: The submitted idea is similar to the following existing ideas (use /quit to exit):"
        )
        for i, similar_idea in enumerate(similar_ideas, start=1):
            print(f"{i}. {similar_idea}")

        while True:
            choice = input("Do you want to continue with this idea? (y/n): ")
            if choice.lower() == "n":
                return submit_idea(redis_conn)  # Ask the user to enter a new idea
            elif choice.lower() == "y":
                break
            else:
                print('Invalid choice. Please enter either "y" or "n".')

    while True:
        names = input(
            "Enter the name(s) of the person(s) who made the idea (comma-separated) (use /quit to exit): "
        )
        if names.strip() == "":
            print("Invalid input. Please enter the name(s) of the person(s).")
        else:
            break

    names_list = [name.strip() for name in names.split(",")]
    names_string = ", ".join(names_list)

    if idea in ideas:
        # If the idea already exists, append the names to the existing idea
        existing_names = redis_conn.smembers(f"idea_names:{idea}")
        for name in names_list:
            redis_conn.sadd(f"idea_names:{idea}", name)
    else:
        # If the idea is new, add it to the database with 0 votes
        redis_conn.hset("ideas", idea, 0)
        # Store the names of people who made the idea in a set
        for name in names_list:
            redis_conn.sadd(f"idea_names:{idea}", name)

    redis_conn.lpush(names_string, f"Idea submitted: {idea}")
    print("Idea submitted successfully!")
    return True


def vote_for_idea(redis_conn, user_name):
    ideas = get_ideas(redis_conn)
    if not ideas:
        print("No ideas found. Be the first to submit one!")
        return

    print("Available Ideas:")
    for idea, names in ideas.items():
        votes = redis_conn.hget("ideas", idea)
        votes_count = int(votes.decode()) if votes else 0
        print(f"Idea: {idea}")
        print(f'Made by: {", ".join(names)}')
        print(f"Votes: {votes_count}")
        print()

    while True:
        idea_name = input(
            'Enter the name of the idea you want to vote for (type "/quit" to exit): '
        )
        if idea_name.strip() == "/quit":
            return
        elif idea_name.strip() == "":
            print("Invalid input. Please enter the name of the idea.")
        elif idea_name not in ideas:
            print("Invalid idea. Please try again.")
        else:
            break

    # Check if the user has already voted for the idea
    if redis_conn.sismember(f"voted:{idea_name}", user_name):
        print("You have already voted for this idea.")
        return

    # Add the user to the set of users who have voted for the idea
    redis_conn.sadd(f"voted:{idea_name}", user_name)

    # Increment the vote count for the idea
    redis_conn.hincrby("ideas", idea_name, amount=1)

    print("Vote submitted successfully!")
