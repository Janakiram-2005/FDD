import motor.motor_asyncio
from core.config import settings
from datetime import datetime

class Database:
    client: motor.motor_asyncio.AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    """Initialize MongoDB connection on app startup."""
    db_instance.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    db_instance.db = db_instance.client[settings.MONGO_DB_NAME]
    
async def close_mongo_connection():
    """Close MongoDB connection on app shutdown."""
    if db_instance.client:
        db_instance.client.close()

async def save_log(log_id: str, status: str, payload: dict):
    """
    Save a verification log to MongoDB.
    MongoDB natively supports inserting arbitrary JSON into the payload without schema migrations.
    """
    collection = db_instance.db["verification_logs"]
    document = {
        "_id": log_id,
        "timestamp": datetime.utcnow(),
        "status": status,
        "payload": payload
    }
    # Update or insert the document (upsert)
    await collection.update_one({"_id": log_id}, {"$set": document}, upsert=True)
