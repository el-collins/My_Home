from motor.motor_asyncio import AsyncIOMotorClient # type: ignore # Import the AsyncIOMotorClient class from the motor.motor_asyncio module

import os # Import the os module to interact with the operating system
from dotenv import load_dotenv # type: ignore # Import the load_dotenv function from the dotenv module to load environment variables from a.env file

load_dotenv() # Load environment variables from the.env file

def get_db_client(): # Define a function to get a database client
    MONGO_URL = os.getenv("MONGO_URL") # Get the MongoDB connection string from the environment variables
    client = AsyncIOMotorClient(MONGO_URL) # Create a new AsyncIOMotorClient instance with the MongoDB connection string
    return client # Return the database client

users_database = get_db_client().Users # Get the Users database
user_collection = users_database.users # Get the users collection from the Users database

property_database = get_db_client().Properties # Get the Properties database
property_collection = property_database.properties # Get the properties collection from the Properties database

wishlist_database = get_db_client().Wishlist # Get the Wishlist database
wishlist_collection = wishlist_database.wishlists # Get the wishlists collection from the Wishlist database