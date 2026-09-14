from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.bio_service import process_live_biometrics

router = APIRouter()

@router.websocket("/ws/verify")
async def verify_biometrics_websocket(websocket: WebSocket):
    """
    WebSocket Endpoint for Track B: Live Biometric Liveness and Matching.
    Receives base64 frames and sends real-time feedback.
    """
    await websocket.accept()
    try:
        # First message must be the document face base64
        init_data = await websocket.receive_json()
        doc_face_b64 = init_data.get("doc_face_b64")
        
        if not doc_face_b64:
            await websocket.send_json({"status": "FAILED", "message": "Missing doc_face_b64"})
            await websocket.close()
            return
            
        await process_live_biometrics(websocket, doc_face_b64)
        
    except WebSocketDisconnect:
        print("Client disconnected from Biometric Live Stream")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        try:
            await websocket.close()
        except:
            pass
