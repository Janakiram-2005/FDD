import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import tempfile
import os
import base64
from fastapi import WebSocket
from deepface import DeepFace
from models.schemas import BiometricResult

MODEL_PATH = os.path.join(os.path.dirname(__file__), "face_landmarker.task")

def calculate_ear(eye: list) -> float:
    """Calculates Eye Aspect Ratio to detect blinks."""
    v1 = np.linalg.norm(np.array([eye[1].x, eye[1].y]) - np.array([eye[5].x, eye[5].y]))
    v2 = np.linalg.norm(np.array([eye[2].x, eye[2].y]) - np.array([eye[4].x, eye[4].y]))
    h = np.linalg.norm(np.array([eye[0].x, eye[0].y]) - np.array([eye[3].x, eye[3].y]))
    return (v1 + v2) / (2.0 * h)

def check_blur(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

async def process_live_biometrics(websocket: WebSocket, doc_face_b64: str):
    """
    Receives base64 image frames from websocket, tracks blinks in real-time,
    and performs DeepFace matching once liveness is confirmed.
    """
    blinks = 0
    is_eyes_closed = False
    clearest_frame = None
    max_clarity = 0.0
    
    # Save extracted doc face to temp file immediately
    doc_face_bytes = base64.b64decode(doc_face_b64)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_doc:
        temp_doc.write(doc_face_bytes)
        temp_doc_path = temp_doc.name

    try:
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=2
        )
        
        with vision.FaceLandmarker.create_from_options(options) as landmarker:
            
            # Loop to receive frames until blinks >= 2 or timeout/disconnect
            while blinks < 2:
                data = await websocket.receive_json()
                if "frame" not in data:
                    continue
                    
                frame_b64 = data["frame"].split(",")[-1]
                frame_bytes = base64.b64decode(frame_b64)
                np_arr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    continue
                    
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                results = landmarker.detect(mp_image)
                
                if not results.face_landmarks:
                    await websocket.send_json({"status": "processing", "message": "No face detected. Please look at the camera."})
                    continue
                    
                if len(results.face_landmarks) > 1:
                    await websocket.send_json({"status": "processing", "message": "Multiple faces detected! Ensure only you are in frame."})
                    continue
                    
                landmarks = results.face_landmarks[0]
                h, w, _ = frame.shape
                
                # Face Distance Check
                face_width = max([l.x for l in landmarks]) - min([l.x for l in landmarks])
                if face_width < 0.2:
                    await websocket.send_json({"status": "processing", "message": "Move Closer"})
                    continue
                if face_width > 0.8:
                    await websocket.send_json({"status": "processing", "message": "Move Further Back"})
                    continue

                # Evaluate clarity and save best frame for DeepFace
                clarity = check_blur(frame)
                if clarity > max_clarity:
                    max_clarity = clarity
                    clearest_frame = frame.copy()
                
                # Blink Detection Logic
                left_eye_indices = [33, 160, 158, 133, 153, 144]
                right_eye_indices = [362, 385, 387, 263, 373, 380]
                
                left_eye = [landmarks[i] for i in left_eye_indices]
                right_eye = [landmarks[i] for i in right_eye_indices]
                
                ear_left = calculate_ear(left_eye)
                ear_right = calculate_ear(right_eye)
                avg_ear = (ear_left + ear_right) / 2.0
                
                if avg_ear < 0.22:
                    is_eyes_closed = True
                elif avg_ear > 0.28 and is_eyes_closed:
                    blinks += 1
                    is_eyes_closed = False
                    
                # Format landmarks for JSON transmission (only sending the eyes to save bandwidth)
                eyes_data = [{"x": l.x, "y": l.y} for l in left_eye + right_eye]
                    
                await websocket.send_json({
                    "status": "processing", 
                    "message": f"Blinks detected: {blinks}/2. Please blink.",
                    "blinks": blinks,
                    "eye_landmarks": eyes_data
                })

        # Liveness passed! Notify user that DeepFace is running
        await websocket.send_json({"status": "processing", "message": "Liveness Confirmed! Verifying Identity..."})
        
        if clearest_frame is None or max_clarity < 10.0:
            await websocket.send_json({"status": "completed", "result": {"similarity_score": 0.0, "liveness_status": "FAILED_BLURRY_VIDEO"}})
            await websocket.close()
            return
            
        # DeepFace Matching
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_live:
            cv2.imwrite(temp_live.name, clearest_frame)
            temp_live_path = temp_live.name

        try:
            import asyncio
            result = await asyncio.to_thread(
                DeepFace.verify,
                img1_path=temp_live_path, 
                img2_path=temp_doc_path, 
                model_name="SFace", 
                enforce_detection=False 
            )
            
            similarity = 1.0 - result["distance"]
            similarity = max(0.0, min(1.0, similarity + 0.3))
            
            final_status = "PASSED" if result["verified"] else "FAILED_MATCH"
            final_result = {"similarity_score": similarity * 100, "liveness_status": final_status}
            
            await websocket.send_json({"status": "completed", "result": final_result})
            
        except Exception as e:
            print(f"DeepFace Error: {e}")
            await websocket.send_json({"status": "completed", "result": {"similarity_score": 0.0, "liveness_status": "ERROR_MATCHING"}})
        finally:
            os.remove(temp_live_path)

    finally:
        if os.path.exists(temp_doc_path):
            os.remove(temp_doc_path)
        try:
            await websocket.close()
        except:
            pass
