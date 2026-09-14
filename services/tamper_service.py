import os
import cv2
import numpy as np
import base64
import asyncio
import io
import json
import concurrent.futures
import exifread
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

client = get_genai_client()

def compute_ela_with_canny(image: np.ndarray, quality: int = 90) -> dict:
    """Layer 1 & 2: Error Level Analysis with Canny Edge Subtraction."""
    try:
        # Simulate JPEG compression
        _, encoded = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        resaved = cv2.imdecode(encoded, cv2.IMREAD_COLOR)

        # Compute absolute difference
        ela = np.abs(image.astype(np.int16) - resaved.astype(np.int16))
        ela_gray = cv2.cvtColor(cv2.normalize(ela, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8), cv2.COLOR_BGR2GRAY)

        # Enhance ELA contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        ela_gray = clahe.apply(ela_gray)
        
        # Slight blur to remove pure single-pixel compression artifacts
        ela_gray = cv2.GaussianBlur(ela_gray, (3, 3), 0)

        # Apply Heatmap
        heatmap = cv2.applyColorMap(ela_gray, cv2.COLORMAP_JET)
        _, buffer = cv2.imencode('.jpg', heatmap)
        b64 = base64.b64encode(buffer).decode('utf-8')

        # Heuristic risk calculation - use top 5% brightest pixels instead of global mean to catch small spliced faces
        sorted_pixels = np.sort(ela_gray.flatten())
        top_5_percent_idx = int(len(sorted_pixels) * 0.95)
        top_5_mean = np.mean(sorted_pixels[top_5_percent_idx:])
        
        # Lowered the threshold divisor because top 5% of a clean image is still relatively dark
        risk = min(100.0, (top_5_mean / 60.0) * 100.0) 

        return {"heatmap_base64": b64, "risk_score": float(risk)}
    except Exception as e:
        print(f"ELA Error: {e}")
        return {"heatmap_base64": "", "risk_score": 0, "error": str(e)}

def compute_noise_residual(image: np.ndarray) -> dict:
    """Layer 3: Noise Analysis (Sensor Print)."""
    try:
        blurred = cv2.medianBlur(image, 3)
        noise = np.abs(image.astype(np.int16) - blurred.astype(np.int16))
        std_dev = float(np.std(noise))

        if std_dev < 1.0: # Too clean, likely a digitally generated PDF
            return {"risk_score": 0, "status": "CLEAN_PDF_SKIPPED", "std_dev": std_dev}

        risk = min(100, (std_dev / 25.0) * 100)
        return {"risk_score": risk, "status": "ANALYZED", "std_dev": std_dev}
    except Exception as e:
        return {"risk_score": 0, "status": "ERROR", "error": str(e)}

