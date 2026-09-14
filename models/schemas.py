from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class VIZData(BaseModel):
    name: Optional[str] = None
    doc_number: Optional[str] = None
    dob: Optional[str] = None
    expiry: Optional[str] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    face_base64: Optional[str] = None
    optional_data: Optional[str] = None

class MRZParsedData(BaseModel):
    document_type: Optional[str] = None
    nationality: Optional[str] = None
    document_number: Optional[str] = None
    dob: Optional[str] = None
    sex: Optional[str] = None
    expiry_date: Optional[str] = None
    names: Optional[str] = None
    optional_data: Optional[str] = None
    mrz_checksum_valid: bool = False

class OCRResult(BaseModel):
    viz_data: Optional[VIZData] = None
    mrz_data: Optional[MRZParsedData] = None
    qr_data: Optional[Any] = None
    raw_mrz_lines: List[str] = Field(default_factory=list)
    average_confidence: float = 0.0
    detected_elements: List[Dict[str, Any]] = Field(default_factory=list)

class TamperResult(BaseModel):
    overall_risk_score: float = 0.0
    needs_review: bool = False
    layers: Optional[Dict[str, Any]] = None
    vertex_ai: Optional[Dict[str, Any]] = None
    db_verification_status: Optional[str] = None
    db_verification_message: Optional[str] = None
    format_validation_status: Optional[str] = None
    format_validation_message: Optional[str] = None

class BiometricResult(BaseModel):
    similarity_score: float = Field(0.0, ge=0.0, le=1.0)
    liveness_status: str = "UNKNOWN"

class VerificationResponse(BaseModel):
    log_id: str
    doc_type: Optional[str] = "UNKNOWN"
    risk_score: float = Field(0.0, ge=0.0, le=100.0)
    ocr_result: Optional[OCRResult] = None
    tamper_result: Optional[TamperResult] = None
    biometric_result: Optional[BiometricResult] = None
    status: str = "PROCESSING"
    errors: List[str] = Field(default_factory=list)
