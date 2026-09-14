import asyncio
import cv2
import numpy as np
import re
import json
import pymupdf as fitz  # PyMuPDF
import base64
from paddleocr import PaddleOCR
from rapidocr_onnxruntime import RapidOCR
import pytesseract
from dateutil import parser
from mrz.checker.td1 import TD1CodeChecker
from mrz.checker.td2 import TD2CodeChecker
from mrz.checker.td3 import TD3CodeChecker
from models.schemas import OCRResult, MRZParsedData, VIZData, TamperResult
from core.database import save_log
from services.tamper_service import run_tamper_analysis
from services.qr_service import extract_qr_data
from services.db_service import verify_identity, validate_doc_format
from google import genai
from google.genai import types

def get_genai_client():
    try:
        import os
        import base64
        import tempfile
        
        creds_base64 = os.environ.get("GOOGLE_CREDENTIALS_BASE64", "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiY29udmVydGlvbmFsYWkiLAogICJwcml2YXRlX2tleV9pZCI6ICIyZTY2ZGU2MmE2NGU2NDc2ZjQ0YzMyMDU4MWUxZDNiMTg4NmVhNmU2IiwKICAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdkFJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLWXdnZ1NpQWdFQUFvSUJBUURVczVzOXFiWEg2b0JPXG5KelR4WkxQL284d2lRTEU5MTBaVHJDTFI1UjU1NlZvRUlVMnBuendqQ21hUE1yZkFuVWw3a1gyZnd1c0xWdVFQXG5lcGhyZlJOSStqcG5EKzFpdlQ1NmJ1QjJEb1VUUUpiVmZkWkVoUmo3cGZHeU9XcmxBSExQaG8wQmdFMjFKMitVXG50Rmtxd2VnVnVpRExRZjlMaE83SnVCSlJ2RG9uKzNWenJpM0w4Y0tsWFd3ZEprRFkzS01wbCt0QzRCL010cVU5XG4xV0p2SVM2LzlPU1ZHWHhVMHhWYkh1ZEE3WjZaZ2x2Si9uek5EU3BicmFJNk5VblhwanlNNUtkNHFCNTVYQitVXG5vb2RiV1krdmZYaGNKVGhiUmFob2dCR1dYdEtqWEI5R1RHVWM0My9wSEVxa3Z2MSt2R25lUmhsWWg2OU85bVNHXG5iVHhFK2lndkFnTUJBQUVDZ2dFQUZqaHZNdGxzWnFhdVlidkIwYWdLRDk1T1FKUE9rRjNSZUlOR25mUFlJN2RIXG5rcC9pQzZMWmR2V3FzaklEdFVrWk9LSUI1RE5LTjhTTGpieHFlT3czbkF1Y0YxRTRKUFVOTm1BbjdkMWxkSlh1XG5TLzVaNkkyWkJ3MFdlMTU1TnRROXFrVnRyS2I1TjBBWDdZcUx1Q1pLdHg1Yk43QzgyV2haUTlTSmdXVnZFK2NGXG51aFlSSVk0dDJJNU45VkFydzA4TitYWVpMNlFhNkNGY3o2MTdJb3dLdWxpalE4SkpHanZMSFh0M2ZDQVladWhSXG50ZERqWGZwRTd3bk5scExvYnNTaVRjVmZQd0x1d3FHTkxmQ3ZoRjNhM3ZrVzczazR1cUhGczlOZ052RnlTdFBsXG5VNmd4RWdpNEpYd3pqNVdTOEZLY0lvV0VYWmNqY2JwWGowajIzaGhnM1FLQmdRRDlVckx6OUpyZXc5QVhDamxmXG5mcXNnZEJ0OEo0T2JUSUxEWjhXM3NkbFQ0ZW9wVy9JVnMvYUVsSUJ6VFcrVlZMYUk4OWU4TlVNRXp5M0V6cDh6XG43UklaeXdTVjU5cU1ucnByMVpJM0EwTlZoSUovajNuS2twUWFSeDFxQ1l2ZUE3bUlHRHFUTi9aRXZlV1FXZDBTXG5wdEhCdkhFN1JqMkhXc2tKZ0VoV2hGNzlXd0tCZ1FEVzh3UXhGa2EwRVVJQnd2V0R6TVJ5dEcrM0pxNGFqKzh5XG5TRDVXb0Y3YjZ5SklwQ3FITzZEYmI2VEJMZmdza09xdmpYOExrVkRhTm1EWUUvRG90QjJhT2U2d0lNcGMxS2YwXG5IYXMvSDVmZmRuNWpJMS9WcWFQV3VOclkrRFMrYnVnNTU3eGFlZm4rV0JiUC9NM2t0eEVGbXd4ME5tUVJKbXVqXG5pakRiWklvVXZRS0JnR1R0a1F6dmROQ3lWWE1JaU1sS1QyWHp2SXVmdHFpbU9DY2diajc4NWVpc3hyM0p1MDc0XG5UNHlOR2d4V1d0RzFXYkNBN29BMi9FZXJQOEg4ektORW5nU1d4WEh3V1R2VGRkVEcxNldCY0U5Zkp4c3BqODJzXG56c01WZUZ1cUNBYmhsd2JwR0ZWVlk1SUowcS9MamZBRGRPanFhbmJDU250bUtWald1bnQxNjk2bkFvR0FlSWVxXG5xUS9SczdVZHF6azBUS1NzMzVrWUw3NUwwRzgzZEoyWC95Rk1MOHRJM1N6WkFCM0tsR0dsSkFIdjhLV09ROFIzXG5JZmhwT3dOVkNMVWQySTd2TG9VZnQ3bWJYN1NMUFZMSnJNcTljYnZUSVNvNzJlYVhEWmQ0ZUVPdDU3N3ZEMUZIXG5pQUJ2MDFSMzdrYlcrVkpDQkQrdUd4aEl3bWtsNEgxajZoSVZiNDBDZ1lCU2RzSUUrcldKNGNYdkwvbmx0VjNSXG50b0RiTSsyZWlGVFNZZC9DNVBtcFdKOVVwOGhkS2hJaGltajhUaTVrbWpEUkI2UkNtZzl1eFlvVURhSCtaSG15XG5zL2ZZMnU0TnFiR3llVjJldnp1eTRXMFZjVFVUV1VQSFJVRzlNM3U5RitMRW93aUVTK0NyZGpudkhZdUt6WGhIXG5Ka1ZqZ3NUZkYvajZYNGNpbU0yTjF3PT1cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJhZ2VudC1hY2Nlc3Mta2V5QGNvbnZlcnRpb25hbGFpLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjEwMzkzMTU3NTQ4OTI4MzY1NzA3MCIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvYWdlbnQtYWNjZXNzLWtleSU0MGNvbnZlcnRpb25hbGFpLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAidW5pdmVyc2VfZG9tYWluIjogImdvb2dsZWFwaXMuY29tIgp9Cg==")
        creds_json = base64.b64decode(creds_base64).decode('utf-8')
        
        # Write to a temporary file
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, 'w') as f:
            f.write(creds_json)
            
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
        
        return genai.Client(
            vertexai=True,
            project="convertionalai",
            location="us-central1"
        )
    except Exception as e:
        print(f"GenAI Client Error: {e}")
        return None

