from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from core.database import db_instance
import pymongo
import re

router = APIRouter()

class IdentityCreate(BaseModel):
    doc_number: str
    doc_type: str
    name: str
    dob: str
    is_blacklisted: bool = False
    notes: str = ""

@router.post("/add-identity")
async def add_identity(identity: IdentityCreate):
    collection = db_instance.db["national_identities"]
    
    clean_doc_number = re.sub(r'\s+', '', str(identity.doc_number).strip().upper())
    
    document = {
        "doc_number": clean_doc_number,
        "doc_type": identity.doc_type,
        "name": identity.name,
        "dob": identity.dob,
        "is_blacklisted": identity.is_blacklisted,
        "notes": identity.notes
    }
    
    # Upsert the document
    await collection.update_one(
        {"doc_number": clean_doc_number},
        {"$set": document},
        upsert=True
    )
    
    return {"status": "success", "message": f"Successfully added {clean_doc_number} to the MongoDB B-Tree Index for O(log N) fast lookups!"}
