import cv2
import numpy as np
import zxingcpp
import zlib
import base64
import xml.etree.ElementTree as ET

def extract_qr_data(img: np.ndarray) -> dict:
    """
    Reads an image (numpy array), finds a QR code, and extracts the data.
    If it detects an Aadhaar Secure QR Code (compressed byte stream),
    it will attempt to decompress it and extract XML data.
    """
    try:
        if img is None:
            return {"status": "ERROR", "message": "Invalid image provided for QR extraction."}

        # zxing-cpp handles formats automatically, passing the raw image is best
        barcodes = zxingcpp.read_barcodes(img)
        if not barcodes:
            # Try with grayscale and thresholding for tricky scans
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)
            barcodes = zxingcpp.read_barcodes(thresh)
            
            if not barcodes:
                return {"status": "NOT_FOUND", "message": "No QR code detected."}

        # We take the first barcode found
        barcode = barcodes[0]
        raw_data = barcode.bytes
        
        # Check if it's potentially an Aadhaar Secure QR Code
        try:
            # Try to interpret as plain text first
            text_data = raw_data.decode('utf-8')
            return {"status": "SUCCESS", "type": "STANDARD", "data": text_data}
            
        except UnicodeDecodeError:
            # It's likely a binary Aadhaar QR!
            pass

        # Attempt to decode Aadhaar Secure QR
        try:
            # Search for the zlib magic bytes
            zlib_start = -1
            for i in range(len(raw_data) - 1):
                if raw_data[i] == 0x78 and raw_data[i+1] in [0x01, 0x9C, 0xDA, 0x5E]:
                    zlib_start = i
                    break
                    
            if zlib_start != -1:
                try:
                    decompressed = zlib.decompress(raw_data[zlib_start:])
                    xml_str = decompressed.decode('utf-8')
                    
                    root = ET.fromstring(xml_str)
                    aadhaar_data = root.attrib
                    
                    return {"status": "SUCCESS", "type": "AADHAAR_SECURE", "data": aadhaar_data}
                except Exception:
                    pass
        except Exception:
            pass

        return {"status": "SUCCESS", "type": "RAW_BYTES", "data": base64.b64encode(raw_data).decode('utf-8')}

    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
