from fastapi import APIRouter, File, UploadFile, HTTPException
from services.tamper_service import run_tamper_analysis
from services.ocr_service import convert_to_image
from models.schemas import TamperResult

router = APIRouter()

@router.post("/analyze", response_model=TamperResult, summary="Check document for tampering")
async def analyze_tampering_endpoint(file: UploadFile = File(...)):
    """
    Endpoint for Track C: ELA and Vertex AI tampering detection.
    """
    image_bytes = await file.read()
    
    try:
        image = convert_to_image(image_bytes, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    mime_type = "application/pdf" if file.filename.lower().endswith(".pdf") else "image/jpeg"
    
    tamper_data = await run_tamper_analysis(image, image_bytes, mime_type)
    
    return TamperResult(
        heatmap_base64=tamper_data.get("ela_heatmap_base64"),
        vertex_analysis=tamper_data.get("vertex_analysis")
    )