async def online_classify_document(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Uses Vertex AI for highly accurate and fast online classification."""
    client = get_genai_client()
    if not client:
        return "UNKNOWN"
        
    prompt = (
        "Classify the provided identity document into one of the following exact categories: "
        "AADHAAR_CARD, AADHAAR_FULL_PAGE, VOTER_ID, PAN, PASSPORT. "
        "Respond ONLY with the exact string of the category. If it's none of these, respond with UNKNOWN."
    )
    try:
        def run_model():
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt
                ],
            )
            return response.text.strip().upper()

        loop = asyncio.get_event_loop()
        # Timeout of 25s to ensure fallback happens fast if network issues, but gives enough time for Vertex AI
        result_text = await asyncio.wait_for(loop.run_in_executor(None, run_model), timeout=25.0)
        
        valid_categories = ["AADHAAR_CARD", "AADHAAR_FULL_PAGE", "VOTER_ID", "PAN", "PASSPORT"]
        if result_text in valid_categories:
            return result_text
        return "UNKNOWN"
    except asyncio.TimeoutError:
        print("Online Classification Error: Request timed out after 25 seconds.")
        return "UNKNOWN"
    except Exception as e:
        print(f"Online Classification Error: {type(e).__name__} - {e}")
        return "UNKNOWN"

async def online_extract_document(image_bytes: bytes, mime_type: str = "image/jpeg", doc_type: str = "UNKNOWN") -> dict:
    """Uses Vertex AI to extract VIZ data strictly as JSON."""
    client = get_genai_client()
    if not client:
        return None
        
    prompt = f"""
    You are an expert OCR and data extraction AI. Extract the following fields from the provided {doc_type} identity document.
    Return the extracted data strictly as a JSON object with the following keys:
    - name (string)
    - doc_number (string)
    - dob (string, YYYY-MM-DD format if possible)
    - address (string)
    
    If a field is not found, return null for that key. Do not include markdown formatting or backticks in the response. Just the JSON object.
    """
    try:
        def run_model():
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            return response.text.strip()

        loop = asyncio.get_event_loop()
        result_text = await asyncio.wait_for(loop.run_in_executor(None, run_model), timeout=25.0)
        import json
        return json.loads(result_text)
    except asyncio.TimeoutError:
        print("Online Extraction Error: Request timed out after 25 seconds.")
        return None
    except Exception as e:
        print(f"Online Extraction Error: {type(e).__name__} - {e}")
        return None

# Initialize Engines Lazily
_rapid_ocr_instance = None
_paddle_ocr_instance = None

def get_rapid_ocr():
    global _rapid_ocr_instance
    if _rapid_ocr_instance is None:
        _rapid_ocr_instance = RapidOCR()
    return _rapid_ocr_instance

def get_paddle_ocr():
    global _paddle_ocr_instance
    if _paddle_ocr_instance is None:
        _paddle_ocr_instance = PaddleOCR(use_textline_orientation=True, lang='en', enable_mkldnn=False)
    return _paddle_ocr_instance

def check_image_clarity(image: np.ndarray, threshold: float = 15.0) -> bool:
    """
    Calculate the Laplacian variance of the image to detect blur.
    Returns True if clear, False if blurry.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance >= threshold

def convert_to_image(file_bytes: bytes, filename: str = "upload.jpg") -> np.ndarray:
    """
    Converts bytes to an OpenCV image array. Handles PDFs via PyMuPDF.
    """
    if filename.lower().endswith(".pdf") or file_bytes.startswith(b'%PDF'):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if len(doc) == 0:
            raise ValueError("Empty PDF")
        page = doc.load_page(0)
        pix = page.get_pixmap()
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        if pix.n == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        elif pix.n == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        return img_array
    else:
        np_arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image bytes.")
        return img

def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Grayscale, Deskew, Bilateral filter, and Adaptive Threshold.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Deskewing
    coords = np.column_stack(np.where(gray > 0))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        if abs(angle) > 0.5 and abs(angle) < 45:
            (h, w) = gray.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Enhancement
    blurred = cv2.bilateralFilter(gray, 9, 75, 75)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresh

def auto_classify_document(text_blocks: list) -> str:
    """
    Classifies document based on extracted text using keywords (Offline Fallback).
    """
    full_text = " ".join([t[1].upper() for t in text_blocks])
    
    if "INCOME TAX DEPARTMENT" in full_text or ("GOVT OF INDIA" in full_text and "PERMANENT ACCOUNT NUMBER" in full_text):
        return "PAN"
    if "ELECTION COMMISSION" in full_text or "EPIC" in full_text or "ELECTOR PHOTO IDENTITY" in full_text:
        return "VOTER_ID"
    # Aadhaar format check
    if re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', full_text) or "UNIQUE IDENTIFICATION AUTHORITY" in full_text:
        if len(full_text) > 400: # Heuristic for Full Page vs Card
            return "AADHAAR_FULL_PAGE"
        return "AADHAAR_CARD"
    if "REPUBLIC OF INDIA" in full_text or "PASSPORT" in full_text or re.search(r'P<IND', full_text):
        return "PASSPORT"
        
    return "UNKNOWN"

def extract_face_base64(image: np.ndarray) -> str:
    """Detects the largest face using Haar Cascades and returns it as a Base64 string."""
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
        if len(faces) == 0:
            return None
        
        # Get largest face
        faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
        x, y, w, h = faces[0]
        
        # Add 20% padding
        pad = int(w * 0.2)
        x_start = max(0, x - pad)
        y_start = max(0, y - pad)
        x_end = min(image.shape[1], x + w + pad)
        y_end = min(image.shape[0], y + h + pad)
        
        face_crop = image[y_start:y_end, x_start:x_end]
        _, buffer = cv2.imencode('.jpg', face_crop)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print(f"Face extraction failed: {e}")
        return None

def extract_mrz_with_tesseract(image: np.ndarray) -> list[str]:
    """
    Applies morph blackhat for ROI, then Tesseract with strict whitelist.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)
    
    # We pass the processed or full image to Tesseract for the bottom portion
    h, w = gray.shape
    bottom_crop = gray[int(h*0.6):h, :] # Rough heuristic for MRZ position
    
    custom_config = r'--oem 1 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'
    text = pytesseract.image_to_string(bottom_crop, config=custom_config)
    
    lines = text.split('\n')
    mrz_pattern = re.compile(r'^[A-Z0-9<]{28,44}$')
    return [line.replace(' ', '') for line in lines if mrz_pattern.match(line.replace(' ', ''))]

def parse_mrz_with_checker(mrz_lines: list[str]) -> dict:
    """Uses mrz checker to validate checksums and extract info."""
    if not mrz_lines or len(mrz_lines) < 2:
        return None
        
    mrz_text = "\n".join(mrz_lines)
    checker = None
    
    try:
        if len(mrz_lines) == 3 and len(mrz_lines[0]) == 30:
            checker = TD1CodeChecker(mrz_text)
        elif len(mrz_lines) == 2 and len(mrz_lines[0]) == 36:
            checker = TD2CodeChecker(mrz_text)
        elif len(mrz_lines) == 2 and len(mrz_lines[0]) == 44:
            checker = TD3CodeChecker(mrz_text)
            
        if checker:
            fields = checker.fields()
            is_valid = bool(checker)
            return {
                "valid_checksums": is_valid,
                "document_type": fields.document_type,
                "country": fields.country,
                "surname": fields.surname,
                "name": fields.name,
                "document_number": fields.document_number,
                "nationality": fields.nationality,
                "birth_date": fields.birth_date,
                "sex": fields.sex,
                "expiry_date": fields.expiry_date
            }
    except Exception as e:
        print(f"MRZ Parsing Error: {e}")
    return None

def standardize_date(date_str: str) -> str:
    try:
        dt = parser.parse(date_str, fuzzy=True)
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str

def format_sse(step: str, message: str, status: str, payload: dict = None, error_code: str = None) -> str:
    data = {"step": step, "message": message, "status": status}
    if payload:
        data["payload"] = payload
    if error_code:
        data["error_code"] = error_code
    return f"data: {json.dumps(data)}\n\n"

async def stream_document_ocr(image_bytes: bytes, log_id: str, filename: str = "upload.jpg", force: bool = False):
    try:
        print(f"\n[{log_id}] === STARTING DOCUMENT OCR (Force={force}) ===")
        print(f"[INFO] Phase 1: Ingesting document {filename}")
        # Phase 1: Ingestion & Clarity
        yield format_sse("Phase 1", "Ingesting document and checking clarity...", "IN_PROGRESS")
        try:
            loop = asyncio.get_event_loop()
            # Wrap in executor and wait_for to prevent Zip Bombs from hanging the thread indefinitely
            image = await asyncio.wait_for(
                loop.run_in_executor(None, convert_to_image, image_bytes, filename),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            yield format_sse("Error", "Document parsing timed out. Possible Zip Bomb.", "FAILED", error_code="TIMEOUT")
            return
        except Exception as e:
            yield format_sse("Error", "Failed to parse document. Ensure it's a valid image or PDF.", "FAILED", error_code="UNSUPPORTED_FORMAT")
            return

        if not check_image_clarity(image) and not force:
            print(f"[ERROR] Image is too blurry. Needs confirmation.")
            yield format_sse("Error", "This image is blurry. Do you want to continue?", "NEEDS_CONFIRMATION", error_code="IMAGE_CLARITY_ISSUE")
            return
            
        # 🚀 Start Track C Tampering Analysis in the background (Parallel Consensus)
        mime_type = "application/pdf" if filename.lower().endswith(".pdf") else "image/jpeg"
        tamper_task = asyncio.create_task(run_tamper_analysis(image, image_bytes, mime_type))
        
        preprocessed = preprocess_image(image)

        # Phase 2: Hybrid Classification
        print(f"[INFO] Phase 2: Running Hybrid Classification (Online/Offline)...")
        yield format_sse("Phase 2", "Attempting Online AI classification...", "IN_PROGRESS")
        
        doc_type = await online_classify_document(image_bytes, mime_type)
        
        if doc_type == "UNKNOWN":
            print(f"[WARN] Online classification failed or returned UNKNOWN. Falling back to Offline RapidOCR...")
            yield format_sse("Phase 2", "Online AI unreachable. Falling back to Offline RapidOCR classification...", "IN_PROGRESS")
            result, _ = get_rapid_ocr()(preprocessed)
            if not result:
                yield format_sse("Error", "No text detected in document.", "FAILED", error_code="NO_TEXT_DETECTED")
                return
                
            doc_type = auto_classify_document(result)
            if doc_type == "UNKNOWN":
                print(f"[ERROR] Document type not recognized.")
                yield format_sse("Error", "Document type not recognized. Must be PAN, Aadhaar, Voter ID, or Passport.", "FAILED", error_code="UNSUPPORTED_DOCUMENT")
                return
            
        print(f"[INFO] Classification result: {doc_type}")
        yield format_sse("Classification", f"Detected Document Type: {doc_type}", "IN_PROGRESS")

        # Phase 3: Intelligent Routing
        viz_data = VIZData()
        mrz_data = None
        raw_mrz_lines = []
        validation_errors = []
        
        if doc_type in ["PAN", "AADHAAR_CARD", "AADHAAR_FULL_PAGE", "VOTER_ID"]:
            print(f"[INFO] Phase 3: Attempting Online AI Extraction for {doc_type}...")
            yield format_sse("Phase 3", f"Extracting VIZ data using Online AI...", "IN_PROGRESS")
            
            online_data = await online_extract_document(image_bytes, mime_type, doc_type)
            if online_data:
                viz_data.name = online_data.get("name")
                viz_data.doc_number = online_data.get("doc_number")
                viz_data.dob = online_data.get("dob")
                viz_data.address = online_data.get("address")
                print(f"[SUCCESS] Online Extraction complete: {viz_data.doc_number}")
            else:
                print(f"[WARN] Online extraction failed. Falling back to Offline PaddleOCR for {doc_type}...")
                yield format_sse("Phase 3", f"Online extraction failed. Routing VIZ to Offline PaddleOCR...", "IN_PROGRESS")
                # PaddleOCR extraction
                paddle_res = get_paddle_ocr().predict(image)
                extracted_texts = []
                if paddle_res and len(paddle_res) > 0 and 'rec_texts' in paddle_res[0]:
                    extracted_texts = paddle_res[0]['rec_texts']
                
                full_text = " ".join(extracted_texts)
                
                # Very basic regex extractions for demo
                if doc_type == "PAN":
                    pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', full_text)
                    if pan_match:
                        viz_data.doc_number = pan_match.group(0)
                    else:
                        validation_errors.append("INVALID_UNIQUE_ID")
                elif doc_type in ["AADHAAR_CARD", "AADHAAR_FULL_PAGE"]:
                    aadhaar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', full_text)
                    if aadhaar_match:
                        viz_data.doc_number = aadhaar_match.group(0)
                        
                elif doc_type == "VOTER_ID":
                    epic_match = re.search(r'\b[A-Z]{3}\d{7}\b', full_text)
                    if epic_match:
                        viz_data.doc_number = epic_match.group(0)
                    else:
                        validation_errors.append("INVALID_UNIQUE_ID")
                
                # Simple Heuristics for Name and Address (Offline Fallback)
                name = None
                address = None
                for idx, text in enumerate(extracted_texts):
                    if ("DOB" in text.upper() or "YEAR OF BIRTH" in text.upper()) and idx > 0 and not name:
                        name = extracted_texts[idx-1]
                    if "ADDRESS" in text.upper():
                        address_parts = extracted_texts[idx:min(idx+4, len(extracted_texts))]
                        address = " ".join(address_parts).replace("Address", "").replace(":", "").strip()
                
                if name: viz_data.name = name
                if address: viz_data.address = address
            
            # Extract face for Track B
            viz_data.face_base64 = extract_face_base64(image)
            
            # Phase 3b: QR Code Extraction & Verification
            qr_data_extracted = None
            qr_res = extract_qr_data(image)
            if qr_res.get('status') == 'SUCCESS':
                print(f"[INFO] QR Code Extracted successfully: {qr_res.get('type')}")
                yield format_sse("Phase 3", f"Scanned Secure QR Code Data.", "IN_PROGRESS")
                qr_data_extracted = qr_res.get('data')
                
                # Cross-Verification Logic
                if isinstance(qr_data_extracted, dict):
                    qr_name = qr_data_extracted.get("name", qr_data_extracted.get("n", "")).upper()
                    ocr_name = viz_data.name.upper() if viz_data.name else ""
                    
                    if qr_name and ocr_name:
                        # Simple fuzzy logic: Check if parts of OCR name are in QR name
                        ocr_parts = ocr_name.replace(',', '').split()
                        matches = sum(1 for part in ocr_parts if len(part) > 2 and part in qr_name)
                        if matches == 0 and len(ocr_parts) > 0:
                            print(f"[ERROR] Cross-Verification Failed! QR Name: {qr_name}, OCR Name: {ocr_name}")
                            validation_errors.append("QR_CROSS_VERIFICATION_FAILED")
            else:
                print(f"[WARN] QR Code Extraction failed: {qr_res.get('message')}")
                yield format_sse("Phase 3", f"QR Code extraction failed: {qr_res.get('message')}", "WARNING")
                qr_data_extracted = {"error": qr_res.get('message', 'QR Not Found')}
        elif doc_type == "PASSPORT":
            print(f"[INFO] Phase 3: Routing MRZ to Tesseract...")
            yield format_sse("Phase 3", "Routing MRZ to Tesseract...", "IN_PROGRESS")
            raw_mrz_lines = extract_mrz_with_tesseract(image)
            if not raw_mrz_lines:
                validation_errors.append("MRZ_NOT_FOUND")
            else:
                mrz_string = "\n".join(raw_mrz_lines)
                parsed_mrz = parse_mrz_with_checker(raw_mrz_lines)
                if parsed_mrz:
                    mrz_data = MRZParsedData(
                        document_type=parsed_mrz["document_type"],
                        nationality=parsed_mrz["nationality"],
                        document_number=parsed_mrz["document_number"],
                        names=f"{parsed_mrz['name']} {parsed_mrz['surname']}".strip(),
                        mrz_checksum_valid=parsed_mrz["valid_checksums"]
                    )
                    if not parsed_mrz["valid_checksums"]:
                        validation_errors.append("MRZ_CHECKSUM_FAILED")
                else:
                    validation_errors.append("MRZ_PARSE_ERROR")
        
        # Output formulation
        if validation_errors:
            print(f"[ERROR] Document validation failed: {validation_errors}")
            yield format_sse("Error", "Document validation failed.", "FAILED", payload={"errors": validation_errors}, error_code="VALIDATION_FAILED")
            return
            
        ocr_res = OCRResult(
            viz_data=viz_data,
            mrz_data=mrz_data,
            qr_data=qr_data_extracted if 'qr_data_extracted' in locals() else None,
            raw_mrz_lines=raw_mrz_lines,
            average_confidence=0.9, # Placeholder
            detected_elements=[]
        )
        print(f"[DEBUG] QR Data in locals: {'qr_data_extracted' in locals()}")
        if 'qr_data_extracted' in locals():
            print(f"[DEBUG] QR Data Extracted: {qr_data_extracted}")
        print(f"[DEBUG] OCRResult qr_data: {ocr_res.qr_data}")
        
        print(f"[INFO] Phase 4: Awaiting Forensic Tamper Analysis (Vertex + ELA)...")
        yield format_sse("Phase 4", "Awaiting Forensic Tamper Analysis...", "IN_PROGRESS")
        tamper_data = await tamper_task
        
        tamper_res = TamperResult(
            overall_risk_score=tamper_data.get("overall_risk_score", 0.0),
            needs_review=tamper_data.get("needs_review", False),
            layers=tamper_data.get("layers", {}),
            vertex_ai=tamper_data.get("vertex_ai", {})
        )
        
        risk_score = tamper_res.overall_risk_score
        
        # QR Code Heuristic Override
        if ocr_res.qr_data and isinstance(ocr_res.qr_data, dict) and ocr_res.qr_data.get('error'):
            print(f"[WARN] Applying Heuristic Override: Missing/Invalid QR code detected!")
            risk_score = min(100.0, risk_score + 85.0) # Add huge penalty
            tamper_res.needs_review = True
            tamper_res.overall_risk_score = risk_score
            # Also append reasoning to vertex AI so it shows in the UI if possible, or just let needs_review trigger the UI alert.
        
        print(f"[INFO] Phase 5: Format & Database Verification...")
        yield format_sse("Phase 5", "Running Cryptographic Format & Database Checks...", "IN_PROGRESS")
        
        # Format Check
        doc_no = viz_data.doc_number if viz_data and viz_data.doc_number else (mrz_data.document_number if mrz_data else "")
        person_name = viz_data.name if viz_data and viz_data.name else (mrz_data.names if mrz_data else "")
        
        format_res = validate_doc_format(doc_type, doc_no, person_name)
        tamper_res.format_validation_status = format_res["status"]
        tamper_res.format_validation_message = format_res["message"]
        
        if format_res["status"] == "FAILED":
            risk_score = 100.0
            tamper_res.needs_review = True
            
        # Database Verification Check
        db_res = await verify_identity(doc_type, doc_no, person_name)
        tamper_res.db_verification_status = db_res["status"]
        tamper_res.db_verification_message = db_res["message"]
        
        if db_res["status"] in ["NOT_FOUND", "BLACKLISTED", "NAME_MISMATCH"]:
            risk_score = 100.0
            tamper_res.needs_review = True
            
        tamper_res.overall_risk_score = risk_score
        
        print(f"[INFO] Phase 6: Persisting audit log...")
        yield format_sse("Phase 6", "Persisting audit log...", "IN_PROGRESS")
        
        output_payload = {
            "doc_type": doc_type,
            "ocr_data": ocr_res.model_dump(),
            "tamper_data": tamper_res.model_dump(),
            "risk_score": risk_score
        }
        await save_log(log_id, "PROCESSING_COMPLETED", output_payload)
        
        print(f"[SUCCESS] Processing complete for {filename}.")
        yield format_sse("Phase 6", "Processing complete.", "COMPLETED", output_payload)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[CRITICAL ERROR] Unexpected error in pipeline: {str(e)}")
        yield format_sse("Error", f"Unexpected error: {str(e)}", "FAILED", error_code="INTERNAL_ERROR")