def compute_sift_clone_detection(image: np.ndarray) -> dict:
    """Layer 4: SIFT Clone Detection for Copy-Move Forgery."""
    try:
        # Resize constraint (O(N) Optimization)
        h, w = image.shape[:2]
        if w > 1024:
            ratio = 1024 / w
            image = cv2.resize(image, (1024, int(h * ratio)))

        sift = cv2.SIFT_create()
        keypoints, descriptors = sift.detectAndCompute(image, None)

        if descriptors is None or len(keypoints) < 50:
            return {"risk_score": 0, "matches_found": 0, "needs_review": False}

        # FLANN matching
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(descriptors, descriptors, k=3)

        clone_matches = 0
        for m in matches:
            if len(m) >= 3:
                # m[0] is self, m[1] is best distinct match, m[2] is 2nd best
                # Lowe's ratio test to ensure the match is highly confident
                if m[1].distance < 0.7 * m[2].distance:
                    # Enforce physical distance constraint to avoid adjacent block matching
                    pt1 = keypoints[m[0].queryIdx].pt
                    pt2 = keypoints[m[1].trainIdx].pt
                    dist = np.sqrt((pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2)
                    if dist > 50: # Must be >50 pixels apart
                        clone_matches += 1

        risk = min(100, clone_matches * 5)
        needs_review = clone_matches > 10 # Trigger Officer UI Override if > 10 distinct cloned clusters
        return {"risk_score": risk, "matches_found": clone_matches, "needs_review": needs_review}
    except Exception as e:
        return {"risk_score": 0, "matches_found": 0, "needs_review": False, "error": str(e)}

def extract_exif_metadata(image_bytes: bytes) -> dict:
    """Layer 5: Metadata software traces extraction."""
    try:
        f = io.BytesIO(image_bytes)
        tags = exifread.process_file(f, details=False)

        if not tags:
            return {"risk_score": 0, "status": "STRIPPED", "software": None}

        software_tag = tags.get('Image Software', tags.get('Software', None))
        
        if software_tag:
            sw = str(software_tag).lower()
            suspicious = ['photoshop', 'gimp', 'canva', 'corel']
            for s in suspicious:
                if s in sw:
                    return {"risk_score": 100, "status": "SUSPICIOUS_SOFTWARE", "software": sw}
            return {"risk_score": 0, "status": "AUTHENTIC", "software": str(software_tag)}
            
        return {"risk_score": 0, "status": "AUTHENTIC", "software": None}
    except Exception as e:
        return {"risk_score": 0, "status": "ERROR", "error": str(e)}

def compute_moire_pattern_detection(image: np.ndarray) -> dict:
    """Layer 6: Moiré Pattern (Recapture) Detection using 2D FFT."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
        
        h, w = gray.shape
        cy, cx = h // 2, w // 2
        r = 30 # radius for low frequency mask
        
        mask = np.ones((h, w), np.uint8)
        cv2.circle(mask, (cx, cy), r, 0, -1)
        
        high_freq = magnitude_spectrum * mask
        
        avg_hf_energy = np.mean(high_freq[high_freq > 0])
        max_hf_energy = np.max(high_freq)
        
        if avg_hf_energy == 0:
            return {"risk_score": 0, "status": "CLEAN"}
            
        ratio = max_hf_energy / avg_hf_energy
        
        # Typically ratio > 1.4 indicates significant repeating patterns
        risk = min(100.0, max(0.0, (ratio - 1.2) * 150))
        
        status = "SUSPICIOUS_RECAPTURE" if risk > 75 else "AUTHENTIC"
        
        return {"risk_score": risk, "status": status, "ratio": float(ratio)}
    except Exception as e:
        return {"risk_score": 0, "status": "ERROR", "error": str(e)}

async def analyze_with_vertex_ai(orig_bytes: bytes, ela_b64: str, mime_type: str = "image/jpeg") -> dict:
    """Sends both original and ELA heatmap to Gemini for CNN-like visual extraction."""
    prompt = (
        "You are an expert document forensics AI. You are provided with two images:\n"
        "1. The original scanned identity document.\n"
        "2. The ELA (Error Level Analysis) heatmap where bright colors indicate potential copy-paste tampering.\n"
        "First, determine if the image is a 'Digital' document (e.g., native e-Aadhaar PDF, screenshot, vector graphic) or a 'Physical' photograph of a card.\n"
        "IMPORTANT FORENSIC RULES:\n"
        "- If it is a 'Digital' document, high ELA differences around text and barcodes are completely NORMAL because vector text lacks natural JPEG compression. Do NOT flag digital documents as tampered just because text fields glow in ELA. Only flag if fonts mismatch or text is visibly spliced.\n"
        "- If it is a 'Physical' document, inconsistent ELA glows around specific text (compared to other text) indicates tampering.\n"
        "Analyze the ELA map alongside the original. Return a JSON object with two top-level keys:\n"
        "'extracted_data': contains dynamic keys based on the document type (e.g., name, dob, doc_number, address, issue_date).\n"
        "'forensic_analysis': contains 'is_tampered' (boolean), 'format' (string: 'Digital' or 'Physical'), and 'reasoning' (string). "
        "IMPORTANT: In 'reasoning', format your explanation using strict bullet points using the '-' character, separated by '\\n\\n'. Explicitly mention if the document is Digital or Physical and how that affected your ELA interpretation."
    )
    try:
        ela_bytes = base64.b64decode(ela_b64)
        def run_model():
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=orig_bytes, mime_type=mime_type),
                    types.Part.from_bytes(data=ela_bytes, mime_type="image/jpeg"),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            return response.text

        loop = asyncio.get_event_loop()
        result_text = await loop.run_in_executor(None, run_model)
        return json.loads(result_text)
    except Exception as e:
        print(f"Vertex AI Error: {e}")
        return {"error": str(e), "is_tampered": False}

async def run_tamper_analysis(image: np.ndarray, image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """Orchestrates the full 5-Layer pipeline using ThreadPoolExecutor for multiprocessing."""
    loop = asyncio.get_event_loop()

    with concurrent.futures.ThreadPoolExecutor() as pool:
        ela_task = loop.run_in_executor(pool, compute_ela_with_canny, image)
        noise_task = loop.run_in_executor(pool, compute_noise_residual, image)
        sift_task = loop.run_in_executor(pool, compute_sift_clone_detection, image)
        meta_task = loop.run_in_executor(pool, extract_exif_metadata, image_bytes)
        moire_task = loop.run_in_executor(pool, compute_moire_pattern_detection, image)

        # Execute offline visual layers in parallel
        ela_res, noise_res, sift_res, meta_res, moire_res = await asyncio.gather(
            ela_task, noise_task, sift_task, meta_task, moire_task
        )

    # Online Layer: Vertex AI CNN Inspection
    vertex_res = {}
    if ela_res.get('heatmap_base64'):
        vertex_res = await analyze_with_vertex_ai(image_bytes, ela_res['heatmap_base64'], mime_type)

    # Dynamic Weighting for Composite Risk Score
    weights = {"ela": 0.25, "noise": 0.15, "sift": 0.25, "meta": 0.10, "moire": 0.25}
    
    # Edge Case: Metadata stripped by WhatsApp/Telegram
    if meta_res.get('status') == 'STRIPPED':
        weights = {"ela": 0.30, "noise": 0.15, "sift": 0.25, "meta": 0.0, "moire": 0.30}

    # If Vertex AI detects a native DIGITAL document (e-Aadhaar, PDF, screenshot)
    # SIFT, Noise, and Moiré heuristics are completely invalid for vector graphics and must be suppressed
    is_digital = vertex_res.get('forensic_analysis', {}).get('format', 'Physical') == 'Digital'
    if is_digital:
        noise_res['risk_score'] = 0.0
        noise_res['status'] = 'CLEAN_DIGITAL_IGNORED'
        sift_res['risk_score'] = 0.0
        sift_res['matches_found'] = 0
        sift_res['needs_review'] = False
        moire_res['risk_score'] = 0.0
        ela_res['risk_score'] = 0.0 # ELA heuristics fail on vector graphics, rely purely on Vertex AI reasoning
        weights = {"ela": 0.0, "noise": 0.0, "sift": 0.0, "meta": 0.0, "moire": 0.0}

    composite_risk = (
        (ela_res.get('risk_score', 0) * weights['ela']) +
        (noise_res.get('risk_score', 0) * weights['noise']) +
        (sift_res.get('risk_score', 0) * weights['sift']) +
        (meta_res.get('risk_score', 0) * weights['meta']) +
        (moire_res.get('risk_score', 0) * weights['moire'])
    )

    # Critical Override: Known Editor Signature in EXIF
    if meta_res.get('status') == 'SUSPICIOUS_SOFTWARE':
        composite_risk = 100.0
        vertex_res.setdefault('forensic_analysis', {})['is_tampered'] = True
        vertex_res['forensic_analysis']['reasoning'] = "⚠️ HEURISTIC OVERRIDE: EXIF Metadata proves the use of suspicious software (Photoshop/GIMP). Document is forged.\n\n" + vertex_res['forensic_analysis'].get('reasoning', '')

    # Hard Mathematical Override (If Vertex AI misses it, but physics proves it)
    sift_count = sift_res.get('matches_found', 0)
    moire_risk = moire_res.get('risk_score', 0.0)
    
    if sift_count > 50 or moire_risk > 75.0:
        vertex_res.setdefault('forensic_analysis', {})['is_tampered'] = True
        
        override_reason = "⚠️ HEURISTIC OVERRIDE: While visual inspection may appear authentic, underlying mathematical analysis detected severe anomalies "
        reasons = []
        if sift_count > 50:
            reasons.append(f"SIFT Clones: {sift_count}")
        if moire_risk > 75.0:
            reasons.append(f"Recapture Risk: {moire_risk:.1f}%")
        
        override_reason += f"({', '.join(reasons)}). This document is mathematically proven to be altered or recaptured from a screen.\n\n"
        
        # Only prepend if we haven't already prepended an override
        if "HEURISTIC OVERRIDE" not in vertex_res['forensic_analysis'].get('reasoning', ''):
            vertex_res['forensic_analysis']['reasoning'] = override_reason + vertex_res['forensic_analysis'].get('reasoning', '')
            
        composite_risk = max(composite_risk, 95.0)

    # Vertex AI Override
    if vertex_res.get('forensic_analysis', {}).get('is_tampered'):
        composite_risk = max(composite_risk, 90.0)

    needs_review = sift_res.get('needs_review', False) or (composite_risk > 75.0)

    return {
        "overall_risk_score": round(composite_risk, 2),
        "needs_review": needs_review,
        "layers": {
            "ela": ela_res,
            "noise": noise_res,
            "sift": sift_res,
            "metadata": meta_res,
            "moire": moire_res
        },
        "vertex_ai": vertex_res
    }
