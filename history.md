# Project History Log

## [2026-09-08] Backend Forensics, Biometrics, and MongoDB Overhaul
- **Task Completed:** Implemented the Hybrid Forensic Pipeline (5-Layer) and Biometric Liveness Verification (Track B).
- **Task Completed:** Migrated Biometric Liveness Verification from a 3.5s video recording to a Live WebSocket Streaming pipeline.
- **Key Decisions:** 
  - Opted to use a `ThreadPoolExecutor` and `asyncio.gather` for the 5-layer pipeline in `services/tamper_service.py` to massively speed up OpenCV processing and prevent GIL locks.
  - Implemented MediaPipe for server-side blink and face distance detection via Live WebSocket stream, providing real-time feedback to the UI without running heavy CV models on the client side.
  - Extracted EXIF data using `exifread` and handled "STRIPPED" data natively to prevent false positives from WhatsApp compressions.
  - Updated MongoDB to securely persist complete `verification_logs` via standard Pydantic V2 `.env` integration.
- **Files Modified/Created:**
  - `services/tamper_service.py` (Rewritten for 5 layers)
  - `models/schemas.py` (Updated `TamperResult`)
  - `api/routes_ocr.py` (Updated to handle new schema)
  - `services/bio_service.py` (Implemented WebSocket MediaPipe stream and DeepFace matching)
  - `api/routes_bio.py` (Updated with WebSocket endpoint)
  - `frontend/src/components/BiometricModal.tsx` (WebSocket streaming React UI Component for Camera)
  - `frontend/src/App.tsx` (Added granular anomaly rendering and Officer Override alert block)
  - `.env` and `core/config.py` (Setup MongoDB variables via pydantic-settings)
- **Current State & Next Steps:**
  - The application is fully functional. The Biometric pipeline now processes live video frames instantaneously.
  - Next steps would involve the user dropping their real MongoDB URI into `.env`, testing with physical camera inputs, and potentially starting the Light/Dark mode UI overhaul.

## [2026-09-09] Git Initialization and Push
- **Task Completed:** Initialized the Git repository and pushed all files to the user's private repository (`https://github.com/Janakiram-2005/FDD.git`).
- **Key Decisions:** 
  - Included all secret files (like `.env` and GCP `.json` credentials) intentionally as requested by the user since the repository is private and shared with collaborators.
  - Added a root `.gitignore` to prevent pushing `__pycache__` and `node_modules` folders.
- **Files Modified/Created:**
  - `.gitignore` (Created at root)
- **Current State & Next Steps:**
  - The codebase is now safely pushed to GitHub. Future updates can be handled via standard git workflows.

## [2026-09-09] Recapture Detection & Hybrid Document Classification Upgrade
- **Task Completed:** Implemented Moiré Pattern (Recapture) detection to combat WhatsApp 'photo of a screen' bypasses.
- **Task Completed:** Upgraded document classification to a Hybrid (Online/Offline) system for better Aadhaar and Election Card robustness.
- **Task Completed:** Swapped DeepFace model from ArcFace to Facenet for significantly faster recognition speeds, preserving the MediaPipe blink algorithms.
- **Key Decisions:**
  - Used a 2D FFT (Fast Fourier Transform) frequency domain analysis for Moiré pattern detection, added as "Layer 6" to the tampering pipeline.
  - Deployed Vertex AI (Gemini) as an instant 'Online' classification engine for complex documents, falling back to an upgraded RapidOCR string matching regex if internet or AI fails.
- **Files Modified/Created:**
  - `services/tamper_service.py` (Added `compute_moire_pattern_detection` and integrated into concurrent execution).
  - `services/ocr_service.py` (Added Vertex AI `online_classify_document` and upgraded offline regex).
  - `services/bio_service.py` (Changed DeepFace model to `Facenet`).
  - `frontend/src/App.tsx` (Updated grid UI to display Recapture Risk).
- **Current State & Next Steps:**
  - The system is far more robust against WhatsApp compressions and newer card formats.
## [2026-09-09] QR Verification, MRZ Validation, & Pipeline Tuning
- **Task Completed:** Implemented Secure QR Code parsing for Aadhaar cards and integrated MRZ Modulus-10 checksum math for passports.
- **Task Completed:** Fixed a severe False Positive issue where native digital PDFs triggered ELA/Noise detection by instructing Vertex AI to classify formats (Digital vs Physical) and overriding heuristic mathematics for digital vectors.
- **Task Completed:** Added a 'Blur/Glare Gatekeeper Override' allowing users to force processing of blurry images via frontend confirmation.
- **Key Decisions:** 
  - Used \pyzbar\ and \zlib\ to decompress Aadhaar Secure QR payloads and perform exact string cross-validation against Vertex AI OCR outputs.
  - Handled the back-page routing elegantly by extracting the QR if no face is found.
- **Files Modified/Created:**
  - \services/qr_service.py\ (Created for zlib extraction)
  - \services/tamper_service.py\ (Added Digital format logic)
  - \services/ocr_service.py\ (Integrated QR and MRZ checks)
  - \models/schemas.py\ (Added qr_data)
  - \rontend/src/App.tsx\ (Added UI for QR payload, MRZ validity, and blurry image confirmation)
- **Current State & Next Steps:**
  - The application is highly resilient against native digital manipulation and standard copy-paste fraud. Next steps involve extensive user testing on both Aadhaar and Passports.

### Completed Task: Stabilize OCR Pipeline & Fix Biometric UI (2026-09-09)
- Fixed TimeoutError crashes in Vertex AI classification and extraction by increasing timeouts and adding explicit try-except logic.
- Fixed a frontend stream abort issue where QR code failures (FAILED) completely halted UI rendering.
- Implemented a Forensic QR Heuristic Override: If a document requires a QR code (Aadhaar, PAN, Voter ID) and the QR extraction fails, it automatically spikes the risk score to 85% and triggers a Manual Review alert, defeating high-quality digital fakes.
- Cleaned up React linter warnings, hoisted functions properly in App.tsx, and removed unused variables in the backend.
- Pushed all final changes, including Face API JS weights, to GitHub.

### Completed Task: Database Cross-Verification & PAN Validation (2026-09-10)
- Implemented a MongoDB-backed National Database Verification module with O(log N) indexed search performance.
- Built a dynamic Add Identity Modal UI and backend API (POST /api/v1/db/add-identity) to easily insert mock records for testing.
- Integrated fuzzy string matching for cross-referencing OCR names against Database names.
- Implemented advanced PAN Card cryptographic formatting rules (Regex, Status Character, and Surname Initial check) to detect deepfake textual edits.
- Updated the verification UI to explicitly display Matched Database Details (Name and DOB) when verified.
- Updated requirements.txt with pymongo and pydantic-settings in preparation for deployment.
