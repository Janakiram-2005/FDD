from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List
import uuid
import asyncio

from services.ocr_service import stream_document_ocr
from models.schemas import OCRResult
from core.database import save_log

router = APIRouter()

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp", "application/pdf"]

@router.post("/stream-extract", summary="Stream OCR processing via SSE")
async def stream_extract_endpoint(file: UploadFile = File(...), force: bool = Form(False)):
    """
    Accepts an image or PDF and streams granular OCR progress updates using Server-Sent Events (SSE).
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )
        
    MAX_FILE_SIZE = 15 * 1024 * 1024 # 15MB
    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size is 15MB."
        )
        
    log_id = str(uuid.uuid4())
    filename = file.filename
    
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    }

    return StreamingResponse(
        stream_document_ocr(image_bytes, log_id, filename, force),
        media_type="text/event-stream",
        headers=headers
    )
