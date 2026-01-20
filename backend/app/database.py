import os
from motor.motor_asyncio import AsyncIOMotorClient
from .llm.adapter import load_config

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    """Initialize MongoDB connection."""
    cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "config.yaml"))
    
    # Fallback to default if config file not found or load fails
    try:
        config = load_config(cfg_path)
    except:
        config = {}
        
    uri = config.get("mongodb_uri", "mongodb://localhost:27017")
    db_name = config.get("database_name", "rag_chatbot")
    
    print(f"Connecting to MongoDB at {uri}...")
    
    db.client = AsyncIOMotorClient(uri)
    db.db = db.client[db_name]
    
    # Ping to verify connection
    try:
        await db.client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"WARNING: Could not connect to MongoDB: {e}")

async def close_mongo_connection():
    """Close MongoDB connection."""
    if db.client:
        db.client.close()
