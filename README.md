# Fraud Detection Document (FDD) Screening System

A robust, multi-layered document verification and biometric liveness system. This system is designed to securely authenticate documents (such as Aadhaar and Passports) and perform real-time liveness checks to prevent tampering, recapture, and deepfake attacks.

## 🚀 Key Features

### 1. Hybrid Forensic Pipeline (5-Layer)
- **Error Level Analysis (ELA) & Noise Detection:** Detects digital manipulation and copy-paste forgery.
- **Moiré Pattern Detection:** Analyzes 2D Fast Fourier Transform (FFT) frequencies to detect "photo of a screen" recapture attacks.
- **Format Classification:** Distinguishes between native digital PDFs and physical scans to prevent false positives.
- **Secure QR Parsing:** Extracts and cryptographically verifies Aadhaar Secure QR payloads using `pyzbar` and `zlib`.
- **MRZ Checksum Validation:** Implements Modulus-10 checksum math for Passport MRZ data cross-verification.

### 2. Biometric Liveness Verification
- **Real-Time WebSockets:** Streams video frames from the frontend to the backend instantly.
- **MediaPipe Blink Detection:** Server-side eye aspect ratio monitoring to verify physical presence.
- **DeepFace matching (Facenet):** High-speed facial recognition comparing the live person to the document photo.

### 3. Hybrid Document Classification & OCR
- **Vertex AI (Gemini) Integration:** Instantly classifies complex documents and extracts textual data.
- **Offline Regex Fallback:** Utilizes RapidOCR for string matching if the AI service is unavailable.
- **Database Cross-Verification:** Fuzzy string matching against a MongoDB-backed National Database to ensure the OCR data matches registered records.

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI, WebSockets
- **AI/ML:** OpenCV, MediaPipe, DeepFace (Facenet), Vertex AI (Gemini)
- **Database:** MongoDB
- **Frontend (Optional):** React, TypeScript, TailwindCSS

## ⚙️ Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Janakiram-2005/FDD.git
   cd FDD
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy the `.env.example` file to `.env` and fill in your credentials.
   ```bash
   cp .env.example .env
   ```
   *Note: You must provide a valid `MONGO_URI` and GCP `GOOGLE_APPLICATION_CREDENTIALS` JSON file.*

5. **Run the server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🔐 Security Note
This repository does not contain production secrets. All sensitive keys, database URIs, and mock APIs have been excluded. To run the application, you must configure your own `.env` and Google Cloud credentials.
