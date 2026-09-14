import asyncio
import os
import sys

# Add parent directory to path to allow importing core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import db_instance, connect_to_mongo, close_mongo_connection
import pymongo

MOCK_DATA = [
    {
        "doc_number": "593499339185", # Spaces removed for standard storage
        "doc_type": "AADHAAR",
        "name": "Pinnamaraju Purnima Sai",
        "is_blacklisted": False,
        "dob": "16/09/2006",
        "notes": "Valid Citizen"
    },
    {
        "doc_number": "974842715377",
        "doc_type": "AADHAAR",
        "name": "Rahul Kumar",
        "is_blacklisted": False,
        "dob": "15/08/1990",
        "notes": "Valid Citizen"
    },
    {
        "doc_number": "UYD2588101",
        "doc_type": "VOTER_ID",
        "name": "Arjun Singh",
        "is_blacklisted": True,  # Blacklisted identity
        "dob": "01/01/1985",
        "notes": "Flagged for fraudulent activities."
    },
    {
        "doc_number": "ABCDE1234F",
        "doc_type": "PAN",
        "name": "Pinnamaraju Purnima Sai",
        "is_blacklisted": False,
        "dob": "16/09/2006",
        "notes": "Valid Citizen"
    }
]

async def seed_db():
    print("Connecting to MongoDB...")
    await connect_to_mongo()
    
    collection = db_instance.db["national_identities"]
    
    print("Creating B-Tree Index on doc_number...")
    # Create an index for lightning fast O(log N) lookups
    await collection.create_index([("doc_number", pymongo.ASCENDING)], unique=True)
    
    print("Seeding database...")
    for record in MOCK_DATA:
        # Upsert based on doc_number
        await collection.update_one(
            {"doc_number": record["doc_number"]},
            {"$set": record},
            upsert=True
        )
        
    print(f"Successfully seeded {len(MOCK_DATA)} identities into the database!")
    
    # Verify by searching
    count = await collection.count_documents({})
    print(f"Total documents in collection: {count}")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed_db())
