from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from core.config import databaseUri  # Assuming this is where your URI is defined

client = None

def get_client():
    global client
    if client is None:
        raise Exception("Database connection is not initialized")
    return client

def initialize_db():
    global client
    if client is None:
        try:
            uri = databaseUri  # Use your securely defined URI
            client = MongoClient(uri, tlsCAFile=certifi.where(), server_api=ServerApi('1'))
            client.admin.command("ping")
            print("MongoDB connect ho gaya!")
        except Exception as e:
            print("Mongo nahi milra!", e)
            raise
